import argparse
import node2vec
import networkx as nx

def gen_embeddings(args):
    Gnx.read_edgelist(args.graph)
    ndim = args.ndim
    # Precompute probabilities and generate walks - **ON WINDOWS ONLY WORKS WITH workers=1**
    node2vec = Node2Vec(G, dimensions=ndim, walk_length=30, num_walks=200, workers=4)  # Use temp_folder for big graphs
    # Embed nodes
    model = node2vec.fit(window=10, min_count=1, batch_words=4)  
    # Save embeddings for later use
    model.wv.save_word2vec_format(EMBEDDING_FILENAME)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=str, default=None, help="Filename with saved data to plot")
    parser.add_argument("--outfile", type=str, default='embeddings.emb', help="Output file to save embeddings to")
    parser.add_argument("--outdir", type=str, default='.', help="Output path to save emb file to")
    parser.add_argument("--ndim", type=int, default=10, help="Set the embedding dimension")
    args = parser.parse_args()
    gen_embeddings(args)
