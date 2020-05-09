import argparse
import fire
import gensim
import json

from typing            import Union
from collections       import defaultdict
from sklearn.neighbors import NearestNeighbors


# Nearest Neighbors
NN_ALGORITHMS = ['cosine_similarity', 'ball_tree', 'kd_tree', 'brute', 'auto']


def get_k_neighbors(targets: Union[list, str],
                    emb_file_path: str = "./embeddigns.emb",
                    n_neighbors: int = 5, 
                    algorithm: str = "cosine_similarity",
                    save_output: bool = True,
                    output_path: str = "./nearest_neighbors.json",
                    ):
    f"""Restrive k nearest neighbors for each of the provided targets

    Args:
        tragets (list, str): the target name for getting nearest neighbors
            OR list of target names for retriving nearest neighbors.
        emb_file_path (str): path to the node2vec embedding file.
        n_neighbors (int): number of nearest neighbors to retrieve
        algorithm (str): the choice of neighbors search algorithm, which must be
            one of {NN_ALGORITHMS}
        save_output (bool): if true save nearest neighbors dictionary to disk
        output_path (str): path for saving the nearest neighbors dictionary
    
    Returns:
        A dictionary with targets as keys and a another dictionary of neighbors
        and distances to neighbors as value.
    """

    # check inputs
    if type(targets) == str:
        targets = [targets]
    if algorithm not in NN_ALGORITHMS:
        raise Exception("NN algorithm must be one of {NN_ALGORITHMS}")
    if output_path.split(".")[-1] != "json":
        output_path = output_path + ".json"

    # read in trained node2vec embeddings
    model = gensim.models.keyedvectors.KeyedVectors.load_word2vec_format(emb_file_path)
    unknown_targets = [t for t in targets if t not in model.wv.index2word]
    if len(unknown_targets) != 0:
        raise Exception(f"{unknown_targets} not in node2vec embedding vocabulary")

    # get nearest neighbors
    nearest_neighbors = defaultdict(dict)
    if algorithm == "cosine_similarity":
        for target in targets:
            # similary by word returns key, distance pairs
            neighbor_distance_pair = model.similar_by_word(target, topn=n_neighbors)
            neighbors = [n for n,d in neighbor_distance_pair]
            distances = [d for n,d in neighbor_distance_pair]

            # assign nearest neighbors and distances
            nearest_neighbors[target]["neighbors"] = neighbors
            nearest_neighbors[target]["distances"] = distances
    else:
        # get vocab and vectors from model
        ordered_vocab = model.wv.index2word
        ordered_vectors = model.wv.vectors

        # create nearest neighbor models
        n_neighbors = n_neighbors + 1   # ordered vector includes target vector
        nn = NearestNeighbors(n_neighbors=n_neighbors, algorithm=algorithm)
        nbrs = nn.fit(ordered_vectors)
        for target in targets:
            target_idx = ordered_vocab.index(target)
            target_vector = ordered_vectors[target_idx]
            distances, neighbors_idx = nbrs.kneighbors([target_vector])

            # convert to list and remove target point itself
            distances = list(distances)[0][1:]
            neighbors_idx = list(neighbors_idx)[0][1:]
            neighbors = [ordered_vocab[idx] for idx in neighbors_idx]

            # assign neighbors and distances
            nearest_neighbors[target]["neighbors"] = neighbors
            nearest_neighbors[target]["distances"] = distances

    # save nearest_neighbors
    if save_output:
        json.dump(nearest_neighbors, open(output_path, "w"), indent=4)

    return nearest_neighbors


if __name__ == "__main__":
    fire.Fire(get_k_neighbors)