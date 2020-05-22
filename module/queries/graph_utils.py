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


def save_all_node_names_ids_json(g, out_path="all_node_names_ids.json"):
    """
    Writes a dictionary of all nodes to json file, {instance_label:instance_id}
    :param out_path: (string) path to write json file
    :param g: (Graph) BGV backend graph.
    :return: None
    """
    json_string = json.dumps({g.get_instance_label(node): node for node in g})
    with open(out_path, "w") as f:
        f.write(json_string)
    print("Saved all node names and ids to {}".format(out_path))


def save_all_concept_names_ids_json(out_path="all_concept_names_ids.json"):
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
    node_dicts = []
    for node in g:
        node_info = g.get_node(node)
        node_dict = {'qid': node, 'label': node_info['instance_label'],
                     'domain': CONCEPT_ID_LABEL_DICT[node_info['concept_id']]}
        node_dicts.append(node_dict)

    link_dicts = []
    for src_node_id, dst_node_id, relation_id in g.get_all_edges():
        link_dict = {'target': dst_node_id, 'source': src_node_id,
                     'weight': 0.1, 'label': RELATION_ID_LABEL_DICT[relation_id]}
        link_dicts.append(link_dict)

    graph_dict = {'nodes': node_dicts, 'links': link_dicts}
    return graph_dict


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


def get_subgraph_k_hops_around_node_concept_type(g, instance_id, concept_id, k, max_results):
    """
    Performs BFS starting at node corresponding to instance_id, and returns subgraph with all neighbors
    of node within k hops of type concept_id. Subgraph also includes all nodes on the path between
    instance_id and the ending nodes of type concept_id.
    :param g: (Graph) BGV backend Graph
    :param instance_id: (string) id of node around which to build subgraph
    :param concept_id: (string) id of concept in which to end paths with
    :param k: (string) number of hops around instance_id of node to include in subgraph
    :param max_results: (int) maximum number of leaf nodes of type concept_id to present
    :return: (Graph) subgraph with all neighbors of node within k hops
    :return: (list[tuples]) target_concept_results holds a list of tuples containing all visited nodes
                            of type concept_id, as well as the path_length from instance_id
    """

    q = [([instance_id], 0)]
    visited = set()
    subgraph_nodes = set()
    target_concept_results = list()

    while len(q) > 0:
        curr_path, curr_k = q.pop(0)
        curr_id = curr_path[-1]

        if curr_id not in visited:
            visited.add(curr_id)

            if g.get_concept_id(curr_id) == concept_id:  # encountered desired concept
                if len(target_concept_results) < max_results:
                    subgraph_nodes.update(curr_path)  # add all nodes in this path to our subgraph
                    target_concept_results.append((curr_id, curr_k))
                else:  # if reached max_results, return
                    return g.get_subgraph(subgraph_nodes), target_concept_results

            if curr_k < k:
                for child_id in g.get_node_neighbors(curr_id):
                    q.append((curr_path + [child_id], curr_k+1))

    return g.get_subgraph(subgraph_nodes), target_concept_results


def subgraph_tool(instance_id, concept_id, k, max_results=100):
    """
    Given a starting node, an ending node type, and number of hops, return subgraph in json dictionary form.
    :param instance_id: (string) starting node id
    :param concept_id: (string) id of type/domain/concept of ending node
    :param k: (int) maximum number of hops from starting node to explore
    :param max_results: (int) maximum number of leaf nodes of type concept_id to present
    :return: (dict) contains results list and subgraph
    """
    concept_label = CONCEPT_ID_LABEL_DICT[concept_id]
    g = get_graph()
    subg, target_concept_results = get_subgraph_k_hops_around_node_concept_type(g, instance_id, concept_id, k, max_results)
    graph_dict = graph_to_dict(subg)
    results_list = list()
    for node_id, path_length in target_concept_results:
        result_dict = {'name': g.get_instance_label(node_id), 'domain': concept_label, 'path_length': path_length}
        results_list.append(result_dict)
    json_dict = {'results': results_list, 'graph': graph_dict}
    return json_dict
