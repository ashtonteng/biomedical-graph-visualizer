python3 ./queries/nearest_neighbors.py --targets "['Q191924', 'Q179452']" \
                                     --emb_file-path ./ent_emb.json \
                                     --n_neighbors 5 \
                                     --distance_metric cos\
                                     --aggregate_method nearest\
                                     get_neighbors
