import json
import argparse
from nltk.tokenize import word_tokenize
from utils import parse_args
import os
from typing import Dict, List


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


def process_data(path_to_file: str, name_output_file: str) -> None:
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
    freq_labels: Dict[str, int] = {}
    output_dir = os.path.join(os.getcwd(), 'datasets/rdrs/')
    os.makedirs(output_dir, exist_ok=True)

    with open(path_to_file, 'r', encoding='utf-8') as reader:
        with open(os.path.join(output_dir, name_output_file), 'w', encoding='utf-8') as writer:
            data = json.load(reader)
            for document in data:
                entities = process_1document(document, freq_labels)
                for entity in entities:
                    writer.write(f"{entity}\n")
        with open(os.path.join(output_dir, f"{name_output_file}_frequency.txt"), 'w', encoding='utf-8') as writer:
            for label, freq in freq_labels.items():
                writer.write(f"{label} {freq}\n")


if __name__ == '__main__':
    sg = parse_args()
    process_data(sg.file, "rdrs")


