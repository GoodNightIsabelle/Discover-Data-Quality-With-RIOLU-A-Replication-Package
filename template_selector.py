from utils import Utils
import re
import string
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans

class TemplateSelector:
    def __init__(self, template_coverage):
        # Get the coverage
        self.template_coverage = template_coverage

        # Store a sorted gain dictionary
        self.sorted_gain = None
        self.template_pool = []
        
    def sort_coverage(self):
        # Sort the coverage
        self.sorted_coverage = dict(sorted(self.template_coverage.items(), key=lambda item: item[1], reverse=True))

    def select_templates(self):
        self.sort_coverage()
        coverages = list(self.sorted_coverage.values())
        templates = list(self.sorted_coverage.keys())
        if len(coverages) > 1:
            coverages.append(1e-5)
            # Reshape the coverages into a 2D array
            X = np.array(coverages).reshape(-1, 1)
            kmeans = KMeans(n_clusters=2, random_state=0)
            kmeans.fit(X)

            # Get the cluster assignments
            cluster_labels = kmeans.labels_
            
            # Decide the larger cluster label
            label_select = np.argmax(kmeans.cluster_centers_)
            self.template_pool = [templates[i] for i in range(len(templates)) if cluster_labels[i]==label_select]
        else:
            self.template_pool = templates