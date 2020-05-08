import os

import networkx as nx

from .constants import *


DOWNLOAD_DIR = "./queries/download"


class Graph:

    def __init__(self):
        self.G = None
        print("Building graph from local files, please wait for success message...")
        self.build_graph()
        print("Success: done building graph! Graph has {} nodes.".format(self.G.number_of_nodes()))

    def build_graph(self):
        self.G = nx.MultiDiGraph()  # allows self_loops and multiedges
        for (concept1, concept2) in EDGES_DICT:
            relation, query_template = EDGES_DICT[(concept1, concept2)]
            concept1_id, concept2_id = CONCEPT_LABEL_ID_DICT[concept1], CONCEPT_LABEL_ID_DICT[concept2]
            relation_id = RELATION_LABEL_ID_DICT[relation]

            f = open(os.path.join(DOWNLOAD_DIR, "{}_{}_{}.tsv".format(concept1_id, concept2_id, relation_id)), "r")
            for line in f:
                instance1_id, instance1_label, instance2_id, instance2_label = line.split("\t")
                node1 = Node(instance1_id, instance1_label, concept1_id)
                node2 = Node(instance2_id, instance2_label, concept2_id)
                if instance1_id not in self.G:
                    self.G.add_node(instance1_id, data=node1)
                if instance2_id not in self.G:
                    self.G.add_node(instance2_id, data=node2)
                self.G.add_edge(instance1_id, instance2_id, relation_id=relation_id)

    def get_node(self, instance_id):
        """
        :param instance_id: id of instance
        :return: Node instance corresponding to instance_id
        """
        if instance_id not in self.G:
            raise ValueError("Node {} not found".format(instance_id))
        return self.G.nodes[instance_id]['data']

    def get_node_successors(self, instance_id):
        """
        Gets all successors of current node. May contain current node.
        :param instance_id: id of instance
        :return: list of successors
        """
        if instance_id not in self.G:
            raise ValueError("Node {} not found".format(instance_id))
        return list(set(self.G.successors(instance_id)))

    def get_node_predecessors(self, instance_id):
        """
        Gets all predecessors of current node. May contain current node.
        :param instance_id: id of instance
        :return: list of predecessors
        """
        if instance_id not in self.G:
            raise ValueError("Node {} not found".format(instance_id))
        return list(set(self.G.predecessors(instance_id)))

    def get_node_neighbors(self, instance_id):
        """
        Gets all neighbors of current node. May contain current node.
        :param instance_id: id of instance
        :return: list of neighbors
        """
        if instance_id not in self.G:
            raise ValueError("Node {} not found".format(instance_id))
        return list(set(self.get_node_successors(instance_id) + self.get_node_predecessors(instance_id)))

    def get_directional_edges(self, instance1_id, instance2_id):
        """
        Gets a list of relation_ids *from* instance1 *to* instance2
        :param instance1_id: id of instance1
        :param instance2_id: id of instance2
        :return: list of relation_ids
        """
        if instance1_id not in self.G:
            raise ValueError("Node {} not found".format(instance1_id))
        if instance2_id not in self.G:
            raise ValueError("Node {} not found".format(instance2_id))

        if instance2_id not in self.G[instance1_id]:
            return []  # no edges between them
        else:
            view = self.G[instance1_id][instance2_id]
            return [view[key]['relation_id'] for key in view]

    def get_edges(self, instance1_id, instance2_id):
        """
        Gets a list of relation_ids between instance1 and instance2 regardless of direction.
        :param instance1_id: id of instance1
        :param instance2_id: id of instance2
        :return: list of relation_ids
        """
        if instance1_id not in self.G:
            raise ValueError("Node {} not found".format(instance1_id))
        if instance2_id not in self.G:
            raise ValueError("Node {} not found".format(instance2_id))
        return self.get_directional_edges(instance1_id, instance2_id) + self.get_directional_edges(instance2_id, instance1_id)


class Node:

    def __init__(self, instance_id, instance_label, concept_id):
        """
        Class for all nodes in the Biomedical Graph Visualizer.
        :param instance_id: id of this instance
        :param instance_label: label of this instance
        :param concept_id: id of the type of this instance
        """
        self.instance_id = instance_id
        self.instance_label = instance_label
        self.concept_id = concept_id

    def __str__(self):
        return "{} ({}) ({})".format(self.instance_label, self.instance_id, CONCEPT_ID_LABEL_DICT[self.concept_id])

    def __repr__(self):
        return "{} ({}) ({})".format(self.instance_label, self.instance_id, CONCEPT_ID_LABEL_DICT[self.concept_id])

