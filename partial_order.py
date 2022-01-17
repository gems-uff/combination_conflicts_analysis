import pandas as pd
import json
from pandas.io.json import json_normalize


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
        self.v1 = False
        self.v2 = False

    def set_version(self, version):
        if version == 'v1':
            self.v1 = True
        if version == 'v2':
            self.v2 = True
    
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
            occurrence.set_version(version)
            occurrence.set_index(version, line_index+1)
            index[line] = occurrence
        else:
            occurrence = index[line]
            occurrence.set_version(version)
            occurrence.set_index(version, line_index+1)
            index[line] = occurrence
    return index


def violates_partial_order(v1,v2, context_before, context_after, resolution, chunk_id):
    v1 = normalize_lines(v1.splitlines())
    v2 = normalize_lines(v2.splitlines())
    context_before = normalize_lines(context_before.splitlines())
    context_after = normalize_lines(context_after.splitlines())
    if type(resolution) == str:
        resolution = normalize_lines(resolution.splitlines())
    index = {}
    index = populate_index(v1, 'v1', index)
    index = populate_index(v2, 'v2', index)
    
    last_v1_index = None
    last_v2_index = None
    
    for line in resolution:
        if line != '':
            if line not in context_before and line not in context_after:
                if line in index:
                    # side, side_index, multiple = index[line]
                    occurrence = index[line]
                    if occurrence.v1:
                        if last_v1_index != None:
                            if occurrence.last_v1_index < last_v1_index:
                                return True
                        last_v1_index = occurrence.last_v1_index
                    if occurrence.v2:
                        if last_v2_index != None:
                            if occurrence.last_v2_index < last_v2_index:
                                return True
                        last_v2_index = occurrence.last_v2_index
                else:
                    print(f'Resolution line not found in the chunk or context code. Discard chunk id: {chunk_id}')
                    return None
    return False

def is_null(row):
    return pd.isna(row['chunk_id'])


def test():
    # v1 = "        if (this.largeIcon != null) {\n            that.largeIcon = Bitmap.createBitmap(this.largeIcon);\n        }\n        that.iconLevel = that.iconLevel;\n"
    # v2 = "        that.iconLevel = this.iconLevel;\n"
    # resolution = '        if (this.largeIcon != null) {\n            that.largeIcon = Bitmap.createBitmap(this.largeIcon);\n        }\n        that.iconLevel = this.iconLevel;\n'
    # v1 = ""
    # v2 = "    private int getCdmaLevel() {\n        if (mSignalStrength == null) return 0;\n        final int cdmaDbm = mSignalStrength.getCdmaDbm();\n        final int cdmaEcio = mSignalStrength.getCdmaEcio();\n        int levelDbm = 0;\n        int levelEcio = 0;\n\n        if (cdmaDbm >= -75) levelDbm = 4;\n        else if (cdmaDbm >= -85) levelDbm = 3;\n        else if (cdmaDbm >= -95) levelDbm = 2;\n        else if (cdmaDbm >= -100) levelDbm = 1;\n        else levelDbm = 0;\n\n        // Ec/Io are in dB*10\n        if (cdmaEcio >= -90) levelEcio = 4;\n        else if (cdmaEcio >= -110) levelEcio = 3;\n        else if (cdmaEcio >= -130) levelEcio = 2;\n        else if (cdmaEcio >= -150) levelEcio = 1;\n        else levelEcio = 0;\n\n        return (levelDbm < levelEcio) ? levelDbm : levelEcio;\n    }\n\n    private int getEvdoLevel() {\n        if (mSignalStrength == null) return 0;\n        int evdoDbm = mSignalStrength.getEvdoDbm();\n        int evdoSnr = mSignalStrength.getEvdoSnr();\n        int levelEvdoDbm = 0;\n        int levelEvdoSnr = 0;\n\n        if (evdoDbm >= -65) levelEvdoDbm = 4;\n        else if (evdoDbm >= -75) levelEvdoDbm = 3;\n        else if (evdoDbm >= -90) levelEvdoDbm = 2;\n        else if (evdoDbm >= -105) levelEvdoDbm = 1;\n        else levelEvdoDbm = 0;\n\n        if (evdoSnr >= 7) levelEvdoSnr = 4;\n        else if (evdoSnr >= 5) levelEvdoSnr = 3;\n        else if (evdoSnr >= 3) levelEvdoSnr = 2;\n        else if (evdoSnr >= 1) levelEvdoSnr = 1;\n        else levelEvdoSnr = 0;\n\n        return (levelEvdoDbm < levelEvdoSnr) ? levelEvdoDbm : levelEvdoSnr;\n    }\n\n    private void updateAirplaneMode() {\n        mAirplaneMode = (Settings.System.getInt(mContext.getContentResolver(),\n            Settings.System.AIRPLANE_MODE_ON, 0) == 1);\n    }\n\n"
    # resolution = "\n    private void updateAirplaneMode() {\n        mAirplaneMode = (Settings.System.getInt(mContext.getContentResolver(),\n            Settings.System.AIRPLANE_MODE_ON, 0) == 1);\n    }\n\n"

    v1 = "A\nX\nA\nB"
    v2 = "A\nA\nX\nB"
    resolution = "A\nA\nB"
    # resolution = "A\nB\nA"
    # resolution = "A\nB\nX"
    # resolution = "A\nX\nB"
    # resolution = "A\nB"
    print(violates_partial_order(v1, v2, resolution, 0))

def get_size(text):
    return text.count('\n')

if __name__ == '__main__':
    file = 'data/dataset.json'
    with open(file) as f:
        data_listofdict = json.load(f)
    df = pd.DataFrame.from_dict(data_listofdict)
    total = 0
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
            resolution_size = len(clean_solution)
            violates_partial_order_status = violates_partial_order(v1, v2, before_context, after_context, clean_solution, chunk_id)
            if violates_partial_order_status:
                violates_partial_order_count+=1
            total+=1
            collected_data.append([chunk_id, violates_partial_order_status, chunk_size, resolution_size])

    print(f'Total: {total}.  Violates partial order: {violates_partial_order_count} ({(violates_partial_order_count/total)*100:.2f}%)')
    collected_data_df = pd.DataFrame(collected_data, columns=['chunk_id', 'violates_partial_order', 'chunk_size', 'resolution_size'])
    collected_data_df.to_csv('data/partial_order_result.csv', index=False)



