#!/bin/sh
DATA_DIR="/data4/blanca/data/wikidata-bmi/"
# Location of the STransE executable relative to the runpath of this script
STRANSE="../STransE/STransE"
REL_DATA_DIR="/data4/blanca/data/wikidata-bmi/relation/"
OUT_DIR="/data4/blanca/checkpoints/wikidata-bmi/out/"
RELATION_PREDICTION="../relationPrediction/main.py"

# First, remove stale files
rm ./module/graph_lib/download/*.tsv
rm ./module/graph_lib/download/BGV_Graph.pkl

# Download the graph
python3 ./setup_graph.py --download --autocomplete


python3 ./module/similarity_tool/preprocessing.py \
	--pkl /home/blanca/biomedical-graph-visualizer/module/graph_lib/download/BGV_Graph.pkl

# Go to STransE directory (sibling of this repo) and run
# STransE must already be built from src in order for this to run properly
$STRANSE -model 1 -data $DATA_DIR -size 50 -margin 5 -l1 1 -lrate 0.0005 -init 0

# Run relation embedding train script
python $RELATION_PREDICTION --data $REL_DATA_DIR --get_2hop True --partial_2hop True --margin 1 --epochs_gat 1000 --epochs_conv 100 --weight_decay_gat 0.00001 --out_channels 50 --drop_conv 0.3 --output_folder $OUT_DIR --entity_out_dim 25 50
