import pandas as pd
import json

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