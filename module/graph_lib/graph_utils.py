"""
Various functions that operate on internal Graph and Node classes.
"""
import json
import pickle

import module.graph_lib.graph as graph
from module.graph_lib.constants import *


def get_graph(pickle_path=GRAPH_PICKLE_PATH, replace_pickle=False):
    """
    if pickle_path given exists, loads pickle and returns graph.
    Otherwise, builds BGV graph, saves it to disk as pickle, and returns graph
    :param pickle_path: (string) path to save graph pickle
    :param replace_pickle: (bool) if True, even if pickle_path exists, replace it with new version
    :return: (Graph) g
    """
    if os.path.exists(pickle_path) and replace_pickle is False:
        g = graph.Graph(pickle_path=pickle_path)
        print("Loaded Graph from {}".format(pickle_path))
    else:
        pickle_path = GRAPH_PICKLE_PATH
        g = graph.Graph()
        g.save_graph_to_pickle(pickle_path=pickle_path)
        print("Saved Graph to disk as {}".format(pickle_path))
    return g


def get_pagerank_dict(pickle_path=PAGERANK_DICT_PICKLE_PATH, replace_pickle=False):
    """
    if pickle_path given exists, loads pickle and returns graph.
    Otherwise, builds BGV graph, saves it to disk as pickle, and returns graph
    :param pickle_path: (string) path to load graph pickle
    :param replace_pickle: (bool) if True, even if pickle_path exists, replace it with new version
    :return: (Graph) g
    """
    if os.path.exists(pickle_path) and replace_pickle is False:
        pagerank_dict = pickle.load(open(pickle_path, "rb"))
        print("Loaded PageRank dict from {}".format(pickle_path))
    else:
        g = get_graph()
        pickle_path = PAGERANK_DICT_PICKLE_PATH
        pagerank_dict = g.rank_nodes()
        pickle.dump(pagerank_dict, open(pickle_path, "wb"))
        print("Saved PageRank dict to disk as {}".format(pickle_path))

    return pagerank_dict


def save_all_node_names_ids_json(g, out_path):
    """
    Writes a dictionary of all nodes to json file, {instance_label:(instance_id, concept_id)}
    :param out_path: (string) path to write json file
    :param g: (Graph) BGV backend graph.
    :return: None
    """
    print(out_path)
    json_string = json.dumps({g.get_instance_label(node): (node, g.get_concept_id(node)) for node in g})
    with open(out_path, "w") as f:
        f.write(json_string)
    print("Saved all node names and ids to {}".format(out_path))


def save_all_concept_names_ids_json(out_path):
    """
    Writes a dictionary of all concepts to json file, {concept_label:concept_id}
    :param out_path: (string) path to write json file
    :return: None
    """
    json_string = json.dumps(CONCEPT_LABEL_ID_DICT)
    with open(out_path, "w") as f:
        f.write(json_string)
    print("Saved all concept names and ids to {}".format(out_path))


def graph_to_dict(g):
    """
    Encodes a Graph in web-friendly dictionary format.
    :param g: (Graph) BGV backend Graph
    :return: (dict) graph_dict contains web-friendly information about nodes and edges
    """
    pagerank_dict = get_pagerank_dict()
    node_dicts = []
    for node in g:
        node_info = g.get_node(node)
        node_dict = {'qid': node, 'label': node_info['instance_label'],
                     'domain': CONCEPT_ID_LABEL_DICT[node_info['concept_id']], 'rank': pagerank_dict[node]}
        node_dicts.append(node_dict)

    link_dicts = []
    existing_edges = set()
    for src_node_id, dst_node_id, relation_id in g.get_all_edges():
        if (src_node_id, dst_node_id) in existing_edges:  # only keep one copy of an edge between src and dst
            continue
        else:
            existing_edges.add((src_node_id, dst_node_id))
            existing_edges.add((dst_node_id, src_node_id))
            link_dict = {'target': dst_node_id, 'source': src_node_id,
                         'weight': 0.1, 'label': RELATION_ID_LABEL_DICT[relation_id]}
            link_dicts.append(link_dict)

    graph_dict = {'nodes': node_dicts, 'links': link_dicts}
    return graph_dict
