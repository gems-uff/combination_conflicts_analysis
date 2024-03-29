
import seaborn as sns
import pandas as pd
import numpy as np

# data_folder = "/Users/heleno/Documents/data"
data_folder = "C:\\Users\\HelenoCampos\\Documents\\data"

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
    data.extend(get_strategies_plot_data(df, v1_only, v2_only, v1v2, v2v1, delta_min, -10, 15, delta_min-1, variable))
    data.extend(get_strategies_plot_data(df, v1_only, v2_only, v1v2, v2v1, -10, 10, 1, -1, variable))
    data.extend(get_strategies_plot_data(df, v1_only, v2_only, v1v2, v2v1, 10, delta_max, 15, 0, variable))
        
    df = pd.DataFrame(data, columns=['delta', 'v1', 'v2', 'v1v2', 'v2v1', 'others'])
    df['v1'] = df['v1'] * 100
    df['v2'] = df['v2'] * 100
    df['v1v2'] = df['v1v2'] * 100
    df['v2v1'] = df['v2v1'] * 100
    df['others'] = df['others'] * 100
    return df

def get_strategies_plot_data2(df, v1_only, v2_only, v1v2, v2v1, delta_values, last_delta, variable):
    data = []
    # last_delta = delta_values[0] - 1
    for delta in delta_values:
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

def get_delta_percentages(df_delta, v1_only, v2_only, v1v2, v2v1, variable, start, end):
    if len(df_delta) > 0:
        # print(f'> {start} and <= {end}') # uncomment here to show the bins
        v1_c = v1_only[(v1_only[variable] > start) & (v1_only[variable] <= end)]
        v2_c = v2_only[(v2_only[variable] > start) & (v2_only[variable] <= end)]
        v1v2_c = v1v2[(v1v2[variable] > start) & (v1v2[variable] <= end)]
        v2v1_c = v2v1[(v2v1[variable] > start) & (v2v1[variable] <= end)]
        others_c = len(df_delta) - len(v1_c) - len(v2_c) - len(v1v2_c) - len(v2v1_c)
        v1_p = len(v1_c)/len(df_delta)
        v2_p = len(v2_c)/len(df_delta)
        v1v2_p = len(v1v2_c)/len(df_delta)
        v2v1_p = len(v2v1_c)/len(df_delta)
        others_p = others_c / len(df_delta)
        return [end, v1_p, v2_p, v1v2_p, v2v1_p, others_p]

'''
    This is the version we are using in the SBES paper
'''
def get_strategies_plot_df2(df, v1_only, v2_only, v1v2, v2v1, variable):
    delta_max = int(df[variable].max())
    delta_min = int(df[variable].min()) - 1
    bin_size = 50
    range_max = 350 
    
    negative_values = [-x for x in range(10, range_max + 1, bin_size)]
    positive_values = [x for x in range(10, range_max + 1, bin_size)]
    negative_values = negative_values[::-1]
    middle_values = [x for x in range(-9, 10)]
    delta_values = negative_values[1:] + middle_values + positive_values[:-1]
    data = []
    # first delta includes the range from delta_min to the first delta
    range_start = delta_min
    range_end = negative_values[0]
    df_delta = df[(df[variable] > range_start) & (df[variable] <= range_end)]
    data.append(get_delta_percentages(df_delta, v1_only, v2_only, v1v2, v2v1, variable, range_start, range_end))

    range_start = range_end
    for delta in delta_values:
        range_end = delta
        df_delta = df[(df[variable] > range_start) & (df[variable] <= range_end)]
        if len(df_delta) > 0:
            data.append(get_delta_percentages(df_delta, v1_only, v2_only, v1v2, v2v1, variable, range_start, range_end))
        range_start = range_end
        
    # last delta includes the range from delta_max to the actual last delta
    range_start = positive_values[-1] - 1
    range_end = delta_max
    df_delta = df[(df[variable] > range_start) & (df[variable] <= range_end)]
    data.append(get_delta_percentages(df_delta, v1_only, v2_only, v1v2, v2v1, variable, range_start, range_end))

    df = pd.DataFrame(data, columns=['delta', 'v1 only', 'v2 only', 'v1v2', 'v2v1', 'others'])
    df['v1 only'] = df['v1 only'] * 100
    df['v2 only'] = df['v2 only'] * 100
    df['v1v2'] = df['v1v2'] * 100
    df['v2v1'] = df['v2v1'] * 100
    df['others'] = df['others'] * 100
    return df[['delta', 'v1 only', 'v1v2', 'others', 'v2v1', 'v2 only']]

