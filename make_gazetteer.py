from search_wiki_data import *
from datasets.process_multiconer import _is_divider
import spacy
import os
from typing import List, Dict
from spacy.tokens import Doc
import time
from utils import parse_args
from tqdm import tqdm
import json
import re
import logging

logging.basicConfig(filename='dataset_processing_errors.log', level=logging.ERROR, format='%(asctime)s:%(levelname)s:%(message)s')


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
                        if max_similarity == 1:
                            break

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


def dataset2NERdict(path_to_train_data: str, limit: int, lang: str) -> None:
    """
    Process a training dataset and return a dictionary containing the results.
    results = {
        'NER':{
            'text_id_list':[id1, id2, id3, ...],
            'wiki_topics': {topic : wikidata_code}
        }
    }
    It creates 2 json files: `{dataset_name}_ners_dict.json` and `{dataset_name}_docs_dict.json`
    in directory `datasets/{dataset_name}/`

    Args:
        path_to_train_data (str): The path to the training dataset file.
        limit (int): The limit value for the number of topics to retrieve.
        lang (str): The language for the search.

    Returns:
        results (Dict[str, Dict]): A dictionary containing the results of the dataset processing.
            The keys are entities, and the values are dictionaries containing the 'txt_id_list',
            'wiki_topics', and 'tag' for each entity.
    """
    try:
        with open(path_to_train_data, 'r', encoding='utf-8') as fin:
            results = {}
            docs_dict = {}
            sleep_time = 300
            if not os.path.isfile(path_to_train_data):
                raise FileNotFoundError(f"The specified training data file was not found: {path_to_train_data}")
            name_dataset = os.path.basename(path_to_train_data)

            output_dir = f"datasets/{name_dataset}/"
            os.makedirs(output_dir, exist_ok=True)
            results_file_path = os.path.join(output_dir, f"{name_dataset}_ners_dict.json")
            docs_dict_file_path = os.path.join(output_dir, f"{name_dataset}_docs_dict.json")

            #lines = [line.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '') for line in fin if not _is_divider(line)]
            
            entity_counter = 0
            total_lines = sum(1 for _ in fin)
            fin.seek(0)
            for line in tqdm(fin, desc=f"Creating NER dict for dataset {name_dataset}", total=total_lines):
                line = line.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '')
                if _is_divider(line):
                    continue
                if line.startswith('# id'):
                    doc_id = line.split()[-1]
                    continue
                entity_counter += 1

                tag = line.split()[-1]
                entity = ' '.join(line.split()[:-1])

                docs_dict.setdefault(doc_id, [])
                docs_dict[doc_id].append(entity)

                if (entity not in results) or (doc_id not in results[entity]['txt_id_list']):
                    wiki_topics = get_topics_from_wkdt_search_tool(url, api_url, entity, lang, limit)
                    results.setdefault(entity, {'txt_id_list': [], 'wiki_topics': wiki_topics, 'tag': tag})
                    results[entity]['txt_id_list'].append(doc_id)
                    if entity_counter % 1000 == 0:
                        print(f"Sleep for {sleep_time}!\n")
                        time.sleep(sleep_time)
                # write results to file every 100 entities to advoid data loss in case the program crashed
                if entity_counter % 100 == 0:
                    _write_results_to_file(results_file_path, docs_dict_file_path, results, docs_dict)
            if entity_counter % 100 != 0:  # This check ensures we only write if there's data that hasn't been written yet
                _write_results_to_file(results_file_path, docs_dict_file_path, results, docs_dict)
    except FileNotFoundError as e:
        logging.exception("File not found: %s", e)
    except Exception as e:
        logging.exception("Unexpected error: %s", e)


def _write_results_to_file(results_file_path: str, docs_dict_file_path: str, results: Dict, docs_dict: Dict) -> None:
    """
    Write the results and docs_dict dictionaries to the corresponding JSON files.

    Args:
        results_file_path (str): The file path for the results JSON file.
        docs_dict_file_path (str): The file path for the docs_dict JSON file.
        results (Dict): The results dictionary.
        docs_dict (Dict): The docs_dict dictionary.

    Returns:
        None
    """
    with open(results_file_path, 'w', encoding='utf-8') as f, open(docs_dict_file_path, 'w', encoding='utf-8') as f_docs:
        json.dump(results, f, ensure_ascii=False, indent=4)
        json.dump(docs_dict, f_docs, ensure_ascii=False, indent=4)


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
    name_dataset_without_digit = re.sub(r'\d+', '', name_dataset)

    with open(os.path.join(f"datasets/{name_dataset_without_digit}", f"{name_dataset_without_digit}_ners_dict.json"), 'r', encoding='utf-8') as ners_file:
        ners_dict = json.load(ners_file)
    
    with open(os.path.join(f"datasets/{name_dataset_without_digit}", f"{name_dataset_without_digit}_docs_dict.json"), 'r', encoding='utf-8') as docs_file:
        docs_dict = json.load(docs_file)


    # List all directories inside the 'label_synonyms/' directory
    label_synonyms_directories = {name for name in os.listdir('label_synonyms/') if os.path.isdir(os.path.join('label_synonyms/', name))}
    if name_dataset_without_digit not in label_synonyms_directories:
        raise ValueError("The filename of `path_to_train_data` must match one of the names of directories inside the `label_synonyms/` directory.")

    print("Processing:", name_dataset)
    gzt_path = f"gazetteers/gzt_{name_dataset}_thr_{threshold:.2f}_lim_{limit}".replace('.', '_')
    
    label_doc_dict = get_label_synonyms2vecs(model, f"label_synonyms/{name_dataset_without_digit}")
    os.makedirs(gzt_path, exist_ok=True)

    freq_entity_true_label = {}
    processed_entites = {}

    # START
    with open(path_to_train_data, 'r', encoding='utf-8') as fin:
        total_lines = sum(1 for _ in fin)
        fin.seek(0)
        for line in tqdm(fin, desc="Mapping entities to gazetteer", total=total_lines):
            if _is_divider(line) or not line.startswith("# id"):
                continue
            doc_id = line.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '').split()[-1]
            entities = docs_dict.get(doc_id, [])
            uniq_ents = set(entities)
            for entity in uniq_ents:
                if entity in processed_entites:
                    continue
                processed_entites[entity] = True
                true_tag = ners_dict.get(entity, {}).get('tag', '')
                if len(true_tag) == 0:
                    continue
                topics = ners_dict.get(entity, {}).get('wiki_topics', {})
                if add_entity_to_gazetteer(model, entity, true_tag, topics, label_doc_dict, threshold, gzt_path):
                    freq_entity_true_label[true_tag] = freq_entity_true_label.get(true_tag, 0) + 1

    with open(gzt_path + "/coverage.txt", 'w', encoding='utf-8') as file:
        for key, value in freq_entity_true_label.items():
            file.write(f"{key} {value}\n")



if __name__ == "__main__":
    model = spacy.load("en_core_web_lg")
    sg = parse_args()
    # dataset2NERdict() requires internent connection
    dataset2NERdict(path_to_train_data=sg.data, limit=sg.limit, lang=sg.lang)

    if os.path.basename(sg.data) != 'rdrs':
        # make_gazetteer() does not require internent connection
        make_gazetteer(model=model, path_to_train_data=sg.data, threshold=sg.threshold, limit=sg.limit, lang=sg.lang)
    else:
        for i in range(1, 6):
            make_gazetteer(model=model, path_to_train_data=f"{sg.data}{i}", threshold=sg.threshold, limit=sg.limit, lang=sg.lang)




