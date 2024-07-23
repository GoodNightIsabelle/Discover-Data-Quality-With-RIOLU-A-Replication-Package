import sys
sys.path.append('../.')
from pattern_generator import PatternGenerator
from pattern_selector import PatternSelector
from utils import Utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def get_dataframe(path, header=True):
    if header:
        return pd.DataFrame(pd.read_csv(path, dtype=str))
    else:
        return pd.DataFrame(pd.read_csv(path, dtype=str, header=None))

    
def coverage(pattern_pool, data):
    matched = 0
    for i, record in enumerate(data):
        for pattern in pattern_pool:
            # Regular expression with positional constraints
            if Utils.pattern_matching(pattern, record):
                matched += 1
                break
    return matched/len(data)


# Get all the datasets
datasets = ['flights', 'hosp_1k', 'hosp_10k', 'hosp_100k', 'movies']
precisions, recalls, f1_scores = [], [], []
for _ in range(1):
    # For single run
    single_p, single_r, single_f1 = [], [], []
    for dataset in datasets:
        print(dataset)
        path = '../test_anomaly_detection/%s/'%dataset
        dirty_file = path + 'dirty_%s.csv'%dataset
        df_dirty = get_dataframe(dirty_file)
        gt_path  = '../ground_truth_anomaly_detection/gt_%s.csv'%dataset
        gt_df = pd.DataFrame(pd.read_csv(gt_path))
        gt_columns = [column for column in gt_df.columns if column != 'Index']
        # Create the splits
        results = {}
        
        # Time calculation
        for column in gt_columns:
            gt = gt_df[column]
            # Control coverage
            source_column = df_dirty[column]
            filtered_list = [str(source_column[i]) for i in range(len(source_column)) if pd.notna(source_column[i])]
            # Coverage eatimation
            coverage_threshold = 0.95
            
            # Coverage update, re-generate
            generator = PatternGenerator(filtered_list, coverage_threshold)
            generator.pattern_coverage_statictics()
            selector = PatternSelector(generator.pattern_coverage, len(filtered_list))
            # Whether to accept a new cluster? depends on the frequency
            selector.select_patterns()
            pattern_pool = selector.pattern_pool
            # Report the potential pattern problems
            predictions = []
            for i, record in enumerate(source_column):
                # Skip the empty ones
                if type(record) == float:
                    if np.isnan(record):
                        predictions.append(-1)
                        continue
                record = str(record)
                matched = False 
                for pattern in pattern_pool:
                    # Regular expression with positional constraints
                    if Utils.pattern_matching(pattern, record):
                        matched = True
                        predictions.append(0)
                        break
                if not matched:
                    predictions.append(1)
            results[column] = predictions
        
        # Calculate the r, p, f1
        avg_precision, avg_recall = 0, 0
        for column in gt_columns:
            pred = results[column]
            gt = gt_df[column]
            # Save the data
            tp = 0
            fp = 0
            fn = 0
            total = 0
            for i in range(len(pred)):
                # Skip the empty data
                if pred[i] == -1:
                    continue
                if pred[i] == 1 and gt[i] == 1:
                    tp += 1
                elif pred[i] == 1 and gt[i] == 0:
                    fp += 1
                elif pred[i] == 0 and gt[i] == 1:
                    fn += 1
            if tp+fp != 0:
                avg_precision += tp/(tp+fp)
            if tp+fn != 0:
                avg_recall += tp/(tp+fn)
        p = avg_precision/len(gt_columns)
        r = avg_recall/len(gt_columns)
        if p+r != 0:
            f1 = np.round(2*p*r/(p+r), 3)
        else:
            f1 = '-'
        # Write the results
        print('precision: %.3f; recall: %.3f; f1-score: %.3f'% (p, r, f1))
        # Store the precision and recall
        single_p.append(p)
        single_r.append(r)
        single_f1.append(f1)
        # pd.DataFrame(results).to_csv('results/auto_riolu/auto_riolu_%s.csv'%path.split('/')[-2])
    # Add to the run set
    precisions.append(single_p)
    recalls.append(single_r)
    f1_scores.append(single_f1)
    
# Average the p and r scores
precisions = np.mean(precisions, axis=0)
recalls = np.mean(recalls, axis=0)
print('p: ', precisions)
print('r: ', recalls)
avg_f1scores = []
for p, r in zip(precisions, recalls):
    if p+r != 0:
        f1 = np.round(2*p*r/(p+r), 3)
    else:
        f1 = '-'
    avg_f1scores.append(f1)
print('f1: ', avg_f1scores)
