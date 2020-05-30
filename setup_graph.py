import module.graph_lib.downloader as downloader
from module.graph_lib.constants import *
import module.graph_lib.graph_utils as graph_utils
import argparse

"""
This file produces the static files required for BGV. 
"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--download', action="store_true", help='whether or not to download the graph data files')
    parser.add_argument('--graph', action="store_true", help='whether or not to build and save the graph pickle')
    parser.add_argument('--autocomplete', action="store_true", help='whether or not to generate autocomplete json')
    args = parser.parse_args()

    download = args.download
    graph = args.graph
    autocomplete = args.autocomplete

    if download:
        downloader.download_all_data()

    if graph:
        g = graph_utils.get_graph(replace_pickle=True)  # builds a new graph from local files and saves pickle
        graph_utils.get_pagerank_dict(pickle_path=PAGERANK_DICT_PICKLE_PATH, replace_pickle=True)  # runs pagerank on graph and saves pickle
    else:
        g = graph_utils.get_graph(replace_pickle=False)

    if autocomplete:
        if not os.path.exists(AUTOCOMPLETE_DIR):
            os.mkdir(AUTOCOMPLETE_DIR)
        graph_utils.save_all_node_names_ids_json(g, out_path=os.path.join(AUTOCOMPLETE_DIR, "all_node_names_ids.json"))
        graph_utils.save_all_concept_names_ids_json(out_path=os.path.join(AUTOCOMPLETE_DIR, "all_concept_names_ids.json"))
