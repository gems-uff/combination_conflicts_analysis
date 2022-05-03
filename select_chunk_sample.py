from functools import partial
import pandas as pd
import numpy as np
from scipy import stats
'''
    Randomly selects a sample of 30 chunks that violate the partial order in the resolution
        Excludes outliers (chunk_size and resolution_size) from the selection pool
'''

def drop_outliers(data, column):
    return data[(np.abs(stats.zscore(data[column])) < 3)]

partial_order_result = pd.read_csv('data/partial_order_result_new.csv')
violates_partial_order = partial_order_result[partial_order_result['partial_order'] == 'False']

violates_partial_order = drop_outliers(violates_partial_order, 'chunk_size')
violates_partial_order = drop_outliers(violates_partial_order, 'resolution_size')

malformed_chunks = pd.read_csv('data/malformed_chunks.csv')
malformed_chunks = malformed_chunks['chunk_id'].unique()
print(f'Removing {len(malformed_chunks)} malformed chunks')
violates_partial_order = violates_partial_order[~violates_partial_order['chunk_id'].isin(malformed_chunks)]

sample = violates_partial_order.sample(30, random_state = 42)
sample.to_csv('data/violate_partial_order_sample.csv', index=False)