import pandas as pd
import json

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

def equivalent_context(context_solution, context_chunk):
    context_solution = remove_empty_lines(context_solution)
    context_chunk = remove_empty_lines(context_chunk)
    if len(context_solution) != len(context_chunk):
        return False
    for i in range(len(context_solution)):
        if context_solution[i] != context_chunk[i]:
            return False
    return True

class Chunk:
    def __init__(self, chunk_id):
        self.chunk_id = chunk_id
        self.get_chunk(chunk_id)

    def get_conflict_text(self):
        return self.before_context + '<<<<<<<\n' + self.v1 + '=======\n' + self.v2 + '>>>>>>>\n' + self.after_context

    def get_chunk(self, chunk_id):
        file = 'data/dataset.json'

        with open(file) as f:
            data_listofdict = json.load(f)

        df = pd.DataFrame.from_dict(data_listofdict)
        chunk_data = df[df['chunk_id'] == chunk_id]
        if len(chunk_data) >= 1:
            chunk_data = chunk_data.iloc[0]
        self.before_context = chunk_data['before_context']
        self.v1 = chunk_data['v1']
        self.v2 = chunk_data['v2']
        self.after_context = chunk_data['after_context']
        self.resolution = chunk_data['solution']

    '''
        Cleans the chunk resolution text by removing potential context lines.
        We assume that 3 context lines are used before and after the conflicting chunk
        If the solution's context is different from the chunk's context, returns None
    '''
    def get_clean_solution(self):
        solution = normalize_lines(self.resolution.splitlines()).copy()
        before_context = normalize_lines(self.before_context.splitlines())
        after_context = normalize_lines(self.after_context.splitlines())
        
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

def print_line_with_context(resolution, line_index, context_lines_amount):
    if line_index < len(resolution):
        start_context = 0
        end_context = len(resolution)
        if line_index > context_lines_amount:
            start_context = line_index-context_lines_amount
        for line in resolution[start_context:line_index]:
            print(line)
        
        print('----')
        print(resolution[line_index])
        print('----')

        if len(resolution) > line_index + context_lines_amount:
            end_context = line_index + context_lines_amount + 1
        for line in resolution[line_index+1: end_context]:
            print(line)


# resolution = ['1', '2', '3', '4', '5', '6', '7', '8']
# line_index = 7
# context_lines_amount = 2
# print_line_with_context(resolution, line_index, context_lines_amount)