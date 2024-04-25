from tqdm import tqdm
from search_wiki_data import *
from make_gazetteer import *
from datasets.process_multiconer import _is_divider


def write_to_file(file_path, mydict):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(mydict, f, ensure_ascii=False, indent=4)

def get_distinc_entity_dict(path_to_rdrs_processed_corpus):
    distinc_entity_dict = {}
    with open(path_to_rdrs_processed_corpus, "r", encoding="utf-8") as fin:
        total_lines = sum(1 for _ in fin)
        fin.seek(0)
        for line in tqdm(fin, total=total_lines):
            line = line.strip().replace('\u200d', '').replace('\u200c', '').replace('\u200b', '')
            if _is_divider(line):
                continue
            if line.startswith('# id'):
                continue
            tag = line.split()[-1]
            if tag == "Note":
                continue
            entity = ' '.join(line.split()[:-1])
            if entity not in distinc_entity_dict:
                distinc_entity_dict[entity] = {tag: 1}
            elif tag not in distinc_entity_dict[entity]:
                distinc_entity_dict[entity][tag] = 1
            else:
                distinc_entity_dict[entity][tag] += 1
    return distinc_entity_dict
    

def dump_entity_topics_dict_to_file(path_to_rdrs_processed_corpus, lang, limit, out_put_file_path):
    entity_topics_dict = {}
    distinc_entity_dict = get_distinc_entity_dict(path_to_rdrs_processed_corpus)
    entity_counter = 1
    for entity in tqdm(distinc_entity_dict, total=len(distinc_entity_dict), desc="Search and dump"):
        sleep_time = 300
        wiki_topics = get_topics_from_wkdt_search_tool(url, api_url, entity, lang, limit)
        entity_topics_dict[entity] = wiki_topics

        if entity_counter % 1000 == 0:
            print(f"Sleep for {sleep_time}!\n")
            time.sleep(sleep_time)
        # write results to file every 100 entities to advoid data loss in case the program crashed
        if entity_counter % 100 == 0:
            write_to_file(out_put_file_path, entity_topics_dict)
        entity_counter += 1
    if entity_counter % 100 != 0:  # This check ensures we only write if there's data that hasn't been written yet
        write_to_file(out_put_file_path, entity_topics_dict)    
    # print(topic_freq)


if __name__=="__main__":
    lang = "en"
    limit = 5
    path_to_rdrs_processed_corpus = "xxxtest/test1111.txt"
    out_put_file_path = "rdrs_entity_topics_dict.json"
    dump_entity_topics_dict_to_file(path_to_rdrs_processed_corpus, "en", 5, out_put_file_path)