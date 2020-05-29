import argparse
import json
import fire
import numpy as np
import sklearn.neighbors as sk_neighbors
import os
import sys
import json
sys.path.append(os.getcwd())

from module.queries.graph         import Graph
from module.queries.graph_utils   import get_graph
from typing                import Union
from collections           import defaultdict, Counter
from gensim.models         import keyedvectors
from sklearn.decomposition import PCA
from sklearn.metrics       import pairwise


class NearestNeighbors:
    f"""Restrive k nearest neighbors for each of the provided targets

    
    :param targets (list, str): the target name for getting nearest neighbors
            OR list of target names for retrieving nearest neighbors.
    :param emb_file_path (str): path to the node2vec embedding file.
    :param n_neighbors (int): number of nearest neighbors to retrieve
    :param distance_metric (str): the choice of distance metric
    :param exlcude_targets (bool): exclude any input targets from neighbor lists
    
    Returns:
        A dictionary with targets as keys and a another dictionary of neighbors
        and distances to neighbors as values.
    """

    METRICS = {
        "l1": pairwise.manhattan_distances, 
        "l2": pairwise.euclidean_distances,
        "cos": pairwise.cosine_distances, 
    }

    AGGREGATION_METHODS = ['nearest','mean','majority'] 

    def __init__(self, 
                 targets: Union[list, str],
                 emb_file_path: str = "./ent_emb.json",
                 n_neighbors: int = 5, 
                 distance_metric: str = "cos", 
                 exclude_targets: bool = True, 
                 aggregate_method: str = None
                 ):
        # get graph
        self.G = get_graph()

        # check inputs
        if type(targets) == str:
            targets = [targets]
        if distance_metric not in self.METRICS.keys():
            raise Exception("NN algorithm must be one of {METRICS.keys()}")
        if aggregate_method not in self.AGGREGATION_METHODS and aggregate_method is not None:
            raise Exception(f"Aggregation method should be one of {self.AGGREGATION_METHODS}")

        # get concept type
        concepts = [self.G.get_concept_id(t) for t in targets]
        if len(list(set(concepts))) != 1:
            raise Exception("Targets are not under the same concepts ")
        self.concept = concepts[0]

        # check if targets are the same type
        self.targets = [str(t) for t in targets]
        concepts = [self.G.get_concept_id(t) for t in self.targets]
        if len(list(set(concepts))) >1:
            raise Exception("More than one type of targest are provided")
        self.concept = concepts[0]

        # store class variables
        self.n_neighbors = n_neighbors
        self.exclude_targets = exclude_targets
        self.metric = distance_metric 
        self.aggregate_method = aggregate_method
        self.distance = self.METRICS[distance_metric]

        # get embeddings
        vocab, vectors = self.get_embeddings(emb_file_path)
        self.vocab, self.vectors = self._filter_by_concept(vocab, 
                                                          vectors, 
                                                          self.concept,
                                                          self.G)

        # get PCA components
        self.node_2_pca = self.get_pca_components(self.vocab, self.vectors)

        #  get neighbors
        self.neighbors = self._get_neighbors()

        # get PCA mean
        neighbor_pca = [self.node_2_pca[n] for n in self.neighbors.keys()]
        self.neighbor_pca_mean = np.mean(neighbor_pca, axis=0)

        # aggregate results
        if self.aggregate_method is not None:
            self.neighbors = self.aggregate_neighbors(method=self.aggregate_method)

    def __getitem__(self, key):
        """
        :key: target id to get neigbors for 
        :return: list of (neighbor, distance) pairs
        """
        return self.neighbors[key]

    def aggregate_neighbors(self, method:str = "nearest"):
        f"""aggregate nearest neighbors of all targets

        :param method (str): method used to aggregate neighbors.
                aggregating method should be one of {self.AGGREGATION_METHODS}.
                nearest -> aggregate and pick top k neighbor based on distance
                mean -> takes the mean distance for each neighbor and pick nearest
                majority -> pick the neighbors that appears most frequently 
        """
        if method not in self.AGGREGATION_METHODS:
            raise Exception(f"Method has to be one of {self.AGGREGATION_METHODS}")

        # aggregate all neighbors and distances
        neighbors = []
        distances = []
        for k,v in self.neighbors.items():
            # pairs of (neighbor, distance)
            neighbors += [p[0] for p in v]
            distances += [p[1] for p in v]
            
        if method == "nearest":
            # sort and get top k
            nd_dict = defaultdict(lambda: float('inf'))
            for n,d in zip(neighbors, distances):
                if d < nd_dict[n]:
                    nd_dict[n] = d
            neigh_dist_pair = [[k,v] for k,v in nd_dict.items()]
        elif method == "mean":
            neigh_dist = defaultdict(list)
            for n, d in zip(neighbors, distances):
                neigh_dist[n].append(d)
            neigh_dist_pair = [(n,np.mean(d)) for n,d in neigh_dist.items()]
        elif method == "majority":
            neigh_count = Counter()
            for n in neighbors:
                neigh_count[n] += 1
            # take reciprocal so most common neighbor is nearest when sorting
            neigh_dist_pair = [(n,1/c) for n,c in neigh_count.items()]

        # sort neighbors and take top 5    
        neigh_dist_pair = sorted(neigh_dist_pair, 
                                 key=lambda pair: pair[1])
        neigh_dist_pair = neigh_dist_pair[:self.n_neighbors]

        neighbors = {"aggregated": neigh_dist_pair}
        for target in self.targets:
            neighbors[target] = []

        return neighbors

    def get_embeddings(self, emb_file_path:str):
        """get list of embedding and id

        :param emb_file_path (str): path to the embedding file
        """
        embedding_dict = json.load(open(emb_file_path, "rb"))
        vocab = list(embedding_dict.keys())
        vectors = list(embedding_dict.values())
        return vocab, vectors

    def get_neighbors(self, output_path:str = None):
        """save the neighbors as json file

        :param output_path (str): output path of the json file, if not specified
                                  results are not saved 
        """        
        # parse return format for website
        return_list = []
        for idx, (target,neighbors) in enumerate(self.neighbors.items()):

            if target != "aggregated":
                target_dict = self._gen_return_dict(target, 0, idx, True)
                return_list.append(target_dict)

            for neighbor, dist in neighbors:
                neighbor_dict = self._gen_return_dict(neighbor, dist, idx)
                return_list.append(neighbor_dict)

        # sort by similarity score, then by input index
        return_list = sorted(return_list, 
                             key=lambda x: (x["sim_score"], x["input_index"]))
        
        # save output 
        if output_path is not None:
            if output_path.split(".")[-1] != "json":
                output_path = output_path + ".json"
            json.dump(return_list, open(output_path, "w"), indent=4)

        return return_list

    def _gen_return_dict(self, 
                         node:str, 
                         dist:float, 
                         idx:int, 
                         input_node:bool = False):
        """Generate return dictionaries for web input

        :param node (str): node id
        :param dist (float): distance of the node to target
        :param idx (int): target order idx
        :input_node (bool): true if node is one of the input targets
        """
        pc1, pc2 = self.node_2_pca[node] - self.neighbor_pca_mean
        return {"label": self.G.get_node(node)['instance_label'], 
                "id": node, 
                "sim_score": float(dist),   
                "pc1": float(pc1), 
                "pc2": float(pc2), 
                "input_node":  input_node, 
                "input_index": idx}

    def get_pca_components(self, 
                           vocab:list, 
                           vectors:list, 
                           n_components:int = 2):
        """dimentionality reduction using PCA

        :param vocab (list): list of node names
        :param vectors (list): list of node vectors
        :param n_components (int): number of components to return

        :return node name to dimentionality reduced component dictionary
        """
        pca = PCA(n_components=n_components)
        components = pca.fit_transform(vectors)
        return {n:c for n,c in zip(vocab, components)}

    def _filter_by_concept(self, 
                           vocab:list, 
                           vectors:list, 
                           concept:str, 
                           g:Graph):
        """filter nodes by concept type

        :param vocab (list): list of node names
        :param vectors (list): list of vectorized 
        """
        filtered_vocab = []
        filtered_vectors = []
        for voc, vec in zip(vocab, vectors):

            # get node concept
            try:
                voc_concept = g.get_concept_id(voc)
            except:
                print(f"{voc} not found in graph")
                continue

            # populate vector if vocab has the same concept
            if voc_concept == concept:
                filtered_vocab.append(voc)
                filtered_vectors.append(vec)
        
        return filtered_vocab, filtered_vectors
            
    def _get_neighbors(self):
        """Get nearest neighbors based on algorithm of choice"""
        # need to still keep k neighbors after removing targets
        if self.exclude_targets:
            total_neighbors = self.n_neighbors + len(self.targets)
        else: 
            total_neighbors = self.n_neighbors

        # get nearest neighbors 
        nearest_neighbors = defaultdict(list)
        for target in self.targets:

            # get target embedding vector
            target_idx = self.vocab.index(target)
            target_vector = self.vectors[target_idx]

            # get distance
            distances = self.distance([target_vector], self.vectors)[0]

            # exclude targets and get neighbor target pair
            if self.exclude_targets:
                neigh_dist_pair  = [[n,d] for n,d in zip(self.vocab, distances)
                                    if n not in self.targets]
            else:
                neigh_dist_pair  = [[n,d] for n,d in zip(self.vocab, distances)
                                    if n != target]

            # sort by distance
            neigh_dist_pair = sorted(neigh_dist_pair, key=lambda pair: pair[1])

            # keep top k
            if len(neigh_dist_pair) < self.n_neighbors:
                raise Exception("Not enough nearest neighbors") # for debugging
            neigh_dist_pair = neigh_dist_pair[:self.n_neighbors]

            # assign neighbors and distances
            nearest_neighbors[target] = neigh_dist_pair

        return nearest_neighbors


if __name__ == "__main__":
    fire.Fire(NearestNeighbors)
