import json
import argparse
from nltk.tokenize import word_tokenize
from utils import parse_args
import os

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

def process_1document(document, freq_label):
    list_of_entities = []
    entities_dict = document['entities']
    text = document['text']
    words = word_tokenize(text)
    for _, entity_dict in entities_dict.items():
        label = entity_dict.get('MedEntityType', "")
        if len(label) <= 0:
            continue
        entity = []
        for span in entity_dict.get("spans", []):
            begin_pos, end_pos = get_pos_span(text, span['begin'], span['end'])
            entity.extend(words[begin_pos : end_pos + 1])
        list_of_entities.append(' '.join(entity) + f" {label}")
        freq_label[label] = freq_label.get(label, 0) + 1
    return list_of_entities


def process_data(path_to_file, name_output_file):
    freq_labels = {}
    output_dir = os.path.join(os.getcwd(), 'datasets/rdrs/')
    os.makedirs(output_dir, exist_ok=True)

    with open(path_to_file, 'r', encoding='utf-8') as reader:
        with open(output_dir+name_output_file, 'w', encoding='utf-8') as writer:
            data = json.load(reader)
            for document in data:
                entities = process_1document(document, freq_labels)
                for entity in entities:
                    writer.write(f"{entity}\n")
        with open(f"{output_dir}{name_output_file}_frequency.txt", 'w', encoding='utf-8') as writer:
            for label, freq in freq_labels.items():
                writer.write(f"{label} {freq}\n")


if __name__ == '__main__':
    sg = parse_args()
    process_data(sg.file, "rdrs")


