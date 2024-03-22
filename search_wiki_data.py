import requests
from bs4 import BeautifulSoup
import logging
from typing import Generator, Tuple, Dict

url = "https://www.wikidata.org/w/index.php"
api_url = "https://www.wikidata.org/w/api.php"


def get_instances_by_property_P31(api_url: str, page_id: str, lang: str) -> Generator[Tuple[str, str], None, None]:
    """
    Retrieves instances that are possibly related to a given instance based on the P31 ("instance of") property in Wikidata.
    Yields each topic and its corresponding entity ID.

    Args:
        api_url (str): The URL of the Wikidata API.
        page_id (str): The ID of the page for which instances are being retrieved.
        lang (str): The language code for the labels of the retrieved instances.

    Yields:
        Tuple[str, str]: A tuple containing the topic name and its corresponding entity ID.
    """
    page_params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": page_id
    }
    page_response = requests.get(api_url, params=page_params)
    claims = page_response.json().get("entities", {}).get(page_id, {}).get("claims", {})
    list_of_topics = []
    
    if "P279" in claims:
        list_of_topics = claims["P279"]
    
    if "P31" in claims:
        list_of_topics.extend(claims["P31"])
        
    for topic in list_of_topics:
        entity_id = topic.get("mainsnak", {}).get("datavalue", {}).get("value", {}).get("id")
        
        if entity_id:
            params = {
                "action": "wbgetentities",
                "format": "json",
                "ids": entity_id
            }
            response = requests.get(api_url, params=params)
            labels = response.json().get("entities", {}).get(entity_id, {}).get("labels", {})
            
            if lang in labels:
                topic_name = labels[lang].get("value")
                
                if topic_name:
                    yield (topic_name, entity_id)


# """
# Once you got those ids, you just need to request entities labels using the wbgetentities API:
# https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q775450|Q3041294|Q646968|Q434841|Q11920&format=json&props=labels

# you can even get results for only some languages, using the languages parameter:
# https://www.wikidata.org/w/api.php?action=wbgetentities&ids=Q775450|Q3041294|Q646968|Q434841|Q11920&format=json&props=labels&languages=en|de|fr
# """

def get_topics_from_wkdt_search_tool(url: str, api_url: str, query: str, lang: str, limit: int = 500) -> Dict[str, str]:
    """
    Retrieves instances from the Wikidata search tool based on a given query, and then finds the related topics for each instance.

    Args:
        url (str): The URL of the Wikidata search tool.
        api_url (str): The URL of the Wikidata API.
        query (str): The search query to retrieve instances.
        lang (str): The language code for the labels of the retrieved instances.
        limit (int, optional): The maximum number of instances to retrieve. Default is 500.

    Returns:
        dict: A dictionary containing the retrieved topics as keys and their corresponding entity IDs as values.
    """
    wikidata_topics = {}
    params = {
        "title": "Special:Search",
        "limit": limit,
        "offset": 0,
        "ns0": 1,
        "ns120": 1,
        "search": query
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError if the response status code is 4XX or 5XX
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            # Find all search result items
            search_results = soup.find_all("div", class_="mw-search-result-heading")
            # Extract IDs from search results
            retrieved_ids = [result.find("a").get("href").split("/")[-1] for result in search_results if result.find("a")]
            for page_id in retrieved_ids:
                for topic, entity_id in get_instances_by_property_P31(api_url, page_id, lang):
                    if topic not in wikidata_topics:
                        wikidata_topics[topic] = entity_id
            return wikidata_topics 

        logging.error(f"Failed to retrieve data for query \"{query}\". Status code: {response.status_code}")
        return wikidata_topics

    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return wikidata_topics
    except Exception as e:
        logging.error(f"Error from query \"{query}\": {e}")
        return wikidata_topics


if __name__ == "__main__":
    # wikidata_topics = get_topics_from_wkdt_search_tool(url, api_url, "reduced vision", "en", 30)
    # print(wikidata_topics)
    page_id = 'Q13360264'
    page_params = {
        "action": "wbgetentities",
        "format": "json",
        "ids": page_id
    }
    page_response = requests.get(api_url, params=page_params)
    claims = page_response.json().get("entities", {}).get(page_id, {}).get("claims", {})
    print(claims)


