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


def convert_data(path_to_data, path_to_output, domain):

    with open(path_to_data, 'r', encoding='utf-8') as f:
        data = json.load(f)

    documents = data
    list_fields = []
    for document in documents:
        # print(document['text_id'])

        entities = document['entities']

        text = document['text']

        words = word_tokenize(text)
        
        labels = ['O'] * len(words)
        
        

        # print(text)
        # print()
        # print(words)
        # print("Words len:",len(words))
        # print("Labels len:",len(labels))
        # print()

        for no_entity, entity in entities.items():
            label = entity['MedEntityType']
            is_first_word_in_span = True
            for span in entity['spans']:
                begin_pos, end_pos = get_pos_span(
                    text, span['begin'], span['end'])
                # print(no_entity, text[span['begin']:span['end']],
                #       begin_pos, end_pos, label)
                for i in range(begin_pos, end_pos+1):
                    labels[i] = 'I-' + label
                if is_first_word_in_span:
                    labels[begin_pos] = 'B-' + label
                    is_first_word_in_span = False

        fields = list([words, ['_']*len(words), ['_']*len(words), labels])
        fields = [f'# id {document["text_id"]}\tdomain={domain}'] + [list(field) for field in zip(*fields)]
        list_fields.append(fields)

        # print()

    with open(path_to_output, 'w', encoding='utf-8') as f:
        data_str = []
        for _, fields in enumerate(list_fields):
            str_fields = []
            str_fields.append(fields[0])
            for i in range(1, len(fields)):
                str_fields.append(' '.join(fields[i]))
            str_fields = '\n'.join(str_fields)
            data_str.append(str_fields)
        data_str = '\n\n'.join(data_str)
        f.write(data_str)


if __name__ == '__main__':
    sg = parse_args()
    # with open('/home/andrew6072/Downloads/dataset/RDRS-main/data/interim/4/valid.json', 'r', encoding='utf-8') as f:
    #     data = json.load(f)
    #     sample_dict = None
    #     for item in data:
    #         if item.get('text_id') == '1426094':
    #             sample_dict = item
    #             break
    #     if sample_dict != None:
    #         print(sample_dict.get("text"))
    #         print(process_1document(sample_dict, {}))
    process_data(sg.file, "rdrs")


