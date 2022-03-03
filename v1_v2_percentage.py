import pandas as pd
import json

def equivalent_context(context_solution, context_chunk):
    context_solution = remove_empty_lines(context_solution)
    context_chunk = remove_empty_lines(context_chunk)
    if len(context_solution) != len(context_chunk):
        return False
    for i in range(len(context_solution)):
        if context_solution[i] != context_chunk[i]:
            return False
    return True

'''
    Cleans the chunk resolution text by removing potential context lines.
    We assume that 3 context lines are used before and after the conflicting chunk
    If the solution's context is different from the chunk's context, returns None
'''
def get_clean_solution(solution, before_context, after_context):
    solution = normalize_lines(solution.splitlines()).copy()
    before_context = normalize_lines(before_context.splitlines())
    after_context = normalize_lines(after_context.splitlines())
    
    if len(solution) >= 6:
        # what is the last line from the three first solution lines that is present in the before_context?
        solution_before_context_candidate = solution[:3]
        last_line_before_context = 0
        for index, line in enumerate(solution_before_context_candidate):
            if line in before_context:
                last_line_before_context = index
        
        # what is the first line from the last three solution lines that is present in the after_context?
        solution_after_context_candidate = solution[-3:]
        first_line_after_context = len(solution)
        for index, line in enumerate(solution_after_context_candidate):
            if line in after_context:
                first_line_after_context = len(solution) - (3 - index)
                break
        solution_before_context = solution[:last_line_before_context+1]
        solution_after_context = solution[first_line_after_context:]
        if (equivalent_context(solution_before_context, before_context) 
            and equivalent_context(solution_after_context, after_context)):
            return solution[last_line_before_context+1:first_line_after_context]
        else:
            return None
    return solution 


def normalize_line(line):
    return line.replace(" ", "").replace("\t", "").replace("\n", "")

def normalize_lines(lines):
    normalized_lines = []
    for line in lines:
            normalized_lines.append(normalize_line(line))
    return normalized_lines

def remove_empty_lines(lines):
    cleaned_lines = []
    for line in lines:
        if line != '':
            cleaned_lines.append(line)
    return cleaned_lines

def is_null(row):
    return pd.isna(row['chunk_id'])

'''
    Returns the percentage of elements in 'comparison_list' that are in 'base_list'
'''
def get_occurrence_percentage(base_list, comparison_list):
    occurrences_count = 0
    for item in comparison_list:
        if item in base_list:
            occurrences_count+=1
    return round(occurrences_count/len(comparison_list),2)

'''
    Returns the percentage of lines in 'comparison_list' that are both in 'list1' and 'list2'
'''
def get_intersection_percentage(list1, list2, comparison_list):
    occurrences_count = 0
    for item in comparison_list:
        if item in list1 and item in list2:
            occurrences_count+=1
    return round(occurrences_count/len(comparison_list),2)

'''
    Returns a string representing the composition of the resolution in relation to v1 and v2.
    Groups chunks of repeating lines from each side.
    Example:
        v1 = ABC  V2 = CDE  resolution = ABE
        first line is from v1, second from v1, and third from v2.
        if no grouping was used, it would return v1v1v2.
        However, since we are grouping chunks of repeating lines, 
            it will return v1v2
    If a line occurs in both v1 and v2, use (v1_2)
        v1 = ABC V2 = CDE  resolution = BCE
            returns v1(v1_2)v2
'''
def get_chunk_composition(v1, v2, resolution):
    v1 = v1.copy()
    v2 = v2.copy()
    composition = ''
    previous_line = ''
    for line in resolution:
        in_v1 = line in v1
        in_v2 = line in v2
        if in_v1 and in_v2 and previous_line != '(v1_2)':
            composition+=' (v1_2)'
            previous_line = '(v1_2)'
        elif in_v1 and previous_line != 'v1':
            composition+=' v1'
            previous_line = 'v1'
        elif in_v2 and previous_line != 'v2':
            composition+=' v2'
            previous_line = 'v2'
        
        if in_v1:
            v1.remove(line)
        if in_v2:
            v2.remove(line)
            
    return composition

'''
    Given v1 or v2, returns the number of lines in the resolution that is missing from v1 or v2
'''
def get_missing_lines_amount(chunk_side, resolution):
    missing_lines_number = 0
    resolution = resolution.copy()
    for line in chunk_side:
        if line not in resolution:
            missing_lines_number+=1
        else:
            resolution.remove(line)
    return missing_lines_number

def get_size(text):
    return text.count('\n')


# v1 = ['A', 'B', 'C']
# v2 = ['C', 'D', 'E']
# resolution = ['B', 'C', 'E']
# print(get_chunk_composition(v1, v2, resolution))

if __name__ == '__main__':
    file = 'data/dataset.json'
    with open(file) as f:
        data_listofdict = json.load(f)
    df = pd.DataFrame.from_dict(data_listofdict)
    total = 0
    total_manual = 0
    collected_data = []
    violates_partial_order_count = 0
    for index, row in df.iterrows():
        if not is_null(row):
            clean_solution = get_clean_solution(row['solution'], row['before_context'], row['after_context'])
            chunk_id = row['chunk_id']
            v1 = row['v1']
            v2 = row['v2']
            before_context = row['before_context']
            after_context = row['after_context']
            chunk_size = get_size(before_context) + get_size(v1) + get_size(v2) + get_size(after_context)
            if clean_solution != None:
                resolution_size = len(clean_solution)
                clean_solution = remove_empty_lines(clean_solution)
                print(index, chunk_id, chunk_size, resolution_size)
                v1 = normalize_lines(v1.splitlines())
                v2 = normalize_lines(v2.splitlines())
                if type(clean_solution) == str:
                    clean_solution = normalize_lines(clean_solution.splitlines())
                v1 = remove_empty_lines(v1)
                v2 = remove_empty_lines(v2)
                
                v1_percentage = get_occurrence_percentage(v1, clean_solution)
                v2_percentage = get_occurrence_percentage(v2, clean_solution)
                intersection_percentage = get_intersection_percentage(v1, v2, clean_solution)
                composition = get_chunk_composition(v1, v2, clean_solution)
                missing_v1_lines = get_missing_lines_amount(v1, clean_solution)
                missing_v2_lines = get_missing_lines_amount(v2, clean_solution)
                if len(v1) > 0:
                    percentage_missing_v1_lines = round((missing_v1_lines/len(v1))*100,2)
                else:
                    percentage_missing_v1_lines = 0
                if len(v2) > 0:
                    percentage_missing_v2_lines = round((missing_v2_lines/len(v2))*100,2)
                else:
                    percentage_missing_v2_lines = 0

                collected_data.append([chunk_id, v1_percentage, v2_percentage, intersection_percentage,
                    composition, missing_v1_lines, missing_v2_lines, percentage_missing_v1_lines, percentage_missing_v2_lines, len(v1), len(v2)])
            else:
                print(f'Resolution of chunk {chunk_id} could not be isolated.')
                solution = row['solution'].splitlines()
                collected_data.append([chunk_id, -1, -1, -1, '', -1, -1, -1, -1, -1, -1])
                total_manual+=1

    collected_data_df = pd.DataFrame(collected_data, columns=['chunk_id', 'v1_percentage', 'v2_percentage', 'intersection_percentage', 'chunk_composition',
        'missing_v1_lines', 'missing_v2_lines', 'missing_v1_lines_perc', 'missing_v2_lines_perc', 'v1_size', 'v2_size'])
    collected_data_df.to_csv('data/resolution_composition.csv', index=False)