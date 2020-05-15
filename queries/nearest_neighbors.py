import argparse
import json
import os
import sys
import fire
import numpy as np
import sklearn.neighbors as sk_neighbors
sys.path.append(os.getcwd())

from queries.constants import NN_ALGORITHMS, AGGREGATION_METHODS
from typing            import Union
from collections       import defaultdict, Counter
from gensim.models     import keyedvectors


class NearestNeighbors:
    f"""Restrive k nearest neighbors for each of the provided targets

    
    :param targets (list, str): the target name for getting nearest neighbors
            OR list of target names for retrieving nearest neighbors.
    :param emb_file_path (str): path to the node2vec embedding file.
    :param n_neighbors (int): number of nearest neighbors to retrieve
    :param algorithm (str): the choice of neighbors search algorithm, which must be
            one of {NN_ALGORITHMS}
    :param exlcude_targets (bool): exclude any input targets from neighbor lists
    
    Returns:
        A dictionary with targets as keys and a another dictionary of neighbors
        and distances to neighbors as values.
    """

    def __init__(self, 
                   targets: Union[list, str],
                   emb_file_path: str = "./embeddigns.emb",
                   n_neighbors: int = 5, 
                   algorithm: str = "cosine_similarity", 
                   exclude_targets: bool = True 
                   ):

        # check inputs
        if type(targets) == str:
            targets = [targets]
        if algorithm not in NN_ALGORITHMS:
            raise Exception("NN algorithm must be one of {NN_ALGORITHMS}")

        # read in trained node2vec embeddings
        self.model = keyedvectors.KeyedVectors.load_word2vec_format(emb_file_path)
        self.targets = [str(t) for t in targets]
        self.n_neighbors = 5
        self.algorithm = algorithm
        self.exclude_targets = exclude_targets

        #  get neighbors
        self.neighbors = self._get_neighbors()

    def __getitem__(self, key):
        """
        :return: list of (neighbor, distance) pairs
        """
        return self.neighbors[key]

    def aggregate_neighbors(self, method:str = "nearest"):
        f"""aggregate nearest neighbors of all targets

        :param method (str): method used to aggregate neighbors.
                aggregating method should be one of {AGGREGATION_METHODS}.
                nearest -> aggregate and pick top k neighbor based on distance
                mean -> takes the mean distance for each neighbor and pick nearest
                friendliest -> pick the neighbors that appears most frequently 
        """
        if method not in AGGREGATION_METHODS:
            raise Exception(f"Method has to be one of {AGGREGATION_METHODS}")

        # aggregate all neighbors and distances
        neighbors = []
        distances = []
        for k,v in self.neighbors.items():
            # pairs of (neighbor, distance)
            neighbors += [p[0] for p in v]
            distances += [p[1] for p in v]

        if method == "nearest":
            # sort and get top k
            neigh_dist_pair = zip(neighbors, distances)
        elif method == "mean":
            neigh_dist = defaultdict(list)
            for n, d in zip(neighbors, distances):
                neigh_dist[n].append(d)
            neigh_dist_pair = [(n,np.mean(d)) for n,d in neigh_dist.items()]
        elif method == "friendliest":
            neigh_count = Counter()
            for n in neighbors:
                neigh_count[n] += 1
            # take reciprocal so most common neighbor is nearest when sorting
            neigh_dist_pair = [(n,1/c) for n,c in neigh_count.items()]

        # sort neighbors and take top 5    
        neigh_dist_pair = sorted(neigh_dist_pair, 
                                 key=lambda pair: pair[1])
        neigh_dist_pair = neigh_dist_pair[:self.n_neighbors]

        return neigh_dist_pair

    def save_neighbors(self, output_path: str = "./nearest_neighbors.json"):
        """save the neighbors as json file

        :param output_path (str): output path of the json file
        """         
        if output_path.split(".")[-1] != "json":
            output_path = output_path + ".json"

        json.dump(self.neighbors, open(output_path, "w"), indent=4)

    def _get_neighbors(self):
        """Get nearest neighbors based on algorithm of choice"""

        # need to still keep k neighbors after removing targets
        if self.exclude_targets:
            total_neighbors = self.n_neighbors + len(self.targets)
        else: 
            total_neighbors = self.n_neighbors

        # get nearest neighbors 
        nearest_neighbors = defaultdict(list)
        if self.algorithm == "cosine_similarity":
            for target in self.targets:
                # similary by word returns key, distance pairs
                neighbor_distance_pair = self.model.similar_by_word(target, 
                                                                    topn=total_neighbors)
                # assign nearest neighbors and distances
                nearest_neighbors[target] = neighbor_distance_pair
        else:
            # get vocab and vectors from model
            ordered_vocab = self.model.wv.index2word
            ordered_vectors = self.model.wv.vectors

            # create nearest neighbor models
            total_neighbors = total_neighbors + 1   # ordered vector includes target vector
            nn = sk_neighbors.NearestNeighbors(n_neighbors=total_neighbors, 
                              algorithm=self.algorithm)
            nbrs = nn.fit(ordered_vectors)
            for target in self.targets:
                target_idx = ordered_vocab.index(target)
                target_vector = ordered_vectors[target_idx]
                distances, neighbors_idx = nbrs.kneighbors([target_vector])

                # convert to list and remove target point itself
                distances = list(distances)[0][1:]
                neighbors_idx = list(neighbors_idx)[0][1:]
                neighbors = [ordered_vocab[idx] for idx in neighbors_idx]
                neigh_dist_pair  = [[n,d] for n,d in zip(neighbors, distances)]

                # assign neighbors and distances
                nearest_neighbors[target] = neigh_dist_pair

        # remove targets
        if self.exclude_targets:
            for k, v in nearest_neighbors.items():
                updated_n = [[n,d] for n,d in v if n not in self.targets]
                nearest_neighbors[k] = updated_n
        
        # keep only k 
        for k, v in nearest_neighbors.items():
            if len(v) < self.n_neighbors:
                raise Exception("Not enough nearest neighbors") # for debugging

            neigh_dist_pair = v[:self.n_neighbors]
            neighbors = [p[0] for p in neigh_dist_pair]
            distances = [p[1] for p in neigh_dist_pair]
            
            nearest_neighbors[k] = [[n,d] for n,d in zip(neighbors, distances)]

        return nearest_neighbors


if __name__ == "__main__":
    fire.Fire(NearestNeighbors)