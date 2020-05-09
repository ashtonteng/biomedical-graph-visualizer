import argparse
import node2vec
import networkx as nx

from node2vec import Node2Vec

def gen_embeddings(
        G,
        ndim=10,
        window=10,
        min_count=1,
        batch_words=4,
        savepath='./embeddings.emb',
        walk_length=30,
        num_walks=200,
        workers=4
    ):
    # Precompute probabilities and generate walks
    node2vec = Node2Vec(G, dimensions=ndim, walk_length=walk_length, num_walks=num_walks, workers=workers)
    # Embed nodes
    model = node2vec.fit(window=window, min_count=min_count, batch_words=batch_words)
    # Save embeddings for later use
    model.wv.save_word2vec_format(savepath)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=str, default=None, help="Filename with saved data to plot")
    parser.add_argument("--outfile", type=str, default='embeddings.emb', help="Output file to save embeddings to")
    parser.add_argument("--outdir", type=str, default='.', help="Output path to save emb file to")
    parser.add_argument("--ndim", type=int, default=10, help="Set the embedding dimension")
    parser.add_argument("--window", type=int, default=10, help="node2vec window size")
    parser.add_argument("--min_count", type=int, default=1, help="node2vec fit min count")
    parser.add_argument("--batch_words", type=int, default=4, help="node2vec fit batch words")
    parser.add_argument("--walk_length", type=int, default=30)
    parser.add_argument("--num_walks", type=int, default=200)
    parser.add_argument("--num_workers", type=int, default=4)
    args = parser.parse_args()
    
    # Load graph for fitting embeddings
    G = nx.read_edgelist(args.graph)
    gen_embeddings(
        graph,
        args.ndim, args.window, args.min_count, args.batch_words, args.outfile, args.walk_length, args.num_walks, args.workers)
