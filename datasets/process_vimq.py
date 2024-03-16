from utils import parse_args
import json
import os
from typing import List, Dict


def process_vimq(path_to_file: str) -> None:
    """
    Extracts entities and their corresponding tags from a JSON file and writes them to output files.

    Args:
        path_to_file: A string representing the path to the input file.

    Returns:
        None. Writes the extracted entities and their corresponding tags to the 'vimq' file,
        and the frequency count of each tag to the 'frequency.txt' file.
    """
    output_dir = os.path.join(os.getcwd(), 'datasets/vimq/')
    os.makedirs(output_dir, exist_ok=True)

    freq_labels: Dict[str, int] = {}

    with open(path_to_file, 'r', encoding='utf-8') as reader:
        data = json.load(reader)

        with open(os.path.join(output_dir, "vimq"), 'w', encoding='utf-8') as writer:
            for d in data:
                sentence = d.get("sentence", "").strip().split()
                seq_labels = d.get("seq_label", [])

                for label in seq_labels:
                    start_idx, end_idx, tag = label
                    entity = ' '.join(sentence[start_idx:end_idx+1])
                    writer.write(f"{entity} {tag}\n")
                    freq_labels[tag] = freq_labels.get(tag, 0) + 1

        with open(os.path.join(output_dir, "frequency.txt"), 'w', encoding='utf-8') as writer:
            for tag, count in freq_labels.items():
                writer.write(f"{tag} {count}\n")

if __name__ == "__main__":
    sg = parse_args()
    process_vimq(sg.file)