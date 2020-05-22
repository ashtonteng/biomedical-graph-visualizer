import argparse
import json
import os
import sys
import fire
import numpy as np
import sklearn.neighbors as sk_neighbors
sys.path.append(os.getcwd())

from queries.constants     import NN_ALGORITHMS, AGGREGATION_METHODS
from queries.graph         import Graph
from queries.graph_utils   import get_graph
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
    :param algorithm (str): the choice of neighbors search algorithm, which must be
            one of {NN_ALGORITHMS}
    :param exlcude_targets (bool): exclude any input targets from neighbor lists
    
    Returns:
        A dictionary with targets as keys and a another dictionary of neighbors
        and distances to neighbors as values.
    """

    def __init__(self, 
                 targets: Union[list, str],
                 emb_file_path: str = "./embeddings.emb",
                 n_neighbors: int = 5, 
                 algorithm: str = "cosine_similarity", 
                 exclude_targets: bool = True 
                 ):
        # get graph
        self.G = get_graph()

        # check inputs
        if type(targets) == str:
            targets = [targets]
        if algorithm not in NN_ALGORITHMS:
            raise Exception("NN algorithm must be one of {NN_ALGORITHMS}")

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

        self.n_neighbors = n_neighbors
        self.algorithm = algorithm
        self.exclude_targets = exclude_targets
        self.model = keyedvectors.KeyedVectors.load_word2vec_format(emb_file_path)

        # get relevant concepts vectors
        vocab = self.model.wv.index2word
        vectors = self.model.wv.vectors
        self.vocab, self.vectors = self._filter_by_concept(vocab, 
                                                          vectors, 
                                                          self.concept,
                                                          self.G)

        # get PCA components
        self.node_2_pca = self.get_pca_components(self.vocab, self.vectors)

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
                majority -> pick the neighbors that appears most frequently 
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

        return neigh_dist_pair

    def save_neighbors(self, 
                       output_path:str = "./nearest_neighbors.json",
                       web_format:bool = True):
        """save the neighbors as json file

        :param output_path (str): output path of the json file
        :web_format (bool): save neighbors in web input structure
        """         
        if output_path.split(".")[-1] != "json":
            output_path = output_path + ".json"

        if web_format:
            return_list = []
            for idx, (target,neighbors) in enumerate(self.neighbors.items()):

                target_dict = self._gen_return_dict(target, 0, idx, True)
                return_list.append(target_dict)

                for neighbor, dist in neighbors:

                    neighbor_dict = self._gen_return_dict(neighbor, dist, idx)
                    return_list.append(neighbor_dict)

            return_list = sorted(return_list, 
                                 key=lambda x: (x["sim_score"], x["input_index"]))
            json.dump(return_list, open(output_path, "w"), indent=4)

        else:
            json.dump(self.neighbors, open(output_path, "w"), indent=4)


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
        pc1, pc2 = self.node_2_pca[node]
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
            target_idx = self.vocab.index(target)
            target_vector = self.vectors[target_idx]

            if self.algorithm == "cosine_similarity":
                #target_vector = np.array([target_vector,]*len(self.vectors))
                # get distance
                distances = pairwise.cosine_similarity([target_vector], self.vectors)

                # we only want neighbors that are close 
                distances = [abs(d) for d in distances][0]

                # sort and get neighbor distance pair
                neigh_dist_pair  = [[n,d] for n,d in zip(self.vocab, distances)
                                    if n != target]
                neigh_dist_pair = sorted(neigh_dist_pair, key=lambda pair: pair[1])

            else:
                # create nearest neighbor models
                total_neighbors = total_neighbors + 1   # ordered vector includes target vector
                nn = sk_neighbors.NearestNeighbors(n_neighbors=total_neighbors, 
                                algorithm=self.algorithm)
                nbrs = nn.fit(self.vectors)

                # get neighbors and distance 
                distances, neighbors_idx = nbrs.kneighbors([target_vector])

                # convert to list and remove target point itself
                distances = list(distances)[0][1:]
                neighbors_idx = list(neighbors_idx)[0][1:]
                neighbors = [self.vocab[idx] for idx in neighbors_idx]

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