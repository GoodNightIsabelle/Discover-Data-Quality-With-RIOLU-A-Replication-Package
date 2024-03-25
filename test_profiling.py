from pattern_summarizer import PatternGenerator
from utils import Utils
import numpy as np
import os
import json
import random
import sys
import matplotlib.pyplot as plt

all_files = []
# Get all the datasets
folder = './test_data_profiling/hetero/'
files = [file_name for file_name in os.listdir(folder) if '.json' in file_name]
all_files = files
datasets = []

# Get the data
for file_name in files:
    with open(folder+file_name, 'r') as file_:
        # Load the JSON data from the file
        data = json.load(file_)
        datasets.append(data['Data'])
        
folder = './test_data_profiling/homo/'
files = [file_name for file_name in os.listdir(folder) if '.json' in file_name]
all_files += files
# Get the data
for file_name in files:
    with open(folder+file_name, 'r') as file_:
        # Load the JSON data from the file
        data = json.load(file_)
        datasets.append(data['Data'])
        
folder = './test_data_profiling/homo.simple/'
files = [file_name for file_name in os.listdir(folder) if '.json' in file_name]
all_files += files
# Get the data
for file_name in files:
    with open(folder+file_name, 'r') as file_:
        # Load the JSON data from the file
        data = json.load(file_)
        datasets.append(data['Data'])
      

# Store the metrics
avg_precision, avg_recall, avg_f1 = 0, 0, 0
avg_fp = 0
test_sizes = 0
tp_list, fp_list = [], []

# Combine datasets and file names into tuples
combined_data = list(zip(datasets, all_files))

# Sort the tuples based on the size of datasets
sorted_combined_data = sorted(combined_data, key=lambda x: len(x[0]))

# Unzip the sorted tuples back into separate datasets and file names
datasets, all_files = zip(*sorted_combined_data)
sizes = [np.log10(len(dataset)) for dataset in datasets]
# Create the splits
pattern_pools = []
test_current = []
for i, dataset in enumerate(datasets):
    # Ignore the datasets that are too small
    tp, fp, fn = 0, 0, 0
    # Control coverage
    generator = PatternGenerator(dataset, 1)
    test_size = generator.test_size
    test_sizes += test_size
    generator.pattern_coverage_statictics()
    pattern_pool = generator.patterns
    print(all_files[i], pattern_pool)
    
    # Test on current dataset
    for data in generator.test:
        matched = False
        for pattern in pattern_pool:
            # Regular expression with positional constraints
            if Utils.pattern_matching(pattern, data):
                tp += 1
                matched = True
                break
        if matched == False:
            fn += 1
    
    # Test on other datasets
    test_set = []
    for j, dataset in enumerate(datasets):
        if i != j:
            test_set.extend(dataset)
    # Randomly select test set
    test_set = random.choices(test_set, k=test_size)
    for data in test_set:
        for pattern in pattern_pool:
            # Regular expression with positional constraints
            if Utils.pattern_matching(pattern, data):
                fp += 1
                break
    avg_fp += fp
            
    if tp+fp != 0:
        precision = tp/(tp+fp)
    else:
        precision = 0
    avg_precision += precision
    if tp+fn != 0:
        recall = tp/(tp+fn)
    else:
        recall = 0
    avg_recall += recall
    if precision+recall == 0:
        f1 = 0
    else:
        f1 = 2*precision*recall/(precision+recall)
    tp_list.append(tp/test_size)
    fp_list.append(fp/test_size)
    print(all_files[i], round(precision, 3), round(recall, 3), round(f1, 3))
    
avg_precision /= len(datasets)
avg_recall /= len(datasets)
avg_f1 = 2*avg_precision*avg_recall/(avg_precision+avg_recall)
print('average precision: %.3f, average recall: %.3f, average f1: %.3f'%(avg_precision, avg_recall, avg_f1))
print('average fp: %.4f'%(avg_fp/test_sizes))

#!/usr/bin/python3
root_dir = os.path.join(os.path.dirname(sys.argv[0]), '..', '..')

f = plt.figure(1, figsize=(15, 5))
p = f.add_subplot(1, 1, 1)
p.tick_params(axis='both', which='major', labelsize=24)
p.set_ylabel('Match Fraction', fontsize=26)
p.set_xlabel('Dataset (Ordered with size, from small to arge)', fontsize=26)

p.fill_between(range(len(tp_list)), tp_list, fp_list,
               facecolor='green', alpha=0.32)
p.fill_between(range(len(tp_list)), fp_list, 0.0,
               facecolor='#880000', alpha=0.96)

p.text(23, 0.45, u"F1 = %0.1f%%" % (avg_f1 * 100),
       color='green', fontweight='bold', fontsize=36)

p.axhline(y=np.mean(tp_list), ls='dashed', lw=3,
          c='green', alpha=0.9, dashes=(4, 4), label="Avg TP")
p.axhline(y=np.mean(fp_list), ls='dotted', lw=3,
          c='red', alpha=0.9, dashes=(1, 3), label="Avg FP")

p.set_yticks(list(p.get_yticks())[2:] + [np.mean(tp_list), np.mean(fp_list)])

p.set_autoscale_on(False)
p.axis([0, 62, 0, 1.005])
p.xaxis.set_ticks(np.arange(0, 62, 5))
ax2 = p.twinx()
ax2.tick_params(axis='both', which='major', labelsize=24)
ax2.spines['right'].set_position(('outward', 0))

# Plot the second data on the second axis
ax2.plot(sizes, lw=3, c='blue', alpha=0.9, dashes=(1, 3), ls='dotted', label='log10(Data Size)')
ax2.set_yticks(list(ax2.get_yticks())[2:]+[min(sizes), max(sizes)])
ax2.set_ylabel('log10(Data Size)', fontsize=26)
ax2.set_autoscale_on(False)

# Show legend
handles, labels = p.get_legend_handles_labels()
handles2, labels2 = ax2.get_legend_handles_labels()
handles.extend(handles2)
labels.extend(labels2)
p.legend(handles, labels, loc='lower right', fontsize=18)

plt.savefig('./profiling_quality.png', bbox_inches='tight', dpi=300)
print('> "Profiling Quality" plot saved to %s' % './plots/profiling_quality.png')
