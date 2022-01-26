from functools import partial
import pandas as pd
import numpy as np
from scipy import stats
'''
    Randomly selects a sample of 100 chunks that violate the partial order in the resolution
        Excludes outliers (chunk_size and resolution_size) from the selection pool
'''

def drop_outliers(data, column):
    return data[(np.abs(stats.zscore(data[column])) < 3)]

partial_order_result = pd.read_csv('data/partial_order_result.csv')
violates_partial_order = partial_order_result[partial_order_result['violates_partial_order'] == True]

violates_partial_order = drop_outliers(violates_partial_order, 'chunk_size')
violates_partial_order = drop_outliers(violates_partial_order, 'resolution_size')

sample = violates_partial_order.sample(100, random_state = 42)
sample.to_csv('data/violate_partial_order_sample.csv', index=False)