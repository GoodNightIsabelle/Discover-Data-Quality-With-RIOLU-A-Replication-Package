import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

class PatternSelector:
    def __init__(self, pattern_coverage, column_size):
        # Get the coverage
        self.column_size = column_size
        self.pattern_coverage = pattern_coverage

        # Store a sorted gain dictionary
        self.sorted_gain = None
        self.pattern_pool = []
        
    def sort_coverage(self):
        # Sort the coverage
        self.sorted_coverage = dict(sorted(self.pattern_coverage.items(), key=lambda item: item[1], reverse=True))

    def select_patterns(self):
        self.sort_coverage()
        coverages = list(self.sorted_coverage.values())
        patterns = list(self.sorted_coverage.keys())
        if len(coverages) > 1:
            coverages.append(1/self.column_size)
            # Reshape the coverages into a 2D array
            X = np.array(coverages).reshape(-1, 1)
            kmeans = KMeans(n_clusters=2, n_init='auto', random_state=0)
            kmeans.fit(X)

            # Get the cluster assignments
            cluster_labels = kmeans.labels_
            
            # Decide the larger cluster label
            label_select = np.argmax(kmeans.cluster_centers_)
            self.pattern_pool = [patterns[i] for i in range(len(patterns)) if cluster_labels[i]==label_select]
        else:
            self.pattern_pool = patterns
