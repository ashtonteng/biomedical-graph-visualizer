import os
import json

from downloader import query
from queries.constants import *


def download_all_data():
    print("Downloading from Wikidata....")
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)
    for (concept1, concept2) in EDGES_DICT:
        relation, query_template = EDGES_DICT[(concept1, concept2)]
        concept1_id, concept2_id = CONCEPT_LABEL_ID_DICT[concept1], CONCEPT_LABEL_ID_DICT[concept2]
        relation_id = RELATION_LABEL_ID_DICT[relation]
        q = query_template(concept1_id, relation_id)
        print(q)
        res = query(q)

        with open(os.path.join(DOWNLOAD_DIR, "{}_{}_{}.tsv".format(concept1_id, concept2_id, relation_id)), "w") as f:
            for entry in res["results"]["bindings"]:
                # entry['concept']['value'] returns http://www.wikidata.org/entity/Q17815615. Only want id Q17815615.
                instance1_id = entry['concept']['value'].split("/")[-1]
                instance1_label = entry['conceptLabel']['value']
                instance2_id = entry['peripheralConcept']['value'].split("/")[-1]
                instance2_label = entry['peripheralConceptLabel']['value']
                f.write("{}\t{}\t{}\t{}\n".format(instance1_id, instance1_label, instance2_id, instance2_label))


if __name__ == '__main__':
    download_all_data()
