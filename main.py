from downloader import query
from queries.templates import *
from queries.constants import *

TAXON, NO_TAXON, WILDCARD = (query_template_taxon, query_template_no_taxon, query_template_wildcard)
main_concept_id_dict = {GENE: GENE_ID, PROTEIN: PROTEIN_ID}
peripheral_concept_id_dict = {PROTEIN_FAMILY: PROTEIN_FAMILY_ID}
all_concept_id_dict = dict()
all_concept_id_dict.update(main_concept_id_dict)
all_concept_id_dict.update(peripheral_concept_id_dict)
relation_id_dict = {PART_OF: PART_OF_ID}
edges_dict = {(PROTEIN, PROTEIN_FAMILY): (PART_OF, TAXON)}

def download_all_data():
    print("Downloading....")
    for (core_concept, periphery_concept) in edges_dict:
        relation, query_template = edges_dict[(core_concept, periphery_concept)]
        q = query_template(main_concept_id_dict[core_concept], relation_id_dict[relation])
        
        print(q)
        
        '''res = query(q)
        for entry in res["results"]["bindings"]:
            for key in entry:
                print(key, entry[key]["value"])'''

if __name__ == '__main__':
    download_all_data()
    