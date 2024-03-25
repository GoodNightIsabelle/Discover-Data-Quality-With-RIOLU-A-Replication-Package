from template_generator import TemplateGenerator
from template_selector import TemplateSelector
from utils import Utils
import pandas as pd
import numpy as np

def get_dataframe(path, header=True):
    if header:
        return pd.DataFrame(pd.read_csv(path, dtype=str))
    else:
        return pd.DataFrame(pd.read_csv(path, dtype=str, header=None))

def coverage_estimation(source_column, coverage_threshold):
    # Fine tune the coverage threshold
    generator = TemplateGenerator(source_column, coverage_threshold)
    generator.template_coverage_statictics()
    selector = TemplateSelector(generator.template_coverage, len(source_column))
    # Whether to accept a new cluster? depends on the frequency
    selector.select_templates()
    template_pool = selector.template_pool
    return coverage(template_pool, source_column)
    
def coverage(template_pool, data):
    matched = 0
    for i, record in enumerate(data):
        for template in template_pool:
            # Regular expression with positional constraints
            if Utils.template_matching(template, record):
                matched += 1
                break
    return matched/len(data)


# Get all the datasets
dataset = 'hosp_100k'
path = './test_anomaly_detection/%s/'%dataset
dirty_file = path + 'dirty_%s.csv'%dataset
df_dirty = get_dataframe(dirty_file)

gt_path  = './ground_truth_anomaly_detection/gt_%s.csv'%dataset
gt_df = pd.DataFrame(pd.read_csv(gt_path))
gt_columns = [column for column in gt_df.columns if column != 'Index']

# Create the splits
results = {}
avg_precision, avg_recall = 0, 0
for column in gt_columns:
    gt = gt_df[column]
    # Control coverage
    source_column = df_dirty[column]
    filtered_list = [str(source_column[i]) for i in range(len(source_column)) if pd.notna(source_column[i])]
    average_threshold = 0
    coverage_threshold = 0.95
    rounds = 5
    # Coverage eatimation
    for _ in range(rounds):
        average_threshold += coverage_estimation(filtered_list, coverage_threshold)
    coverage_threshold = average_threshold/rounds
    
    # Coverage update, re-generate
    generator = TemplateGenerator(filtered_list, coverage_threshold)
    generator.template_coverage_statictics()
    selector = TemplateSelector(generator.template_coverage, len(filtered_list))
    # Whether to accept a new cluster? depends on the frequency
    selector.select_templates()
    template_pool = selector.template_pool
    print(column, template_pool)
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
        for template in template_pool:
            # Regular expression with positional constraints
            if Utils.template_matching(template, record):
                matched = True
                predictions.append(0)
                break
        if not matched:
            predictions.append(1)
    results[column] = predictions
# Write the results
pd.DataFrame(results).to_csv('results/auto_riolu/auto_riolu_%s.csv'%path.split('/')[-2])
