from utils import parse_args
import json
import os

def process_vimq(path_to_file):
    output_dir = os.path.join(os.getcwd(), 'datasets/vimq/')
    os.makedirs(output_dir, exist_ok=True)
    with open(path_to_file, 'r', encoding='utf-8') as reader:
        freq_labels = {}
        data = json.load(reader)
        with open(output_dir + "vimq", 'w', encoding='utf-8') as writer:
            for d in data:
                sentence = d.get("sentence", "")
                if len(sentence) > 0:
                    sentence = sentence.strip().split()
                    seq_labels = d.get("seq_label", [])
                    for label in seq_labels:
                        start_idx = label[0]
                        end_idx = label[1]
                        tag = label[2]
                        entity = []
                        for i in range(start_idx, end_idx+1):
                            entity.append(sentence[i])
                        writer.write(' '.join(entity) + f" {tag}\n")
                        freq_labels[tag] = freq_labels.get(tag, 0) + 1
        with open(output_dir + "frequency.txt", 'w', encoding='utf-8') as writer:
            for key, value in freq_labels.items():
                writer.write(f"{key} {value} \n")

if __name__ == "__main__":
    sg = parse_args()
    process_vimq(sg.file)