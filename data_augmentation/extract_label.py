target = "Disease"
path_to_data = "datasets/rdrs/rdrs_all.txt"
path_to_output = f"datasets/rdrs/{target}.txt"
entity_set = set()
with open(path_to_data, "r", encoding="utf-8") as reader, open(path_to_output, "w", encoding="utf-8") as writer:
    for line in reader:
        line = line.strip()
        if line and not line.startswith("# id"):
            tag = line.split()[-1]
            entity = ' '.join(line.split()[:-1])
            if entity not in entity_set and (tag == target or tag == "ADR"):
                writer.write(entity + '\n')
                entity_set.add(entity)