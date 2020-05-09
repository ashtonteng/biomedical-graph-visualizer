python3 ./queries/get_k_neighbors.py --targets ['Q14905129','Q21123982'] \
                                     --emb_file-path ./embeddings.emb \
                                     --n_neighbors 5 \
                                     --algorithm cosine_similarity \
                                     --save_output True \
                                     --output_path ./nearest_neighbors.json
