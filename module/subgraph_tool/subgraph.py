"""
Subgraph Tool
"""

from module.graph_lib.graph_utils import *
from module.graph_lib.constants import *


def get_subgraph_k_hops_around_node(g, instance_id, k, max_results, get_stats=False):
    """
    Performs BFS starting at node corresponding to instance_id, and returns subgraph with all neighbors
    of node within k hops. Direct neighbors corresponds to k=1. Also returns information on the types
    of nodes encountered at each level of k.
    :param g: (Graph) BGV backend Graph
    :param instance_id: (string) id of node around which to build subgraph
    :param k: (string) number of hops around instance_id of node to include in subgraph
    :param max_results: (int) maximum number of nodes to present in subgraph
    :param get_stats: (bool) return a dictionary detailing concept distributions at every hop
    :return: (Graph) subgraph with all neighbors of node within k hops
    :return: (list[tuples]) target_results holds a list of tuples containing all visited nodes
                            as well as the path_length from instance_id
    :return: (dict) {hop_num: {concept1: concept1_count, concept2: concept2_count ...}...}
    """

    k_count_dict = dict()
    q = [(instance_id, 0)]
    visited = set()  # only stores node ids
    target_results = list()  # stores tuples of node ids and path length from instance_id

    while len(q) > 0:
        curr_id, curr_k = q.pop(0)
        if curr_id not in visited:

            if len(target_results) < max_results:
                visited.add(curr_id)
                target_results.append((curr_id, curr_k))
            else:  # if reached max_results, return
                return g.get_subgraph(visited), target_results, k_count_dict

            if get_stats:  # store concept distribution at each hop
                if curr_k not in k_count_dict:
                    k_count_dict[curr_k] = dict()
                curr_concept_id = g.get_concept_id(curr_id)
                if curr_concept_id not in k_count_dict[curr_k]:
                    k_count_dict[curr_k][curr_concept_id] = 0
                k_count_dict[curr_k][curr_concept_id] += 1

            if curr_k < k:  # continue and process neighbors
                for child_id in g.get_node_neighbors(curr_id):
                    q.append((child_id, curr_k+1))

    return g.get_subgraph(visited), target_results, k_count_dict


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


def subgraph_tool(instance_id, concept_id=None, k=2, max_results=100):
    """
    Given a starting node, an ending node type, and number of hops, return subgraph in json dictionary form.
    :param instance_id: (string) starting node id
    :param concept_id: (string) id of type/domain/concept of ending node
    :param k: (int) maximum number of hops from starting node to explore
    :param max_results: (int) maximum number of leaf nodes of type concept_id to present
    :return: (dict) contains results list and subgraph
    """
    g = get_graph()

    if concept_id:
        concept_label = CONCEPT_ID_LABEL_DICT[concept_id]
        subg, target_results = get_subgraph_k_hops_around_node_concept_type(g, instance_id, concept_id, k, max_results)
    else:
        subg, target_results, _ = get_subgraph_k_hops_around_node(g, instance_id, k, max_results)

    graph_dict = graph_to_dict(subg)
    results_list = list()
    for node_id, path_length in target_results:

        if concept_id is None:
            concept_label = CONCEPT_ID_LABEL_DICT[g.get_concept_id(node_id)]

        result_dict = {'name': g.get_instance_label(node_id), 'domain': concept_label, 'path_length': path_length}
        results_list.append(result_dict)
    json_dict = {'results': results_list, 'graph': graph_dict}
    return json_dict
