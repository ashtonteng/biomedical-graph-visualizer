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
