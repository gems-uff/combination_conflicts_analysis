
import seaborn as sns
import pandas as pd

def get_chunk_composition_boxplot(data, patterns, variable, variable_text, axis):
    boxplot_data = []
    for pattern in patterns:
        df_pattern = get_chunk_composition_pattern_data(pattern, data)
        for index, row in df_pattern.iterrows():
            boxplot_data.append([row[variable], pattern, row['partial_order']])
    
    boxplot_data = pd.DataFrame(boxplot_data, columns=[variable, 'group', 'partial_order'])
    sns.boxplot(x="group", y=variable, hue='partial_order', data=boxplot_data, showfliers = False, ax = axis).set(
    xlabel='Resolution pattern', ylabel=variable_text)

def get_chunk_composition_pattern_data(pattern, data):
    return data[data['chunk_composition'] == f' {pattern}']