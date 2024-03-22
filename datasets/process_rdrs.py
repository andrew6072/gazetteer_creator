import json
import argparse
from nltk.tokenize import word_tokenize
from utils import parse_args
import os
from typing import Dict, List
from tqdm import tqdm


def get_pos_span(text: str, begin: int, end: int) -> tuple:
    """
    Extracts a substring from `text` using the `begin` and `end` indices,
    and calculates the positions of the beginning and ending words of the substring in the tokenized `text`.

    Args:
        text (str): The input text from which the substring will be extracted.
        begin (int): The index of the beginning of the substring in the `text`.
        end (int): The index of the end of the substring in the `text`.

    Returns:
        tuple: A tuple containing the position of the beginning word and the position of the ending word of the substring in the tokenized `text`.
    """
    cut1 = text[:begin]
    span = text[begin:end]
    begin_pos = len(word_tokenize(cut1))
    end_pos = begin_pos + len(word_tokenize(span)) - 1
    return begin_pos, end_pos

def process_1document(document: dict, freq_label: dict) -> list:
    """
    Extracts entities from a document and updates the frequency label dictionary.
    
    Args:
        document (dict): A dictionary representing a document.
        freq_label (dict): A dictionary to store the frequency of each label.
        
    Returns:
        list: A list of extracted entities, where each entity is a string consisting of the words and the label.
    """
    list_of_entities = []
    entities_dict = document.get('entities', {})
    text = document.get('text', '')
    words = word_tokenize(text)
    text_id = document.get('text_id')
    list_of_entities.append(f"# id {text_id}")
    
    for entity_dict in entities_dict.values():
        label = entity_dict.get('MedEntityType', '')
        if not label:
            continue
        
        entity = []
        for span in entity_dict.get('spans', []):
            begin_pos, end_pos = get_pos_span(text, span['begin'], span['end'])
            entity.extend(words[begin_pos: end_pos + 1])
        
        entity_with_label = ' '.join(entity) + f" {label}"
        list_of_entities.append(entity_with_label)
        freq_label[label] = freq_label.get(label, 0) + 1
    
    return list_of_entities


def process_data(path_to_file: str, name_output_file: str, freq_labels: Dict[str, int]) -> None:
    """
    Reads a JSON file, processes each document in the file using the `process_1document` function,
    and writes the extracted entities to an output file. It also calculates the frequency of each label
    and writes it to a separate frequency file.

    Args:
        path_to_file: The path to the input JSON file.
        name_output_file: The name of the output file.

    Returns:
        None
    """
    output_dir = os.path.join(os.getcwd(), 'datasets/rdrs/')
    os.makedirs(output_dir, exist_ok=True)

    with open(path_to_file, 'r', encoding='utf-8') as reader:
        with open(os.path.join(output_dir, name_output_file), 'a', encoding='utf-8') as writer:
            data = json.load(reader)
            for document in tqdm(data, desc=f"Processing {name_output_file}"):
                entities = process_1document(document, freq_labels)
                for entity in entities:
                    writer.write(f"{entity}\n")
                writer.write("\n")


def merge_and_convert_rdrs(path_to_rdrs_dir: str, name_output_file: str):
    freq_labels: Dict[str, int] = {}
    output_dir = os.path.join(os.getcwd(), 'datasets/rdrs/')
    os.makedirs(output_dir, exist_ok=True)
    path_to_rdrs_dir = os.path.join(path_to_rdrs_dir, "1")
    if not os.path.isdir(path_to_rdrs_dir):
        raise ValueError(f"Error: {path_to_rdrs_dir} is not a directory.")

    # List all files in the directory
    for file_name in os.listdir(path_to_rdrs_dir):
        print(file_name)
        file_path = os.path.join(path_to_rdrs_dir, file_name)
        
        # Check if it's a file before processing
        if os.path.isfile(file_path):
            process_data(file_path, name_output_file, freq_labels)
    
    with open(os.path.join(output_dir, f"{name_output_file}_frequency.txt"), 'w', encoding='utf-8') as writer:
        for label, freq in freq_labels.items():
            writer.write(f"{label} {freq}\n")


def process_all_fold(path_to_folds_dir):
    output_base_dir = os.path.join(os.getcwd(), 'datasets/rdrs/')
    for num, dir_name in enumerate(os.listdir(path_to_folds_dir), start=1):
        dir_path = os.path.join(path_to_folds_dir, dir_name)
        if os.path.isdir(dir_path):
            train_file_path = os.path.join(dir_path, 'train.json')
            freq_labels = {}
            if os.path.exists(train_file_path):
                process_data(train_file_path, f'rdrs{dir_name}', freq_labels)
            with open(os.path.join(output_base_dir, f"rdrs{dir_name}_frequency.txt"), 'w', encoding='utf-8') as writer:
                for label, freq in freq_labels.items():
                    writer.write(f"{label} {freq}\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process RDRS training data.', add_help=False)
    parser.add_argument('--dir', type=str, help='Path to 1 of 5 dir of RDRS')
    # dir has form `RDRS-main/data/interim`
    sg = parser.parse_args()
    merge_and_convert_rdrs(sg.dir, "rdrs")
    process_all_fold(sg.dir)


