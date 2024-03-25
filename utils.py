from collections import Counter
import numpy as np
import re

class Utils:
    
    def split_and_validate(data_list, num_samples):
        # Perform sampling
        samples = np.random.choice(range(len(data_list)), size=num_samples, replace=False)

        # Create a list to store the folds
        train_data = [data_list[j] for j in samples]
        test_data = [data_list[j] for j in range(len(data_list)) if j not in samples]

        return (train_data, test_data), samples
    
    # Summarize characters
    def bag_of_characters_summary(texts):
        # Initialize an empty Counter to store character frequencies
        total_character_counts = Counter()

        # Iterate over each text in the list
        for text in texts:
            # Tokenization: Convert the text into a list of characters
            characters = list(text)

            # Counting: Update the Counter with the character frequencies
            total_character_counts.update(characters)

        # Return the summary as a dictionary
        return dict(total_character_counts)
    
    # Get the maximum length of a symbol
    def symbol_length(symbols, column, coverage):
        symbol_dict = {}
        maximum_length = 0
        column_size = len(column)
        for data in column:
            # Append by position
            pos = 0
            for char in data:
                if char not in symbols:
                    continue
                if pos not in symbol_dict.keys():
                    symbol_dict[pos] = {char:1}
                else:
                    if char not in symbol_dict[pos].keys():
                        symbol_dict[pos][char] = 1
                    else:
                        symbol_dict[pos][char] += 1
                pos += 1
        # Cut the redundent symbols
        for pos, symbols in symbol_dict.items():
            # Stop generating when the coverage is reached
            if sum(symbols.values()) < column_size*(1-coverage):
                maximum_length = pos
                break
            maximum_length = pos
            
        return maximum_length
    
    # Return tokenized tempate with info of a single data record
    def token_info(symbols, data, max_length): 
        # The template is a general idea... Only contains token and symbols
        template = ''
        last_token = ''
        # The token length bag count the length of tokens on each position
        token_length_bag = {}
        # The token char bag indicates the character count on each position of each token
        token_char_bag = {}
        token_bag = {}
        # Go through the record to collect the tokens
        # This will count the token order
        token_count = 0
        symbols_count = 0
        token = ''
        for char in data:
            # Collect the full token
            if char in symbols and symbols_count <= max_length:
                symbols_count += 1
                template += re.escape(char)
                # Not a token anymore... Push the token info if we have any
                if token_count > 0 and last_token != '':
                    token_length_bag['token_%d'%token_count] = token_length
                    token_char_bag['token_%d'%token_count] = token_char
                    token_bag['token_%d'%token_count] = token
                    token = ''
                last_token = ''
            else:
                token += char
                if last_token == '':
                    template += 'TOKEN'
                    last_token = 'TOKEN'
                    # We have another token now
                    token_count += 1
                    # And we should start counting the token length
                    token_length = 1
                    # Also, let's collect the characters
                    token_char = [char]
                # continue counting the token itself
                else:
                    token_length += 1
                    token_char.append(char)
        # Dump the things that are not dumped
        if last_token != '':
            token_length_bag['token_%d'%token_count] = token_length
            token_char_bag['token_%d'%token_count] = token_char
            token_bag['token_%d'%token_count] = token
                
        return (template, token_length_bag, token_char_bag, token_bag)
    
    def rank_and_threshold(dictionary, threshold_percentage, return_sum=False):
        # Sort the dictionary items based on values in descending order
        sorted_items = sorted(dictionary.items(), key=lambda x: x[1], reverse=True)

        # Calculate the total sum of values
        total_sum = sum(value for key, value in sorted_items)

        # Calculate the threshold sum based on the specified percentage
        threshold_sum = threshold_percentage * total_sum

        # Initialize variables for tracking the sum and the selected items
        current_sum = 0
        selected_items = []

        # Iterate through the sorted items until the threshold is reached
        for key, value in sorted_items:
            current_sum += value
            selected_items.append((key, value))

            # Check if the threshold is reached
            if current_sum >= threshold_sum:
                break

        # Create a new dictionary with the selected items
        result_dict = dict(selected_items)

        if return_sum:
            return result_dict, current_sum/total_sum
        else:
            return result_dict
    
    # Template matching for single record
    def pattern_matching(pattern, string):
        pattern = re.compile(pattern)
        return re.fullmatch(pattern, string)

    # Template matching for a list
    def find_exact_match_elements(template, string_list):
        # Compile the regular expression pattern
        pattern = re.compile(template)
        # Use list comprehension to find exact matches
        exact_matches = [element for element in string_list if re.fullmatch(pattern, element)]
        return exact_matches
