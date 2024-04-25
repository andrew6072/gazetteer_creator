SELECT DISTINCT ?item ?itemLabel 
WHERE {
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
  {
    SELECT DISTINCT ?item WHERE {
      ?item p:P31 ?statement0.
      ?statement0 (ps:P31/(wdt:P279*)) wd:Q12308941.
    }
    LIMIT 100
  }
  FILTER EXISTS {
    ?item rdfs:label ?label .
    FILTER(LANG(?label) = 'en')
  }
}