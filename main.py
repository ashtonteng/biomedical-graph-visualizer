from downloader import query
from queries.templates import *
from queries.constants import *


def download_all_data():
    print("Downloading....")
    for (core_concept, periphery_concept) in EDGES_DICT:
        relation, query_template = EDGES_DICT[(core_concept, periphery_concept)]
        q = query_template(CONCEPT_ID_DICT[core_concept], RELATION_ID_DICT[relation])
        print(q)
        print('-'*50)
        res = query(q) # limit your results in templates.py before testing!
        for entry in res["results"]["bindings"]:
            concept = entry['concept']['value']
            concept_label = entry['conceptLabel']['value']
            peripheral_concept = entry['peripheralConcept']['value']
            peripheral_concept_label = entry['peripheralConceptLabel']['value']
            print(concept, concept_label, peripheral_concept, peripheral_concept_label)

if __name__ == '__main__':
    download_all_data()
    