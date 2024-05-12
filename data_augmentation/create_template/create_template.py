import gzip
import itertools
from typing import Generator, List, Optional, Tuple
import os
from tqdm import tqdm

def template(path_to_data, path_to_output_file):
    fin = gzip.open(path_to_data, 'rt') if path_to_data.endswith('.gz') else open(path_to_data, 'rt')
    with open(path_to_output_file, 'w', encoding="utf-8") as writer:
        for line in fin:
            line = line.strip()
            if not line:
                writer.write("\n")
                continue
            if line.startswith("# id"):
                writer.write(line + '\n')
            else:
                tag = line.split()[-1]
                if tag == 'O':
                    writer.write(line + '\n')
                else:
                    prefix, tag_name = tag.split('-')
                    if prefix == "B":
                        writer.write(f"entity _ _ T-{tag_name}\n")


if __name__ == '__main__':
    template("datasets/vimq/train.conll", "vimq_output.txt")
        
        
        