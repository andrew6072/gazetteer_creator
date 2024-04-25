from tqdm import tqdm
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

def dataset2NERdict(path_to_train_data: str, results) -> None:
    with open(path_to_train_data, 'r', encoding='utf-8') as fin:
        filename = os.path.basename(path_to_train_data)
        # file_name = os.path.splitext(filename_with_extension)[0]
        total_lines = sum(1 for _ in fin)
        fin.seek(0)
        for line in tqdm(fin, desc=f"Update ner_dict for {filename}", total=total_lines):
            line = line.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '')
            if _is_divider(line):
                continue
            if line.startswith('# id'):
                doc_id = line.split()[-1]
                continue

            tag = line.split()[-1]
            entity = ' '.join(line.split()[:-1])

            if (entity not in results) or (doc_id not in results[entity]['txt_id_list']):
                results.setdefault(entity, {'txt_id_list': [], 'tag_list': []})
                results[entity]['txt_id_list'].append(doc_id)
                if tag not in results[entity]['tag_list']:
                    results[entity]['tag_list'].append(tag)


if __name__ == "__main__":
    fold = 5
    PATH_TO_TRAIN = f"datasets/rdrs/rdrs"
    PATH_TO_DEV = f"datasets/rdrs/rdrs{fold}_valid.txt"
    gzt_directory = f"gazetteers/gzt_rdrs_all"

    ner_dict = {}
    dataset2NERdict(PATH_TO_TRAIN, ner_dict)
    print("len ner_dict:", len(ner_dict))
    # dataset2NERdict(PATH_TO_DEV, ner_dict)
    # print("len ner_dict:", len(ner_dict))
    

    tag_freq = {}
    for entity, mydict in ner_dict.items():
        for tag in mydict["tag_list"]:
            if tag not in tag_freq:
                tag_freq[tag] = 1
            else:
                tag_freq[tag] += 1
    print("Frequency of dataset without duplicates:",tag_freq)

    for filename in os.listdir(gzt_directory):
        if filename.endswith(".txt"):
            count = 0
            count0 = 0

            filepath = os.path.join(gzt_directory, filename)
            print(f"Processing {filepath}")

            tag_name = os.path.basename(filepath)
            tag_name = os.path.splitext(tag_name)[0]
            print(tag_name)

            with open(filepath, "r", encoding="utf-8") as reader:
                total_lines = sum(1 for _ in reader)
                reader.seek(0)
                for line in tqdm(reader, total=total_lines, desc=f"Count covarage for {tag_name}"):
                    line = line.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '')
                    count0 += 1
                    if line in ner_dict and tag_name in ner_dict[line]['tag_list']:
                        count += 1
            print("Total:",count0,"Covers:",count)