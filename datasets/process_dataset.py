import gzip
import itertools
from typing import Generator, List, Optional, Tuple
import os


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


def get_ner_reader(path_to_data: str) -> Generator[Tuple[List[List[str]], Optional[str]], None, None]:
    """
    Reads multiconer dataset and yields each sentence as a tuple of fields and metadata.
    """
    fin = gzip.open(path_to_data, 'rt') if path_to_data.endswith('.gz') else open(path_to_data, 'rt')
    for is_divider, lines in itertools.groupby(fin, _is_divider):
        if is_divider:
            continue
        lines = [line.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '') for line in lines]

        metadata = lines[0].strip() if lines[0].strip().startswith('# id') else None
        fields = [[line.split()[0], line.split()[3]] for line in lines if not (line.startswith('# id') or line.endswith('O'))]
        fields = [list(field) for field in zip(*fields)]

        yield fields, metadata

def get_ner_multiconer_dataset(path_to_data: str, path_to_output: str) -> None:
    """
    Reads a multiconer dataset, processes the data, and writes the words to an output file.
    Also keeps track of the frequency of different labels.
    """
    freq_labels = {}
    with open(path_to_output, 'w', encoding='utf-8') as file:
        for fields, metadata in get_ner_reader(path_to_data):
            words = []
            for i, tag in enumerate(fields[1]):
                prefix, suffix = tag.split('-')
                words.append(fields[0][i])
                if (i+1 < len(fields[0]) and fields[1][i+1].startswith('B')) or i == len(fields[0]) - 1:
                    file.write(' '.join(words) + f' {suffix}' + '\n')
                    words = []
                    freq_labels[suffix] = freq_labels.get(suffix, 0) + 1

    with open(os.path.dirname(path_to_output) + '/frequency.txt', 'w', encoding='utf-8') as file:
        for key, value in freq_labels.items():
            file.write(f"{key} {value}\n")

if __name__ == '__main__':
    get_ner_multiconer_dataset('datasets/multiconer/multiconer2022/EN-English/en_train.conll', 'datasets/multiconer/multiconer')
    # get_ner_reader('/home/andrew6072/cmpt688/create_gazetteer/datasets/sample.conll')
        
        
        