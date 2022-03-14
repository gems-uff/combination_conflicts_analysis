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


def print_lines(lines):
    for line in lines:
        print(line)

def partial_sorting(v1, v2, m):
  v1.append(None)
  v2.append(None)
  # The value in matrix[i][j] indicates the index in m which should be searched
  # in v1[i:] and v2[j:] 
  matrix = [[None for j in range(len(v2))] for i in range(len(v1))]

  for i in range(len(v1)):
    for j in range(len(v2)):
      if i > 0:
        up = matrix[i-1][j]
        if m[up] == v1[i-1]:  # match in v1
          up += 1
      else:
        up = 0
        
      if j > 0:
        left = matrix[i][j-1]
        if m[left] == v2[j-1]:  # match in v2
          left += 1
      else:
        left = 0

      matrix[i][j] = max(up, left)

      if matrix[i][j] == len(m):
        return True, matrix
  return False, matrix

'''
    A resolution violates the partial order when there is no way to arrange the 
        chunk lines to compose the resolution without breaking their original order
'''
def has_partial_order(v1,v2, context_before, context_after, resolution, chunk_id):
    v1 = normalize_lines(v1.splitlines())
    v2 = normalize_lines(v2.splitlines())
    context_before = normalize_lines(context_before.splitlines())
    context_after = normalize_lines(context_after.splitlines())
    if type(resolution) == str:
        resolution = normalize_lines(resolution.splitlines())
    else:
        resolution = normalize_lines(resolution)
    v1 = remove_empty_lines(v1)
    v2 = remove_empty_lines(v2)
    resolution = remove_empty_lines(resolution)
    partial_sorting_status, sorting_matrix  = partial_sorting(v1, v2, resolution)
    return partial_sorting_status, sorting_matrix

def get_violation_line(sorting_matrix, clean_resolution):
    match = []
    index_violation = max(map(max, sorting_matrix))
    violation_line = clean_resolution[index_violation]
    return violation_line, index_violation, match

def print_matrix(matrix):
  for list in matrix:
    print(list)
  print()

def test():
    v1 = 'a\nb\nc\nd'
    v2 = 'x\ny\nz'
    m1 = 'a\ny\nc\nz\nd'
    m2 = 'a\ny\nd\nz\nc'
    # v1 = ['a', 'b', 'c', 'd']
    # v2 = ['x', 'y', 'z']
    # m1 = ['a', 'y', 'c', 'z', 'd']
    # m2 = ['a', 'y', 'd', 'z', 'c']

    print(has_partial_order(v1, v2,'', '', m1, 0))
    print(has_partial_order(v1, v2,'', '', m2, 0))

def is_null(row):
    return pd.isna(row['chunk_id'])


def get_size(text):
    return text.count('\n')
# test()
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
            chunk_size = get_size(v1) + get_size(v2)
            if clean_solution != None:
                resolution_size = len(clean_solution)
                clean_solution = remove_empty_lines(clean_solution)
                print(index, chunk_id, chunk_size, resolution_size)
                partial_order, sorting_matrix = has_partial_order(v1, v2, before_context, after_context, clean_solution, chunk_id)
                # get_violation_line(sorting_matrix, clean_solution)
                if not partial_order:
                    violates_partial_order_count+=1
                total+=1
                collected_data.append([chunk_id, partial_order, chunk_size, resolution_size])
            else:
                print(f'Resolution of chunk {chunk_id} could not be isolated.')
                solution = row['solution'].splitlines()
                collected_data.append([chunk_id, 'manual', chunk_size, len(solution)])
                total_manual+=1

    print(f'Total: {total}.  Violates partial order: {violates_partial_order_count} ({(violates_partial_order_count/total)*100:.2f}%)')
    print(f'Total # of chunks that require manual analysis: {total_manual} ({(total_manual/(total+total_manual))*100:.2f}%)')
    collected_data_df = pd.DataFrame(collected_data, columns=['chunk_id', 'partial_order', 'chunk_size', 'resolution_size'])
    collected_data_df.to_csv('data/partial_order_result.csv', index=False)