def get_strategies_plot_bins_percentages(df, v1_only, v2_only, v1v2, v2v1, variable):
    delta_max = int(df[variable].max())
    delta_min = int(df[variable].min()) - 1
    bin_size = 50
    range_max = 350 
    
    negative_values = [-x for x in range(10, range_max + 1, bin_size)]
    negative_values = negative_values[1:]
    negative_values = negative_values[::-1]
    positive_values = [x for x in range(10, range_max + 1, bin_size)]
    positive_values = positive_values[1:]
    middle_values = [x for x in range(-10, 11)]
    delta_values = negative_values[1:] + middle_values + positive_values[:-1]
    percentages = []
    # first delta includes the range from delta_min to the first delta
    range_start = delta_min
    range_end = negative_values[0]
    df_delta = df[(df[variable] > range_start) & (df[variable] <= range_end)]
    percentage = round((len(df_delta)/len(df))*100,2)
    percentages.append([range_end, percentage])

    range_start = range_end
    for delta in delta_values:
        range_end = delta
        df_delta = df[(df[variable] > range_start) & (df[variable] <= range_end)]
        if len(df_delta) > 0:
            percentage = round((len(df_delta)/len(df))*100,2)
            percentages.append([range_end, percentage])
        range_start = range_end
        
    # last delta includes the range from delta_max to the actual last delta
    range_start = positive_values[-1] - 1
    range_end = delta_max
    df_delta = df[(df[variable] > range_start) & (df[variable] <= range_end)]
    percentage = round((len(df_delta)/len(df))*100,2)
    percentages.append([range_end, percentage])

    df = pd.DataFrame(percentages, columns=['delta', 'percentage'])

    return df

def get_chunk_composition_pattern_data(pattern, data):
    patterns = [' v1', ' v2', ' v1 v2', ' v2 v1']
    if pattern == 'Others':
        return data[~data['chunk_composition'].isin(patterns)]
    return data[data['chunk_composition'] == f' {pattern}']

def get_normalized_composition_percentage_data(df):
    v1_data = []
    v2_data = []
    last_i = 0
    for i in np.arange(0.1, 0.6, 0.1):
        i = round(i, 1)
        last_i = round(last_i, 1)
        # range = f'$\geq${int(last_i*100)}%,$<${int(i*100)}%'
        range = f'[{int(last_i*100)}%, {int(i*100)}%)'
        v1_count = len(df[(df['normalized_v1_percentage'] >= last_i) & (df['normalized_v1_percentage'] < i)])
        v2_count = len(df[(df['normalized_v2_percentage'] >= last_i) & (df['normalized_v2_percentage'] < i)])
        v1_data.append([v1_count, range])
        v2_data.append([v2_count, range])
        last_i = i
        # print(range)

    v1_data.append([len(df[df['normalized_v1_percentage'] == 0.5]), '50%'])
    v2_data.append([len(df[df['normalized_v2_percentage'] == 0.5]), '50%'])
    # print('0.5')
    

    for i in np.arange(0.6, 1.01, 0.1):
        i = round(i, 1)
        last_i = round(last_i, 1)
        # range = f'$>${int(last_i*100)}%,$\leq${int(i*100)}%'
        range = f'({int(last_i*100)}%, {int(i*100)}%]'
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

'''
    Returns a DataFrame containing our chunks dataset with all collected data
    10,726 chunks resolved with combination
    Removes 549 chunks that belong to projects that are implicit forks (potentially duplicated)
    Total valid chunks: 10,177 
'''
def get_chunks_dataset():
    df = pd.read_csv(f'{data_folder}/chunks_info.csv')
    df2 = pd.read_csv(f'{data_folder}/partial_order_result.csv')
    df = pd.merge(df, df2, on = ['chunk_id'])
    df2 = pd.read_csv(f'{data_folder}/resolution_composition.csv')
    df = pd.merge(df, df2, on=['chunk_id'])
    df['chunk_size'] = df['v1_size'] + df['v2_size']
    print('All chunks: ', len(df))
    df = filter_implicit_forks(df)
    print('Valid chunks: ', len(df))
    return df


'''
    Filter chunks from projects that are implicit forks
'''
def filter_implicit_forks(complete_dataset):
    intersection = pd.read_csv(f'{data_folder}/projects_intersection.csv') # borrowed from another study
    all_chunks = pd.read_csv(f'{data_folder}/all_chunks_ghiotto.csv')
    df = all_chunks[all_chunks['chunk_id'].isin(list(complete_dataset['chunk_id']))]
    selected_projects = df['project'].unique()
    print('Total projects: ', len(selected_projects))
    projects_that_intersect = intersection[intersection['intersection_perc'] > 0]
    filtered_projects = set()
    for index, row in projects_that_intersect.iterrows():
        filtered_projects.add(row['project1'])
        filtered_projects.add(row['project2'])
    filtered_projects.remove('android/platform_frameworks_base') # we keep the biggest of the projects that intersect
    print(f'Filtered {len(filtered_projects)} of {len(selected_projects)} projects for being implicit forks: {filtered_projects}')
    selected_projects = set(selected_projects)
    selected_projects = selected_projects - filtered_projects
    print('Total valid projects: ', len(selected_projects))
    df_without_forks = df[df['project'].isin(selected_projects)]
    df_without_forks = complete_dataset[complete_dataset['chunk_id'].isin(df_without_forks['chunk_id'])]
    return df_without_forks