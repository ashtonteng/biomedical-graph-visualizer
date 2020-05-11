"""
Various functions that operate on internal Graph and Node classes.
"""
import json
import pickle

from .graph import *


def build_and_pickle_graph():
    """
    Builds BGV graph and saves it to disk with pickle.
    :return: (Graph) g
    """
    g = Graph()
    pickle.dump(g, open("BGV_Graph.pkl", "wb"))
    print("Saved Graph to disk as BGV_Graph.pkl")
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
    of node within k hops. Direct neighbors corresponds to k=1.
    :param g: (Graph) BGV backend Graph
    :param instance_id: (string) id of node around which to build subgraph
    :param k: (string) number of hops around instance_id of node to include in subgraph
    :return: (Graph) subgraph with all neighbors of node within k hops
    """
    q = [(instance_id, 0)]
    visited = set()
    while len(q) > 0:
        curr_id, curr_k = q.pop(0)
        if curr_id not in visited:
            visited.add(curr_id)
            if curr_k < k:
                for child_id in g.get_node_neighbors(curr_id):
                    q.append((child_id, curr_k+1))
    return g.get_subgraph(visited)
