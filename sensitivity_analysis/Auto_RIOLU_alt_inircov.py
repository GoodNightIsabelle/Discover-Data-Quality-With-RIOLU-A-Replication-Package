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

def coverage_estimation(source_column, coverage_threshold):
    # Fine tune the coverage threshold
    generator = PatternGenerator(source_column, coverage_threshold)
    generator.pattern_coverage_statictics()
    selector = PatternSelector(generator.pattern_coverage, len(source_column))
    # Whether to accept a new cluster? depends on the frequency
    selector.select_patterns()
    pattern_pool = selector.pattern_pool
    return coverage(pattern_pool, source_column)
    
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
coverage_thresholds = list(np.array(range(85, 100))*0.01)
coverage_thresholds = [0.85, 0.9, 0.95, 0.99]

# Execute 10 times
for _ in range(10):
    # For single run
    single_p, single_r, single_f1 = [], [], []
    for dataset in datasets:
        p_list, r_list, f1_list = [], [], []
        print(dataset)
        path = '../test_anomaly_detection/%s/'%dataset
        dirty_file = path + 'dirty_%s.csv'%dataset
        df_dirty = get_dataframe(dirty_file)
        gt_path  = '../ground_truth_anomaly_detection/gt_%s.csv'%dataset
        gt_df = pd.DataFrame(pd.read_csv(gt_path))
        gt_columns = [column for column in gt_df.columns if column != 'Index']
        # Create the splits
        results = {}
        
        for coverage_threshold in coverage_thresholds:
            print(coverage_threshold)
            for column in gt_columns:
                gt = gt_df[column]
                # Control coverage
                source_column = df_dirty[column]
                filtered_list = [str(source_column[i]) for i in range(len(source_column)) if pd.notna(source_column[i])]
                average_threshold = 0
                rounds = 5
                # Coverage eatimation
                for _ in range(rounds):
                    average_threshold += coverage_estimation(filtered_list, coverage_threshold)
                coverage_threshold = average_threshold/rounds
                
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
            p_list.append(p)
            r_list.append(r)
            f1_list.append(f1)
            # pd.DataFrame(results).to_csv('results/auto_riolu/auto_riolu_%s.csv'%path.split('/')[-2])
        single_p.append(p_list)
        single_r.append(r_list)
        single_f1.append(f1_list)
    # Add to the run set
    precisions.append(single_p)
    recalls.append(single_r)
    f1_scores.append(single_f1)
    
# Average the p and r scores
precisions = np.mean(precisions, axis=0)
recalls = np.mean(recalls, axis=0)
f1_scores = np.mean(f1_scores, axis=0)
print('p: ', precisions)
print('r: ', recalls)
print('f1: ', f1_scores)

# Average f1 score
avg_precisions = np.array(precisions).mean(axis=0)
avg_recalls = np.array(recalls).mean(axis=0)
avg_f1scores = []
for p, r in zip(avg_precisions, avg_recalls):
    if p+r != 0:
        f1 = np.round(2*p*r/(p+r), 3)
    else:
        f1 = '-'
    avg_f1scores.append(f1)

print(f1_scores)
print(avg_f1scores)
# Make a plot of the scores
plt.figure()
for i, f1_score in enumerate(f1_scores):
    plt.plot(coverage_thresholds, f1_score, label=datasets[i])
plt.plot(coverage_thresholds, avg_f1scores, ls='-.', marker='o', label='average f1 score')
plt.xlabel('Initial r_cov')
plt.ylabel('F1 Score')
plt.ylim(0, 1.1)
for i, txt in enumerate(avg_f1scores):
    plt.annotate(txt, (coverage_thresholds[i], avg_f1scores[i]), textcoords="offset points", xytext=(0,8), ha='center')

plt.legend()
plt.show()
