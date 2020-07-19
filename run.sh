#!/bin/sh
DATA_DIR="/data4/blanca/data/wikidata-bmi/"
# Location of the STransE executable relative to the runpath of this script
STRANSE="../STransE/STransE"

# First, remove stale files
rm ./module/graph_lib/download/*.tsv
rm ./module/graph_lib/download/BGV_Graph.pkl

# Download the graph
python3 ./setup_graph.py --download --autocomplete


python3 ./module/similarity_tool/preprocessing.py \
	--pkl /home/blanca/biomedical-graph-visualizer/module/graph_lib/download/BGV_Graph.pkl

# Go to STransE directory (sibling of this repo) and run
# STransE must already be built from src in order for this to run properly
# TODO: Add STransE 
 $STRANSE -model 1 -data $DATA_DIR -size 50 -margin 5 -l1 1 -lrate 0.0005 -init 0

# python3 ./queries/nearest_neighbors.py --targets "['Q191924', 'Q179452']" \
#                                      --emb_file-path ./ent_emb.json \
#                                      --n_neighbors 5 \
#                                      --distance_metric cos\
#                                      --aggregate_method nearest\
#                                      get_neighbors
