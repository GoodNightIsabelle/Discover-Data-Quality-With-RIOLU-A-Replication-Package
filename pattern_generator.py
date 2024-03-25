from utils import Utils
import re
import string
import numpy as np
from sklearn.cluster import KMeans

class PatternGenerator:

    def __init__(self, data, coverage_threshold):
        # Training configurations
        self.coverage_threshold = coverage_threshold
        self.sampling_size = int(np.ceil((1.96**2 * 0.5 * (1-0.5)) / (0.05**2)))
        # Create splits, only consider not nan values
        self.splits, self.indices_train = Utils.split_and_validate(data, self.sampling_size)

        # Get a list of digits and letters
        self.digits = set(str(i) for i in range(10))
        self.upper_letters = set(string.ascii_uppercase)
        self.lower_letters = set(string.ascii_lowercase)

        # Create type mappings and all the combinations
        self.type_mapping = {d:'\\\d' for d in self.digits}
        self.type_mapping.update({l:'[A-Z]' for l in self.upper_letters})
        self.type_mapping.update({l:'[a-z]' for l in self.lower_letters})

        # Template info storage
        self.template_information = {}
        self.patterns = []
        self.pattern_coverage = {}
        
    def information_gathering(self, symbols, column, coverage):
        # Create a new info slot
        self.template_information = {}
        max_length = Utils.symbol_length(symbols, column, coverage)
        for i in range(len(column)):
            (template, token_length_bag, token_char_bag, token_bag) = Utils.token_info(symbols, column[i], max_length)
            # Fit the template
            for token, length in token_length_bag.items():
                token_chars = token_char_bag[token]
                current_token = token_bag[token]
                if template in self.template_information.keys():
                    # If this is a new token
                    if token not in self.template_information[template].keys():
                        self.template_information[template][token] = {'length':{}, 'chars': {}, 'token': {}}
                    # Collect the length count for each position, the number of tokens should be the same
                    if length in self.template_information[template][token]['length'].keys():
                        self.template_information[template][token]['length'][length] += 1
                    else:
                        self.template_information[template][token]['length'][length] = 1
                    # Collect the full token information
                    if current_token in self.template_information[template][token]['token'].keys():
                        self.template_information[template][token]['token'][current_token] += 1
                    else:
                        self.template_information[template][token]['token'][current_token] = 1
                    # Collect the char and type information
                    for j, char in enumerate(token_chars):
                        # Extend the length
                        if 'pos_%d'%j not in self.template_information[template][token]['chars'].keys():
                            self.template_information[template][token]['chars']['pos_%d'%j] = {char:1}
                        else:
                            # Static char check
                            if char not in self.template_information[template][token]['chars']['pos_%d'%j].keys():
                                self.template_information[template][token]['chars']['pos_%d'%j][char] = 1
                            else:
                                self.template_information[template][token]['chars']['pos_%d'%j][char] += 1
                else:
                    # Collect the length count for each position, the number of tokens should be the same
                    self.template_information[template] = {token: {'length': {length:1}, 
                                                                   'chars': {'pos_%d'%j: {c:1} for j, c in enumerate(token_chars)}, 
                                                                   'token': {current_token:1}}}
                                                                   
    
    def pattern_generation(self, symbols, column):
        # Update the template information
        self.information_gathering(symbols, column, self.coverage_threshold)
        for template, token_stats in self.template_information.items():
            composed_template = template
            for _, stats in token_stats.items():
                token_char = ''
                # Check whether the tokens can be categorized
                # Check the number of the bins
                coverages = list([value/sum(stats['token'].values()) for value in stats['token'].values()])
                categories = list(stats['token'].keys())
                if len(coverages) > 1:
                    coverages.append(1)
                    coverages.append(1/len(column))
                    
                    # Reshape the coverages into a 2D array
                    X = np.array(coverages).reshape(-1, 1)
                    # Insert noises
                    kmeans = KMeans(n_clusters=2, random_state=0)
                    kmeans.fit(X)

                    # Get the cluster assignments
                    cluster_labels = kmeans.labels_
                    # Decide the larger cluster label
                    label_select = np.argmax(kmeans.cluster_centers_)
                    categories_selected = [categories[i] for i in range(len(categories)) if cluster_labels[i]==label_select]
                    categories_coverage = sum([coverages[i] for i in range(len(coverages)-2) if cluster_labels[i]==label_select])
                    if categories_coverage >= self.coverage_threshold:
                        token_list = sorted([re.escape(token) for token in categories_selected])
                        if len(token_list) > 1:
                            composed_template = re.sub('TOKEN', '(' + '|'.join(token_list) + ')', composed_template, 1)
                        elif len(token_list) == 1:
                            composed_template = re.sub('TOKEN', token_list[0], composed_template, 1)
                        continue
                else:
                    composed_template = re.sub('TOKEN', re.escape(categories[0]), composed_template, 1)
                    continue
                
                # Length, drop the percentile (coverage)
                filtered = Utils.rank_and_threshold(stats['length'], self.coverage_threshold)
                # The length is fixed if only one key covers the major space
                if len(filtered.keys()) == 1:
                    length_constraint = list(filtered.keys())[0]
                    minimum_constraint = length_constraint
                else:
                    length_constraint = '+'
                    minimum_constraint = min(list(filtered.keys()))
                
                last_type = ''
                type_count = 0
                # Force dump only for no constraint regex
                force_dumped = False
                for pos, char_stats in stats['chars'].items():
                    # Cut the rest if the length is being constrainted
                    if int(pos[4:]) >= minimum_constraint:
                        if length_constraint != '+':
                            break
                        # Force dump
                        elif not force_dumped:
                            if last_type != '':
                                token_char += '%s{%d}'%(last_type, type_count)
                                last_type = ''
                                force_dumped = True
                    filtered = Utils.rank_and_threshold(char_stats, self.coverage_threshold)

                    # Static char check
                    # Check the number of the bins
                    coverages = list([value/sum(char_stats.values()) for value in char_stats.values()])
                    chars = list(char_stats.keys())
                    # Insert noises
                    coverages.append(1)
                    coverages.append(1/len(column))
                    # Reshape the coverages into a 2D array
                    X = np.array(coverages).reshape(-1, 1)
                    kmeans = KMeans(n_clusters=2, random_state=0)
                    kmeans.fit(X)

                    # Get the cluster assignments
                    cluster_labels = kmeans.labels_
                    # Decide the larger cluster label
                    label_select = np.argmax(kmeans.cluster_centers_)
                    chars_selected = [chars[i] for i in range(len(chars)) if cluster_labels[i]==label_select]
                    chars_coverage = sum([coverages[i] for i in range(len(chars)) if cluster_labels[i]==label_select])
                    if chars_coverage >= self.coverage_threshold:
                        # Dump the last?
                        if last_type != '':
                            token_char += '%s{%d}'%(last_type, type_count)
                        char_list = sorted([re.escape(token) for token in chars_selected])
                        if len(char_list) > 1:
                            token_char += '(' + '|'.join(char_list) + ')'
                        elif len(char_list) == 1:
                            token_char += char_list[0]
                        last_type = ''
                    # Static type check
                    else:
                        # Check whether the keys belongs to a certain type
                        mapped = np.unique([self.type_mapping[key] for key in filtered.keys()])
                        if len(mapped) == 1:
                            # Check whether current type belongs to the last
                            if mapped[0] == last_type:
                                type_count += 1
                            else:
                                if last_type != '':
                                    # If longer than length constraint then add an "*"
                                    if int(pos[4:]) > minimum_constraint:
                                        token_char += '%s*'%(last_type)
                                    else:
                                        token_char += '%s{%d}'%(last_type, type_count)
                                last_type = mapped[0]
                                type_count = 1

                        # Multiple types, no symbol
                        elif all(m for m in mapped if m not in symbols):
                            # Construct the current type
                            current_type = '['
                            for item in sorted(mapped):
                                if item == '\\\d':
                                    current_type += '0-9'
                                elif item == '[a-z]':
                                    current_type += 'a-z'
                                else:
                                    current_type += 'A-Z'
                            current_type += ']'
                            # Check whether current type belongs to the last
                            if current_type == last_type:
                                type_count += 1
                            else:
                                if last_type != '':
                                    # If longer than length constraint then add an "*"
                                    if int(pos[4:]) > minimum_constraint:
                                        token_char += '%s*'%(last_type)
                                    else:
                                        token_char += '%s{%d}'%(last_type, type_count)
                                last_type = current_type
                                type_count = 1

                        else:
                            # No constraint on type
                            if '.' == last_type:
                                type_count += 1
                            else:
                                if last_type != '':
                                    # If longer than length constraint then add an "*"
                                    if int(pos[4:]) > minimum_constraint:
                                        token_char += '%s*'%(last_type)
                                    else:
                                        token_char += '%s{%d}'%(last_type, type_count)
                                    
                                last_type = '.'
                                type_count = 1

                # Dump the last?
                if last_type != '':
                    # If longer than length constraint then add an "*"\
                    if force_dumped:
                        token_char += '%s*'%(last_type)
                    else:
                        token_char += '%s{%d}'%(last_type, type_count)
                composed_template = re.sub('TOKEN', r'%s'%token_char, composed_template, 1)
            self.patterns.append(composed_template)

    def pattern_coverage_statictics(self):
        # Structure: template-fold-(coverage& impurity)
        (train_data, test_data) = self.splits
        # Get the Bag-of-Characters summary for the list of texts
        boc_summary = Utils.bag_of_characters_summary(train_data)
        
        # Get special symbols
        symbols = set(item for item in boc_summary.keys() if (item not in self.digits and item not in self.upper_letters and item not in self.lower_letters))
        self.type_mapping.update({l:'[a-z]' for l in symbols})
        
        # Get templates
        self.pattern_generation(symbols, train_data)
        for template in self.patterns:
            # Create a new dict for the template
            if template not in self.pattern_coverage.keys():
                self.pattern_coverage[template] = {}
            # Regular expression with positional constraints
            pattern = re.compile(template)
            # Test the coverage on the training set and the testing set
            cov_train = len(Utils.find_exact_match_elements(pattern, train_data))
            cov_test = len(Utils.find_exact_match_elements(pattern, test_data))
            cov_whole = (cov_train+cov_test)/(len(train_data)+len(test_data))
            
            self.pattern_coverage[template] = cov_whole