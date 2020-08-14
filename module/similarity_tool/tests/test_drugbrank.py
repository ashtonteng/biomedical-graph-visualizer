import numpy as np
import pandas as pd 
import argparse
import itertools
import tqdm
import os
import sys
sys.path.append(os.getcwd())

from collections import defaultdict
from module.similarity_tool.nearest_neighbors import NearestNeighbors


EMBEDDING_TYPES = ['relation', 'stranse', 'node2vec']
AGGREGATION_METHOD =['majority', 'nearest', 'mean']
DISTANCE_METRIC = ['cos', 'l1', 'l2']


def main(args):

    # parse in drugbrank csv
    df = pd.read_csv(args.drugbank_csv)
    MEDICAL_CONDITIONS = df.MedicalCondition.unique().tolist()

    # define test conditions
    test_conditions = [
        EMBEDDING_TYPES, 
        AGGREGATION_METHOD,
        DISTANCE_METRIC, 
        MEDICAL_CONDITIONS
    ]
    test_cases = list(itertools.product(*test_conditions))

    # results dictionary to be converted to dataframe
    results = defaultdict(list)

    # loop over different test parameters
    for emb_type, agg_meth, dist_metr, med_cond in tqdm.tqdm(test_cases):

        # generate train/test split
        df_cond = df[df.MedicalCondition == med_cond]
        targets = df_cond[df_cond.Split == "Train"].WikidataID.tolist()
        true_neighbors = df_cond[df_cond.Split == "Test"].WikidataID.tolist()

        # choose number of neighbors to retrieve
        if args.num_neighbors is None:
            num_neighbors = len(true_neighbors)
        else:
            num_neighbors = args.num_neighbors

        # skip test condition if no test case exist 
        if num_neighbors == 0:
            continue

        # create nearest neighbor class
        nn = NearestNeighbors(
            targets = targets, 
            #emb_file_path = args.emb_file_path, 
            n_neighbors = num_neighbors, 
            distance_metric = dist_metr, 
            aggregate_method = agg_meth,
            embeddings_type = emb_type,
            exclude_targets = True,
            concept = "Q8386"
        )

        # Get neighbors
        preds = nn.aggregate_neighbors(method = "nearest")

        # Get neighbors only
        pred_neighbors = [p[0] for p in preds["aggregated"]]

        # get sensitivity
        tp = len(set(pred_neighbors) & set(true_neighbors))
        sensitivity = tp / num_neighbors

        # store results
        results["EmbeddingType"].append(emb_type)
        results["AggregationMethod"].append(agg_meth)
        results["DistanceMetric"].append(dist_metr)
        results["MedicalCondition"].append(med_cond)
        results["Sensitivity"].append(sensitivity)
        results["TruePositive"].append(tp)
        results["TotalTest"].append(num_neighbors)

    # save results
    df_results = pd.DataFrame.from_dict(results)
    df_results.to_csv(args.results_file)


if __name__ == "__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument("--drugbank_csv", type=str, default='./DrugBank.csv')
    parser.add_argument("--num_neighbors", type=int, default=None)
    parser.add_argument("--emb_file_path", type=str, default='./embeddings.emb')
    parser.add_argument("--results_file", type=str, default='./drugbank_nn_results.csv')
    args = parser.parse_args()

    main(args)
