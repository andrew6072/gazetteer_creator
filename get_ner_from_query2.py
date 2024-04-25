import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from tqdm import tqdm
import requests

endpoint_url = "https://query.wikidata.org/sparql"

def get_query(limit: int, topic_id: str, lang:str) -> str:
    query = f"""
    SELECT DISTINCT ?item ?itemLabel 
    WHERE {{
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{lang}". }}
        {{
            SELECT DISTINCT ?item WHERE {{
                ?item p:P31 ?statement0.
                ?statement0 (ps:P31/(wdt:P279*)) wd:{topic_id}.
            }}
            LIMIT {limit}
        }}
        FILTER EXISTS {{
            ?item rdfs:label ?label .
            FILTER(LANG(?label) = '{lang}')
        }}
    }}
    """
    return query


def get_results(endpoint_url, limit, topic_id, lang):
    query = get_query(limit, topic_id, lang)
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def make_gazetteer(taxonomy_file, LIMIT, LANG, gzt_name):
    # taxonomy_file = "label_taxonomy/multiconer_en/PER.txt"
    filename_with_extension = os.path.basename(taxonomy_file)
    tag_name = os.path.splitext(filename_with_extension)[0]
    itemLabel_set = {}
    taxonomy_ids = []
    with open(taxonomy_file, "r", encoding="utf-8") as reader:
        lines = reader.readlines()
        for line in lines:
            tax_id = line.split()[-1]
            taxonomy_ids.append(tax_id)

    os.makedirs(f"gazetteers/{gzt_name}/", exist_ok=True)
    with open(f"gazetteers/{gzt_name}/{tag_name}.txt", "w", encoding="utf-8") as writer:
        for tax_id in tqdm(taxonomy_ids, desc=f"Creating gzt for {tag_name}"):
            current_limit = LIMIT
            while current_limit > 0:
                try:
                    results = get_results(endpoint_url, current_limit, tax_id, LANG)
                    break  # If successful, break out of the while loop
                except Exception as e:
                    print(f"Error fetching results with limit {current_limit}: {e}")
                    if current_limit <= 500000:
                        current_limit -= 10000  # Decrease limit by 10,000 and retry
                    else:
                        current_limit /= 2
                    if current_limit <= 0:
                        print(f"Failed to fetch results for tax_id {tax_id} after several attempts.")
                        continue  # Skip to the next tax_id if limit becomes zero or negative

            for result in results["results"]["bindings"]:
                itemLabel = result['itemLabel']['value'].lower()
                if itemLabel not in itemLabel_set:
                    writer.write(f"{itemLabel}\n")
                    itemLabel_set[itemLabel] = None

if __name__ == "__main__":
    taxonomy_directory = 'label_taxonomy/rdrs/'  # Specify the directory path
    gzt_name = "gzt_rdrs_all"
    LIMIT = 1000000
    LANG = "ru"

    for filename in os.listdir(taxonomy_directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(taxonomy_directory, filename)
            print(f"Processing {filepath}")
            make_gazetteer(filepath, LIMIT, LANG, gzt_name)
    