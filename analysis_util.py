
import seaborn as sns
import pandas as pd
import numpy as np

def get_chunk_composition_boxplot(data, patterns, variable, variable_text, axis):
    boxplot_data = []
    for pattern in patterns:
        df_pattern = get_chunk_composition_pattern_data(pattern, data)
        for index, row in df_pattern.iterrows():
            boxplot_data.append([row[variable], pattern, row['partial_order']])
    
    boxplot_data = pd.DataFrame(boxplot_data, columns=[variable, 'group', 'partial_order'])
    sns.boxplot(x="group", y=variable, hue='partial_order', data=boxplot_data, showfliers = False, ax = axis).set(
    xlabel='Resolution pattern', ylabel=variable_text)

def get_strategies_plot_data(df, v1_only, v2_only, v1v2, v2v1, start, end, step, last_delta, variable):
    data = []
    for delta in range(start, end, step):
        df_delta = df[(df[variable] > last_delta) & (df[variable] <= delta)]
        if len(df_delta) > 0:
            v1_c = v1_only[(v1_only[variable] > last_delta) & (v1_only[variable] <= delta)]
            v2_c = v2_only[(v2_only[variable] > last_delta) & (v2_only[variable] <= delta)]
            v1v2_c = v1v2[(v1v2[variable] > last_delta) & (v1v2[variable] <= delta)]
            v2v1_c = v2v1[(v2v1[variable] > last_delta) & (v2v1[variable] <= delta)]
            others_c = len(df_delta) - len(v1_c) - len(v2_c) - len(v1v2_c) - len(v2v1_c)
            v1_p = len(v1_c)/len(df_delta)
            v2_p = len(v2_c)/len(df_delta)
            v1v2_p = len(v1v2_c)/len(df_delta)
            v2v1_p = len(v2v1_c)/len(df_delta)
            others_p = others_c / len(df_delta)
            data.append([delta, v1_p, v2_p, v1v2_p, v2v1_p, others_p])
        last_delta = delta
    return data

def get_strategies_plot_df(df, v1_only, v2_only, v1v2, v2v1, variable):
    delta_max = int(df[variable].max())
    delta_min = int(df[variable].min())
    data = []
    data.extend(get_strategies_plot_data(df, v1_only, v2_only, v1v2, v2v1, delta_min, 0, 4, delta_min-1, variable))
    data.extend(get_strategies_plot_data(df, v1_only, v2_only, v1v2, v2v1, 0, 1, 1, -1, variable))
    data.extend(get_strategies_plot_data(df, v1_only, v2_only, v1v2, v2v1, 1, delta_max, 4, 0, variable))
        
    return pd.DataFrame(data, columns=['delta', 'v1', 'v2', 'v1v2', 'v2v1', 'others'])

def get_chunk_composition_pattern_data(pattern, data):
    return data[data['chunk_composition'] == f' {pattern}']

def get_normalized_composition_percentage_data(df):
    v1_data = []
    v2_data = []
    last_i = 0
    for i in np.arange(0.1, 0.6, 0.1):
        i = round(i, 1)
        last_i = round(last_i, 1)
        range = f'({last_i}, {i}]'
        v1_count = len(df[(df['normalized_v1_percentage'] >= last_i) & (df['normalized_v1_percentage'] < i)])
        v2_count = len(df[(df['normalized_v2_percentage'] >= last_i) & (df['normalized_v2_percentage'] < i)])
        v1_data.append([v1_count, range])
        v2_data.append([v2_count, range])
        last_i = i
        # print(range)

    v1_data.append([len(df[df['normalized_v1_percentage'] == 0.5]), '0.5'])
    v2_data.append([len(df[df['normalized_v2_percentage'] == 0.5]), '0.5'])
    # print('0.5')
    

    for i in np.arange(0.6, 1.01, 0.1):
        i = round(i, 1)
        last_i = round(last_i, 1)
        range = f'({last_i}, {i}]'
        # filter_start = (df['normalized_v1_percentage']>=int(last_i))
        # filter_end = (df['normalized_v1_percentage'] < int(i))
        v1_count = len(df[(df['normalized_v1_percentage'] > last_i) & (df['normalized_v1_percentage'] <= i)])
        v2_count = len(df[(df['normalized_v2_percentage'] > last_i) & (df['normalized_v2_percentage'] <= i)])
        v1_data.append([v1_count, range])
        v2_data.append([v2_count, range])
        last_i = i
        # print(range)
    
    return v1_data, v2_data

def print_missing_lines(chunk_side, resolution):
    resolution = resolution.copy()
    for line in chunk_side:
        if line not in resolution:
            print(line)
        else:
            resolution.remove(line)