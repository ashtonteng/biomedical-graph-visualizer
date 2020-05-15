# test on ADHD medications
python3 ./queries/nearest_neighbors.py --targets ['Q191924','Q1706418','Q179452','Q1706418','Q2506823'] \
                                     --emb_file-path ./embeddings.emb \
                                     --n_neighbors 5 \
                                     --algorithm cosine_similarity \
                                     save_neighbors
