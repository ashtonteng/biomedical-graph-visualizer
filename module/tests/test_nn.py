import random
import numpy as np
import tqdm
import os
import sys
sys.path.append(os.getcwd())
from collections import defaultdict
from test_constants import TEST_CONDITIONS, FDA_TEST_CONDITIONS
from queries.nearest_neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split


def test_nn(
    fda_approved: bool = True, 
    emb_file_path: str = "./embeddings.emb", 
    aggregation_method: str = "mean",
    confidence_interval: float = 0.95,
    num_bootstrap_trials: int = 100,
):
    """Test script for nearest neighbor. 

    Given a list of medical conditions and its known drugs used for treatment, 
    a bootstrap is performed by randomly sampling drug as inputs for nearest 
    neighbors and the remaininly unselected drugs as targets. A sensitivity 
    with confidence interval is used for evaluation metrics

    :param fda_approved (bool): only use fda_approved drugs
    :param emb_file_path (str): path to the node embeddings
    :param aggregation_method (str): aggregation method used for nearest neigbors
    :param confidence_interval (str): the confidence interval to display
    :param num_bootstrap_trial (int): number of bootstrap experiments to run 
    """

    # Reproducibility
    random.seed(6)
    CI = confidence_interval
    NUM_TRIALS = num_bootstrap_trials
    results = {}

    if fda_approved:
        conditions = FDA_TEST_CONDITIONS
    else:
        conditions = TEST_CONDITIONS

    # loop over different medical conditions
    for testcase in conditions:

        sensitivity = []
        
        # Bootstrap
        for _ in tqdm.tqdm(range(NUM_TRIALS)):

            # Boostrap samples        
            if fda_approved:
                drugs = testcase['FDADrugIDs']
            else:
                drugs = testcase['DrugIDs']
            total_medications = len(drugs) 
            num_neighbors = random.randint(1, total_medications -1)

            # split to target and neighbors
            targets, neighbors = train_test_split(drugs, test_size=num_neighbors)

            # Create NN class
            nn = NearestNeighbors(
                targets = targets, 
                emb_file_path = emb_file_path, 
                n_neighbors = len(neighbors), 
                algorithm = "cosine_similarity", 
                exclude_targets = True 
            )

            # Get neighbors
            preds = nn.aggregate_neighbors(method = "nearest")

            # Get neighbors only
            pred_neighbors = [p[0] for p in preds]

            # Metrics
            tp = len(set(pred_neighbors) & set(neighbors))
            fn = len(neighbors) - tp
            tpr = tp / (tp + fn)
            sensitivity.append(tpr)

        # Calculate sensitivity and confidence interval
        sensitivity = np.array(sensitivity)
        mean = sensitivity.mean()
        lower = sensitivity[int(((1 - CI)/2)*NUM_TRIALS)]
        upper = sensitivity[int(((1 + CI)/2)*NUM_TRIALS)]

        print(f"{testcase['Name']} sensitivity = {mean} [{lower}, {upper}] {CI}% CI")

        results[testcase['Name']] = [mean, lower, upper]
    
    return results


if __name__ == "__main__":
    test_nn()