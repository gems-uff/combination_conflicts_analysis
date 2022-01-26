import pandas as pd
import json

'''
    Cleans the chunk resolution text by removing potential context lines.
    We assume that 3 context lines are used before and after the conflicting chunk
'''
def get_clean_solution(solution, before_context, after_context):
    if len(solution) >= 6:
        solution = normalize_lines(solution.splitlines())
        before_context = normalize_lines(before_context.splitlines())
        after_context = normalize_lines(after_context.splitlines())

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
        
        return solution[last_line_before_context:first_line_after_context]
    return solution 


class LineOccurrence:
    def __init__(self, content) -> None:
        self.content = content
        self.last_v1_index = None
        self.last_v2_index = None
        self.v1_occurrences = []
        self.v2_occurrences = []
        self.resolution_occurrences = []

    def set_version(self, version):
        if version == 'v1':
            self.v1 = True
        if version == 'v2':
            self.v2 = True

    def register_occurrence(self, version, line_index):
        if version == 'v1':
            self.v1_occurrences.append(line_index)
        if version == 'v2':
            self.v2_occurrences.append(line_index)
    
    def set_index(self, version, index):
        if version == 'v1':
            if self.last_v1_index != None:
                if index > self.last_v1_index:
                    self.last_v1_index = index
            else:
                self.last_v1_index = index

        if version == 'v2':
            if self.last_v2_index != None:
                if index > self.last_v2_index:
                    self.last_v2_index = index
            else:
                self.last_v2_index = index
        
def normalize_line(line):
    return line.replace(" ", "").replace("\t", "").replace("\n", "")

def normalize_lines(lines):
    normalized_lines = []
    for line in lines:
        normalized_lines.append(normalize_line(line))
    return normalized_lines

def populate_index(lines, version, index):
    for line_index, line in enumerate(lines):
        if line not in index:
            occurrence = LineOccurrence(line)
        else:
            occurrence = index[line]
        occurrence.set_version(version)
        occurrence.set_index(version, line_index+1)
        index[line] = occurrence

        occurrence.register_occurrence(version, line_index+1)

    return index

def check_duplications(v1,v2, context_before, context_after, resolution, chunk_id, log_line_duplication=False):
    v1 = normalize_lines(v1.splitlines())
    v2 = normalize_lines(v2.splitlines())
    context_before = normalize_lines(context_before.splitlines())
    context_after = normalize_lines(context_after.splitlines())
    if type(resolution) == str:
        resolution = normalize_lines(resolution.splitlines())
    index = {}
    index = populate_index(v1, 'v1', index)
    index = populate_index(v2, 'v2', index)

    for resolution_index, line in enumerate(resolution):
        if line != '':
            if line not in context_before and line not in context_after:
                if line in index:
                    occurrence = index[line]
                    occurrence.resolution_occurrences.append(resolution_index)
                else:
                    print(f'Resolution line not found in the chunk or context code. Discard chunk id: {chunk_id}')
                    return None
    printed_chunk_id = False
    has_duplication = False
    for index, occurrence in index.items():
        if len(occurrence.resolution_occurrences) > (len(occurrence.v1_occurrences) + len(occurrence.v2_occurrences)):
            if log_line_duplication:
                if not printed_chunk_id:
                    print(f'Chunk id: {chunk_id}')
                    printed_chunk_id = True
                print(f'Line:  {occurrence.content}')
                print(f'Occurrences in resolution: {occurrence.resolution_occurrences}')
                print(f'Occurrences in v1: {occurrence.v1_occurrences}')
                print(f'Occurrences in v2: {occurrence.v2_occurrences}')
                print()

            has_duplication = True
            
    if log_line_duplication and printed_chunk_id:
        print('-------------')
    return has_duplication

def is_null(row):
    return pd.isna(row['chunk_id'])

def get_size(text):
    return text.count('\n')

if __name__ == '__main__':
    file = 'data/dataset.json'
    with open(file) as f:
        data_listofdict = json.load(f)
    df = pd.DataFrame.from_dict(data_listofdict)
    total = 0
    collected_data = []
    has_duplication_count = 0
    for index, row in df.iterrows():
        if not is_null(row):
            clean_solution = get_clean_solution(row['solution'], row['before_context'], row['after_context'])
            chunk_id = row['chunk_id']
            v1 = row['v1']
            v2 = row['v2']
            before_context = row['before_context']
            after_context = row['after_context']
            chunk_size = get_size(before_context) + get_size(v1) + get_size(v2) + get_size(after_context)
            resolution_size = len(clean_solution)
            has_duplication = check_duplications(v1, v2, before_context, after_context, clean_solution, chunk_id)
            if has_duplication:
                has_duplication_count+=1
            total+=1
            collected_data.append([chunk_id, has_duplication, chunk_size, resolution_size])
    print(f'Total combination chunks: {total}.  Has duplications: {has_duplication_count} ({(has_duplication_count/total)*100:.2f}%)')
    collected_data_df = pd.DataFrame(collected_data, columns=['chunk_id', 'has_duplication', 'chunk_size', 'resolution_size'])
    collected_data_df.to_csv('data/has_duplication_result.csv', index=False)



