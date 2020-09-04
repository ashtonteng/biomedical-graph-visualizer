"""This script executes steps 1-5 of the following CV pipeline:
1. Get a set of all nodes 1-hop away from the condition
2. Split 80/20 train/test
3. Remove direct edges between condition and test set
4. Save each fold as a separate graph
5. Preprocess each CV graph for embedding scripts
6. Create embeddings for each CV graph
7. Evaluate NN results
"""
import copy
import os
import re

from sklearn import model_selection
from test_constants import TEST_CONDITIONS, TREATS
from module.graph_lib import graph_utils
from module.graph_lib.graph import Graph
from module.similarity_tool.preprocessing import preprocess_graph_for_relation_prediction

N_FOLDS = 5


def _write_to_file(path, data):
    f = open(path, 'w')
    for x in data:
	fstr = x + '\n'
        f.write(fstr)
    f.close()
    print('Done writing data to {}'.format(path))


def get_drugs_used_to_treat_condition(G, medical_condition):
    """Return a list of drug instance IDs used to treat a given medical condition based on the relationships
    present in the graph G

    Args:
        G (Graph): Graph to query
        medical_condition (dict): Query condition
    Returns: list(string) of instance IDs of drugs used to treat the input query medical_condition

    """
    # Get a list of neighbors
    a_instance_id = medical_condition['ID']
    neighbors = G.get_node_neighbors(a_instance_id)
    # Only consider neighbors that are drugs used for treating this condition
    drugs_used_for_treatment = [
        b_instance_id for b_instance_id in neighbors if TREATS in G.get_edges_between(a_instance_id, b_instance_id)]
    return drugs_used_for_treatment


def gen_cv_graphs(G, medical_condition, data_prefix='./data'):
    """Takes a single Graph instance as input and outputs Nn_FOLDS graphs for each CV split

    Args:
        G (Graph): The full biomedical graph taken from WikiData
        medical_condition (dict): The condition from test_constants to run CV on
        data_prefix (str): location to save CV graph .pkl files
    Returns: pkl_paths list(string) of file paths where CV graphs are saved

    """
    a_instance_id = medical_condition['ID']
    drugs_used_for_treatment = get_drugs_used_to_treat_condition(
        G, medical_condition)
    # Split into 5 folds for 80/20 for train/test split
    kf = model_selection.KFold(n_splits=N_FOLDS)
    pkl_paths = list()
    for fold, (train_index, test_index) in enumerate(kf.split(drugs_used_for_treatment)):
        # Create a copy of the main graph for each CV fold
        g = copy.deepcopy(G)
        X_test = [drugs_used_for_treatment[i] for i in test_index]
        for b_instance_id in X_test:
            g.remove_all_edges_between(a_instance_id, b_instance_id)
        print("Base graph edges: ", len(G.get_all_edges()))
        print("Fold graph edges: ", len(g.get_all_edges()))
        print("Train neighbors: ", len(train_index))
        print("Test  neighbors: ", len(test_index))
        # Save each fold as a separate graph
        lowercase_name = medical_condition['Name'].replace(' ', '_').lower()
        txt_path = os.path.join(data_prefix, "cv_graph_{}_{}_test_instance_ids.txt".format(lowercase_name, fold))
        print("Saving test instance_ids in {}".format(txt_path))
        _write_to_file(txt_path, X_test)
        pkl_path = os.path.join(data_prefix, "cv_graph_{}_{}.pkl".format(lowercase_name, fold))
        print("Saving CV fold graph for {} in {}".format(lowercase_name, pkl_path))
        g.save_graph_to_pickle(pkl_path)
        pkl_paths.append(pkl_path)
    return pkl_paths


def gen_embeddings_input(pkl, embedding_input_dir_prefix='./data'):
    """Takes a graph pkl file as input and saves .txt files for generating embeddings as output.

    Args:
        pkl (str): file path for a graph pickle file to read and preprocess for embedding
        embedding_input_dir_prefix (str): location to save embedding input .txt files

    Returns: None

    """
    g = Graph(pickle_path=pkl).G
    embedding_input_dir = os.path.join(embedding_input_dir_prefix, re.split('[/.]', pkl)[-2])
    print(embedding_input_dir)
    if not os.path.exists(embedding_input_dir):
        os.makedirs(embedding_input_dir)
    preprocess_graph_for_relation_prediction(g, embedding_input_dir)


if __name__ == "__main__":
    G = graph_utils.get_graph()
    # Preprocess data for generating embeddings
    for cond in TEST_CONDITIONS:
        pkl_paths = gen_cv_graphs(G, cond)
        for pkl in pkl_paths:
            gen_embeddings_input(pkl)

