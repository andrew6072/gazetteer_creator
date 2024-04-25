import sys
from SPARQLWrapper import SPARQLWrapper, JSON
import os
from tqdm import tqdm
import requests

endpoint_url = "https://query.wikidata.org/sparql"

def get_query(limit: int, topic_id: str) -> str:
    # query = f"""
    # SELECT DISTINCT ?item ?itemLabel 
    # WHERE {{
    #     SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{lang}". }}
    #     {{
    #         SELECT DISTINCT ?item WHERE {{
    #             ?item p:P31 ?statement0.
    #             ?statement0 (ps:P31/(wdt:P279*)) wd:{topic_id}.
    #         }}
    #         LIMIT {limit}
    #     }}
    #     FILTER EXISTS {{
    #         ?item rdfs:label ?label .
    #         FILTER(LANG(?label) = '{lang}')
    #         #FILTER(REGEX(?label, "^[{char}{char.lower()}]"))
    #     }}
    # }}
    # """
    query = f"""
    SELECT DISTINCT ?item WHERE {{
        ?item p:P31 ?statement0.
        ?statement0 (ps:P31/(wdt:P279*)) wd:{topic_id}.
    }}
    LIMIT {limit}
    """
    return query


def get_results(endpoint_url, limit, topic_id):
    query = get_query(limit, topic_id)
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def get_item_label(wikidata_id):
    url = f"https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids={wikidata_id}"
    response = requests.get(url)
    data = response.json()
    try:
        label = data['entities'][wikidata_id]['labels']['en']['value']
        return label
    except KeyError:
        return None

LIMIT = 10
LANG = "en"
taxonomy_file = "label_taxonomy/multiconer_en/PER.txt"
filename_with_extension = os.path.basename(taxonomy_file)
tag_name = os.path.splitext(filename_with_extension)[0]
itemLabel_set = set()
taxonomy_ids = []
with open(taxonomy_file, "r", encoding="utf-8") as reader:
    lines = reader.readlines()
    for line in lines:
        tax_id = line.split()[-1]
        taxonomy_ids.append(tax_id)


with open(f"gazetteers/gzt_multiconer_en/{tag_name}.txt", "w", encoding="utf-8") as writer:
    for tax_id in tqdm(taxonomy_ids, desc=f"Creating gzt for {tag_name}"):
        results = get_results(endpoint_url, LIMIT, tax_id)
        for result in results["results"]["bindings"]:
            item_id = result['item']['value'].split('/')[-1]
            itemLabel = get_item_label(item_id)
            if itemLabel != None and itemLabel not in itemLabel_set:
                writer.write(f"{itemLabel}\n")
                itemLabel_set.add(itemLabel)
