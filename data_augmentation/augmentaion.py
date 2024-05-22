import gzip
import itertools
from typing import Generator, List, Optional, Tuple, Dict
import os
import random
import uuid

def _is_divider(line: str) -> bool:
    """
    Determines whether a given line is a divider or not
    """
    line = line.strip()
    if not line:
        return True

    first_token = line.split()[0]
    if first_token == "-DOCSTART-":
        return True

    return False


def get_template_list(path_to_data: str) -> Generator[Tuple[List[List[str]], Optional[str]], None, None]:
    """
    Reads a dataset file and returns a generator that yields each sentence as a tuple of fields and metadata.
    """
    templates = []
    with gzip.open(path_to_data, 'rt') if path_to_data.endswith('.gz') else open(path_to_data, 'rt') as fin:
        for is_divider, lines in itertools.groupby(fin, _is_divider):
            if is_divider:
                continue
            lines = [line.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '') for line in lines]
            metadata = lines[0].strip() if lines[0].strip().startswith('# id') else None
            metadata = metadata.split()
            metadata[2] = str(uuid.uuid4())
            fields = [' '.join(metadata)]
            fields.extend([line for line in lines if not line.startswith('# id')])

            templates.append(fields)
    return templates

def _is_divider(line: str) -> bool:
    """
    Checks if a line is a divider.
    """
    return line.strip() == ''


def replacement_1_template(gazetteer_dict: dict, template: list) -> list:
    """
    Replaces entity tags in the template with randomly selected entities from the corresponding gazetteer.
    
    Args:
    - gazetteer_dict (dict): A dictionary containing gazetteers where the keys are entity tags and the values are lists of entities.
    - template (list): A list of strings representing a template with entity tags.
    
    Returns:
    - res (list): The modified template with entity tags replaced by randomly selected entities from the gazetteer.
    """
    
    if not template:
        return None
    
    res = [template[0]]
    
    for element in template[1:]:
        if element.split()[-1].startswith("T-"):
            tag_name = element.split("-")[-1]
            new_entity = random.choice(gazetteer_dict.get(tag_name, []))
            words = new_entity.split()
            res.append(f'{words[0]} _ _ B-{tag_name}')
            res.extend([f'{word} _ _ I-{tag_name}' for word in words[1:]])
        else:
            res.append(element)
    
    return res


def read_files_to_dict(directory: str) -> Dict[str, List[str]]:
    files_dict = {}
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            name_without_extension = os.path.splitext(filename)[0]
            with open(os.path.join(directory, filename), 'r', encoding="utf-8") as file:
                files_dict[name_without_extension] = [line.strip() for line in file.readlines()]
    return files_dict


def entity_replacement_randomtemplate(path_to_gazetteer, path_to_template_file, output_file, number_of_templates):
    gazetteer_dict = read_files_to_dict(path_to_gazetteer)
    templates = get_template_list(path_to_template_file)
    with open(output_file, "w", encoding="utf-8") as writer:
        for _ in range(number_of_templates):
            res = replacement_1_template(gazetteer_dict, random.choice(templates))
            for field in res:
                writer.write(field + '\n')
            writer.write('\n')


def entity_replacement_alltemplate(path_to_gazetteer, path_to_template_file, output_file):
    gazetteer_dict = read_files_to_dict(path_to_gazetteer)
    templates = get_template_list(path_to_template_file)
    with open(output_file, "w", encoding="utf-8") as writer:
        for template in templates:
            res = replacement_1_template(gazetteer_dict, template)
            for field in res:
                writer.write(field + '\n')
            writer.write('\n')


if __name__ == "__main__":
    template_file = "data_augmentation/create_template/output/vimq_template.txt"
    gazetteer_directory = "gazetteers/gzt_vimq"
    output_file = "./test1.txt"
    entity_replacement_alltemplate(gazetteer_directory, template_file, output_file)