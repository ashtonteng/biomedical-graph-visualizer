"""
Various functions that operate on internal Graph and Node classes.
"""
import json

from .graph import *


def get_graph(pickle_path=GRAPH_PICKLE_PATH):
    """
    if pickle_path given exists, loads pickle and returns graph.
    Otherwise, builds BGV graph, saves it to disk as pickle, and returns graph
    :return: (Graph) g
    """
    if os.path.exists(pickle_path):
        g = Graph(pickle_path=pickle_path)
        print("Loaded Graph from {}".format(pickle_path))
    else:
        pickle_path = GRAPH_PICKLE_PATH
        g = Graph()
        g.save_graph_to_pickle(pickle_path=pickle_path)
        print("Saved Graph to disk as {}".format(pickle_path))
    return g


def save_all_node_names_ids_json(g):
    """
    Writes a dictionary of all nodes to json file, {instance_label:instance_id}
    :param g: (Graph) BGV backend graph.
    :return: None
    """
    json_string = json.dumps({g.get_instance_label(node): node for node in g})
    with open("all_node_names_ids.json", "w") as f:
        f.write(json_string)
    print("Saved all node names and ids to all_node_names_ids.json")


def save_all_concept_names_ids_json():
    """
    Writes a dictionary of all concepts to json file, {concept_label:concept_id}
    :return: None
    """
    json_string = json.dumps(CONCEPT_LABEL_ID_DICT)
    with open("all_concept_names_ids.json", "w") as f:
        f.write(json_string)
    print("Saved all concept names and ids to all_concpet_names_ids.json")


def get_subgraph_k_hops_around_node(g, instance_id, k):
    """
    Performs BFS starting at node corresponding to instance_id, and returns subgraph with all neighbors
    of node within k hops. Direct neighbors corresponds to k=1. Also returns information on the types
    of nodes encountered at each level of k.
    :param g: (Graph) BGV backend Graph
    :param instance_id: (string) id of node around which to build subgraph
    :param k: (string) number of hops around instance_id of node to include in subgraph
    :return: (Graph) subgraph with all neighbors of node within k hops
    :return: (dict) {hop_num: {concept1: concept1_count, concept2: concept2_count ...}...}
    """
    k_count_dict = dict()
    q = [(instance_id, 0)]
    visited = set()
    while len(q) > 0:
        curr_id, curr_k = q.pop(0)
        if curr_id not in visited:

            if curr_k not in k_count_dict:
                k_count_dict[curr_k] = dict()
            curr_concept_id = g.get_concept_id(curr_id)
            if curr_concept_id not in k_count_dict[curr_k]:
                k_count_dict[curr_k][curr_concept_id] = 0
            k_count_dict[curr_k][curr_concept_id] += 1

            visited.add(curr_id)
            if curr_k < k:
                for child_id in g.get_node_neighbors(curr_id):
                    q.append((child_id, curr_k+1))
    return g.get_subgraph(visited), k_count_dict
