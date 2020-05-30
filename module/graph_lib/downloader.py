from SPARQLWrapper import SPARQLWrapper, JSON
import time

from module.graph_lib.constants import *

endpoint = SPARQLWrapper("https://query.wikidata.org/bigdata/namespace/wdq/sparql")
wd = "PREFIX wd: <http://www.wikidata.org/entity/>"
wdt = "PREFIX wdt: <http://www.wikidata.org/prop/direct/>"


def query(query):
    endpoint.setQuery(query)
    endpoint.setReturnFormat(JSON)
    result = None
    while result is None:
        try:
            result = endpoint.query().convert()
        except:
            print("HTTP Timeout! Sleeping...")
            time.sleep(5)
    return result


def download_all_data():
    print("Downloading from Wikidata....")
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
    for (concept1, concept2) in EDGES_DICT:
        mapping = EDGES_DICT[(concept1, concept2)]
        if type(mapping) is not list:
            mapping = [mapping]
        for relation, query_template in mapping:
            concept1_id, concept2_id = CONCEPT_LABEL_ID_DICT[concept1], CONCEPT_LABEL_ID_DICT[concept2]
            relation_id = RELATION_LABEL_ID_DICT[relation]
            q = query_template(concept1_id, relation_id)
            print("Downloading tuple: {} | {} | {}".format(concept1, RELATION_ID_LABEL_DICT[relation_id], concept2))
            res = query(q)

            with open(os.path.join(DOWNLOAD_DIR, "{}_{}_{}.tsv".format(concept1_id, concept2_id, relation_id)), "w", encoding="utf-8") as f:
                for entry in res["results"]["bindings"]:
                    # entry['concept']['value'] returns http://www.wikidata.org/entity/Q17815615. Only want id Q17815615.
                    instance1_id = entry['concept']['value'].split("/")[-1]
                    instance1_label = entry['conceptLabel']['value']
                    instance2_id = entry['peripheralConcept']['value'].split("/")[-1]
                    instance2_label = entry['peripheralConceptLabel']['value']
                    f.write("{}\t{}\t{}\t{}\n".format(instance1_id, instance1_label, instance2_id, instance2_label))
