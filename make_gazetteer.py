from search_wiki_data import *
import spacy
import os
from typing import List, Dict
from spacy.tokens import Doc
import time
from utils import parse_args

def get_label_synonyms2vecs(model: spacy.Language, directory_path: str) -> Dict[str, List[Doc]]:
    """
    Reads text files in the given directory, removes the file extension, and stores the file content in a dictionary.
    Each line in the file is stripped of newline characters and passed through the spaCy model to calculate the token vectors.
    The token vectors are then stored in a list and associated with the file key in the dictionary.
    Returns the dictionary containing the file keys and their corresponding token vectors.

    Args:
        model (spacy.Language): A pre-trained spaCy model.
        directory_path (str): The path to the directory containing the text files.

    Returns:
        dict: A dictionary where the keys are the filenames without the ".txt" extension and the values are lists of token vectors calculated using the spaCy model.
    """
    files_dict = {}
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            file_key = filename[:-4]
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file.readlines()]
                syn2vec_list = [model(line) for line in lines]
                files_dict[file_key] = syn2vec_list
    return files_dict


def append_word_to_txtfile(word: str, path_to_file: str) -> None:
    """
    Appends a word to a text file. If the file does not exist, it creates the file.

    Args:
        word (str): The word to append to the file.
        path_to_file (str): The path to the text file.
    """
    with open(path_to_file, 'a', encoding='utf-8') as file:
        file.write(word + '\n')


def add_entity_to_gazetteer(model: spacy.Language, entity: str, true_tag: str, topics: Dict[str, str], label_doc_dict: Dict[str, List[Doc]], threshold: float, directory_path: str) -> bool:
    """
    Compares each topic of the entity to each doc from the list of label, take the maximum similarity,
    if the maximum similarity is greater than the threshold, add the entity to the corresponding gazetteer
    """
    # dictionary checks if the entity is added to which label, to avoid adding the same entity to 1 gazetteer
    added_labels = {label: False for label in label_doc_dict.keys()}
    # print(f"Entity \"{entity}\" is instance of topics: {topics}")
    # print()

    # to check if this entity is added to true tag gazetteer, true tag is taken from official data (training data)
    entity_added_to_true_tag_gazetteer = False

    

    for label, doc_list in label_doc_dict.items():
        for topic, topic_description in topics.items():
            # if the entity is already added to this label because similarity of topic to 1 of the doc
            # is greater than thershold, then dont bother considering other topics.
            if added_labels[label]:
                break

            max_similarity = float("-inf")
            most_related_doc = None
            
            # convert the topic to spacy doc
            topic_doc = model(topic)
            if topic_doc.has_vector and len(topic_doc) > 0:
                for doc in doc_list:
                    if doc.has_vector and len(doc) > 0:
                        similarity = topic_doc.similarity(doc)
                        if similarity > max_similarity:
                            max_similarity = similarity
                            most_related_doc = doc

            # add this entity to gazetteer <label>.txt
            if not added_labels[label] and max_similarity >= threshold:
                # Construct the path to the gazetteer file
                path_to_file = os.path.join(directory_path, f"{label}.txt")
                append_word_to_txtfile(entity, path_to_file)
                added_labels[label] = True
                if label == true_tag:
                    entity_added_to_true_tag_gazetteer = True
                # print(f"Added \'{entity}\' in term of \'{topic}\' to {label} because it's sim to topic \'{most_related_doc}\' with val {max_similarity:.2f}")
                # print()
    return entity_added_to_true_tag_gazetteer


def make_gazetteer(model: spacy.language.Language, path_to_train_data: str, threshold: float, limit: int, lang: str) -> None:
    """
    Creates a gazetteer by extracting topics from a given dataset and adding entities to corresponding gazetteer files.

    Args:
        model (spacy.language.Language): A pre-trained spaCy model.
        path_to_train_data (str): The path to the dataset file. !!!Caution: name of dataset file need to be the same with the label_synonyms file
        threshold (float): The similarity threshold for adding entities to the gazetteer.
        limit (int): The maximum number of topics to extract for each entity.
        lang (str): The language of the dataset.

    Returns:
        None. The function creates gazetteer files in the specified directory.
    """
    # Extract the name of the dataset from the path
    name_dataset = os.path.basename(path_to_train_data)

    # Extract the name of the dataset from the path
    dataset_name = os.path.basename(path_to_train_data)

    # List all directories inside the 'label_synonyms/' directory
    label_synonyms_directories = [name for name in os.listdir('label_synonyms/') if os.path.isdir(os.path.join('label_synonyms/', name))]

    # Check if the dataset name matches any of the directories inside 'label_synonyms/'
    if dataset_name not in label_synonyms_directories:
        raise ValueError("The filename of `path_to_train_data` must match one of the names of directories inside the `label_synonyms/` directory.")

    print(name_dataset)
    directory_path = f"gazetteers/gzt_{name_dataset}_thr_{str(threshold).replace('.', '_')}_lim_{limit}"
    
    label_doc_dict = get_label_synonyms2vecs(model, f"label_synonyms/{name_dataset}")

    os.makedirs(directory_path, exist_ok=True)
    with open(path_to_train_data, 'r', encoding='utf-8') as file:
        freq_entity_true_label = {}
        lines = file.readlines()
        num_lines = len(lines)
        xth_word = 1
        entites = [' '.join(line.strip().split()[:-1]) for line in lines]
        tags = [line.strip().split()[-1] for line in lines]

        average_time_on_1_entity = 0
        for i, entity in enumerate(entites):
            start_time = time.time()

            # first search for related topics of the entity
            # then add the entity to a gazetteer if the similarity of 1 of its topics to that gazetteer
            # is greater then threshold 
            true_label = tags[i]
            topics = get_topics_from_wkdt_search_tool(url, api_url, entity, lang, limit)
            if (add_entity_to_gazetteer(model, entity, true_label, topics, label_doc_dict, threshold, directory_path)):
                freq_entity_true_label[true_label] = freq_entity_true_label.get(true_label, 0) + 1
            
            end_time = time.time()
            average_time_on_1_entity += end_time-start_time
            print(f"Done {xth_word}/{num_lines} in {end_time-start_time:.2f}s")
            xth_word += 1
        print('Average time for adding 1 entity to gzetteer:', average_time_on_1_entity/num_lines)

        with open(directory_path + "/coverage.txt", 'w', encoding='utf-8') as file:
            for key, value in freq_entity_true_label.items():
                file.write(f"{key} {value}\n")

        


if __name__ == "__main__":
    model = spacy.load("en_core_web_lg")
    sg = parse_args()
    make_gazetteer(model=model, path_to_train_data=sg.data, threshold=sg.threshold, limit=sg.limit, lang=sg.lang)




