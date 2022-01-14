import pandas as pd
import json
from pandas.io.json import json_normalize

class Chunk:
    def __init__(self, chunk_id):
        self.get_chunk(chunk_id)

    def get_conflict_text(self):
        return self.before_context + '<<<<<<<\n' + self.v1 + '=======\n' + self.v2 + '>>>>>>>\n' + self.after_context

    def get_chunk(self, chunk_id):
        file = 'new_result2.json'

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