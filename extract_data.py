# the solution content for some conflicts is not correct in the result.json file generated by dataCollection.py. This script is for correcting the problem.
#   problem: when the solution starts with a blank line in the database, the line is not considered as the context (3 first and last lines)
#   solution: access the data/result.json file. for each conflict, retrieve the solution from the database and reprocess the solution content to update the file.


# adds each chunk's before and after context to the result file (data/dataset.json)

import pandas as pd
import json
import psycopg2
import datetime

'''
    Returns the chunk's content
'''
def get_chunk_content(chunk_id):
    conn = None
    rows = None
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost port=32146")
        cur = conn.cursor()
        query = "SELECT content FROM public.conflictingcontent where conflictingchunk_id ="+str(chunk_id)
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        conn.close()
        if(rows is not None):
            content = ""
            for row in rows:
                content += row[0] + "\n"
            return content
        return rows


'''
Get the solution content including the context lines
'''
def get_solution_content(chunk_id):
    conn = None
    rows = None
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost port=32146")
        cur = conn.cursor()
        query = "SELECT content from solutioncontent where conflictingchunk_id ="+str(chunk_id)
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        conn.close()
        if(rows is not None):
            content = ""
            for row in rows:
                content += row[0] + "\n"
            return content
        return rows

def get_before_context(chunk_code):
    lines = chunk_code.split("\n")
    before_context = ""
    start = True
    for line in lines:
        if("<<<<<<<" in line):
            start = False
            continue
        if(start == True):
            before_context+=line+"\n"
    return before_context

def get_after_context(chunk_code):
    lines = chunk_code.split("\n")
    after_context = ""
    start = False
    for line in lines:
        if(">>>>>>>" in line):
            start = True
            continue
        if(start == True):
            after_context+=line+"\n"
    return after_context

def load_data(file_name):
    with open(file_name) as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data)
    return df

new_data = []
df = load_data('data/result.json')
for index, row in df.iterrows():
    print(f'{datetime.datetime.now()} ## Processing index {index} of {len(df)}.')
    if not pd.isna(row['chunk_id']):
        chunk_id = int(row['chunk_id'])
        solution = get_solution_content(chunk_id)
        chunk_content = get_chunk_content(chunk_id)
        before_context = get_before_context(chunk_content)
        after_context = get_after_context(chunk_content)
        base = row['base']
        v1 = row['v1']
        v2 = row['v2']
        new_data.append([chunk_id, v1, v2, base, solution, before_context, after_context])

result_df = pd.DataFrame(new_data, columns = ['chunk_id','v1', 'v2', 'base', 'solution', 'before_context', 'after_context'])
data_dict = result_df.to_dict(orient="records")
with open('data/dataset.json', "w+") as f:
    json.dump(data_dict, f, indent=4)