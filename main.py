from downloader import query
from queries.templates import *
from queries.constants import *


def download_all_data():
    print("Downloading....")
    for (core_concept, periphery_concept) in EDGES_DICT:
        relation, query_template = EDGES_DICT[(core_concept, periphery_concept)]
        q = query_template(CONCEPT_ID_DICT[core_concept], RELATION_ID_DICT[relation])
        
        print(q)
        
        '''res = query(q)
        for entry in res["results"]["bindings"]:
            for key in entry:
                print(key, entry[key]["value"])'''

if __name__ == '__main__':
    download_all_data()
    