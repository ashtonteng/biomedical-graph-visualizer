
"""This script executes step 7 of the following CV pipeline:
1. Get a set of all nodes 1-hop away from the condition
2. Split 80/20 train/test
3. Remove direct edges between condition and test set
4. Save each fold as a separate graph
5. Preprocess each CV graph for embedding scripts
6. Create embeddings for each CV graph
7. Evaluate NN results
"""
import os
import pandas as pd
import numpy as np

from test_constants import TEST_CONDITIONS
from module.graph_lib.constants import DRUG_ID
from module.subgraph_tool.subgraph import get_graph

N_FOLDS = 5


def load_cv_embeddings(cond, fold):
    # TODO: Don't use a relative path or hardcode this
    fold_data_path = 'data/cv_graph_attention_deficit_hyperactivity_disorder_{}'.format(fold)
    gpath = fold_data_path + '.pkl'
    # End debugging params
    eemb = np.loadtxt(os.path.join(fold_data_path, 'entity2vec.txt'))
    eids = pd.read_csv(os.path.join(fold_data_path, 'entity2id.txt'), header=None, delimiter='\t')
    labels = pd.read_csv(fold_data_path + '_test_instance_ids.txt', header=None)
    labels = labels.values.flatten()
    n_test = len(labels)
    rids = pd.read_csv(os.path.join(fold_data_path, 'relation2id.txt'), header=None, delimiter='\t')
    remb = pd.read_csv(os.path.join(fold_data_path, 'relation2vec.txt'), header=None, delimiter='\t')
    remb = remb.values[:, :-1]
    treated_by_id = rids[rids[0] == 'P2176'][1]  # Get the relation vec ID
    treated_by_emb = remb[treated_by_id]
    cond_vec = eemb[np.where(eids[0].values == cond['ID'])]
    cond_treated_by_vec = cond_vec + treated_by_emb
    # Get pairwise distances between the cond_treated_by_vec and all entity embeddings in the graph
    distances = np.linalg.norm(eemb - cond_treated_by_vec, axis=0)
    # Option 1: Use a distance threshold
    # indices = np.argwhere(distances < 50).flatten()
    # Option 2: Get the indices of the k smallest distances
    # Set k to be the number of test examples for the cross-validation
    k = n_test
    n_drugs_found = 0
    drugs_found = list()
    G = get_graph(pickle_path=gpath)
    while n_drugs_found < n_test:
        indices = np.argpartition(distances, k)
        k_nearest_indices = indices[:k]
        k_nearest_entities = eids[0].loc[k_nearest_indices].values
        for e in k_nearest_entities:
            concept_id = G.get_concept_id(e)
            if concept_id == DRUG_ID and e not in drugs_found:
                drugs_found.append(e)
                n_drugs_found += 1
        if n_drugs_found < n_test:
            print("Found {} drugs in this round, expanding search".format(n_drugs_found))
        else:
            print("Found {} drugs in this round".format(n_drugs_found))
        k += 1
    # Now compute performance metrics
    all_drugs_used_for_treatment = cond['DrugIDs']
    print(drugs_found)
    acc = len(set(drugs_found).intersection(all_drugs_used_for_treatment)) / float(len(labels))
    print("Accuracy for {} fold {}: {}".format(cond['Name'], fold, acc))


if __name__ == "__main__":
    # Load all of the embeddings related to conditions to test
    for cond in TEST_CONDITIONS:
        for fold in range(N_FOLDS):
            load_cv_embeddings(cond, fold)
        break  # TODO: Remove this break if we want to test more conditions
    # Load embeddings
    # Load train indices/node instance IDs
    # Load test indices/node instance IDs
    # Compute KNN
    # Compute sensitivity
