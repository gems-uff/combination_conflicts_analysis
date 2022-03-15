
import pandas as pd
import psycopg2
import time
import datetime
import json


'''

    Select all project names for the chunks in the list
    select * from conflictingchunk cc INNER JOIN conflictingfile cf where cc.id in (776662. 776782, 776793, 776828)

'''
def get_projects_stats(chunks_ids):
    conn = None
    rows = None
    data = []
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost port=32146")
        cur = conn.cursor()

        query = f"""select replace(p.htmlurl, 'https://github.com/', '') as "Project",
                    count(cc.id) as "Chunks" 
                    from conflictingchunk cc 
                    INNER JOIN conflictingfile cf on cc.conflictingfile_id=cf.id 
                    inner join revision r on cf.revision_id=r.id
                    inner join project p on r.project_id=p.id
                    where cc.id in ({chunks_ids})
                    group by p.id;
                """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        conn.close()
        if(rows is not None):
            for row in rows:
                project_name = row[0]
                chunks = row[1]
                data.append([project_name, chunks])
        return data

def get_selected_chunk_ids():
    chunks_ids_string = ''
    chunks_ids = []
    with open('data/selected_chunks.txt') as file:
        ids = file.readlines()
        for id in ids:
            id = id.strip()
            chunks_ids_string+=f'{id},'
            chunks_ids.append(id)
    if chunks_ids_string[len(chunks_ids_string)-1] == ',':
        chunks_ids_string = chunks_ids_string[:len(chunks_ids_string)-1]
    return chunks_ids_string, chunks_ids

'''
    Selects the number of chunks per failed merge in the chunks list
'''
def get_merges_chunks_stats(chunks_ids):
    conn = None
    rows = None
    data = []
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost port=32146")
        cur = conn.cursor()

        query = f"""select r.sha as "sha",
                    count(cc.id) as "Chunks" 
                    from conflictingchunk cc 
                    INNER JOIN conflictingfile cf on cc.conflictingfile_id=cf.id 
                    inner join revision r on cf.revision_id=r.id
                    inner join project p on r.project_id=p.id
                    where cc.id in ({chunks_ids})
                    group by r.sha;
                """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        conn.close()
        if(rows is not None):
            for row in rows:
                sha = row[0]
                chunks = row[1]
                data.append([sha, chunks])
        return data

'''
    Selects the number of files per failed merge in the chunks list
'''
def get_merges_files_stats(chunks_ids):
    conn = None
    rows = None
    data = []
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost port=32146")
        cur = conn.cursor()

        query = f"""select r.sha,
                    count(cf.id) as "Files" 
                    from conflictingfile cf 
                    inner join revision r on cf.revision_id=r.id
                    inner join project p on r.project_id=p.id
                    where cf.id in (
                        select cf2.id 
                        from conflictingchunk cc2
                        inner join conflictingfile cf2 on cc2.conflictingfile_id=cf2.id
                        where cc2.id in ({chunks_ids})
                    )
                    group by r.sha;
                """
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        conn.close()
        if(rows is not None):
            for row in rows:
                sha = row[0]
                files = row[1]
                data.append([sha, files])
        return data

def get_chunk_sha(chunk_id):
    conn = None
    result = ''
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost port=32146")
        cur = conn.cursor()

        query = f"""select r.sha
                    from conflictingchunk cc
                    inner join conflictingfile cf on cc.conflictingfile_id=cf.id
                    inner join revision r on cf.revision_id=r.id
                    where cc.id = {chunk_id};"""
        cur.execute(query)
        result = cur.fetchone()
        result = result[0]
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        conn.close()
    return result

def get_file_size(chunk_id, df):
    chunk = df[df['chunk_id'] == int(chunk_id)]
    if len(chunk) > 0:
        file_size = chunk.iloc[0]['fileSize']
        return file_size
    else:
        return -1

def get_chunks_info(chunks_ids):    
    df_attributes = pd.read_csv('data/dataset_attributes.csv') # we borrow this file from another project
    df_attributes = df_attributes[df_attributes['chunk_id'].isin(chunks_ids)]
    return df_attributes[['chunk_id', 'sha', 'fileSize']]

chunks_ids_string, chunks_ids = get_selected_chunk_ids()
projects_data = get_projects_stats(chunks_ids_string)
pd.DataFrame(projects_data, columns=['project', 'chunks']).sort_values(by=['chunks'], ascending=False).to_csv('data/chunks_per_project.csv', index=False)

failed_merges_chunks = get_merges_chunks_stats(chunks_ids_string)
df = pd.DataFrame(failed_merges_chunks, columns=['sha', 'chunks'])

failed_merges_files = get_merges_files_stats(chunks_ids_string)
df2 = pd.DataFrame(failed_merges_files, columns=['sha', 'files'])

df = pd.merge(df, df2, on='sha')

df.sort_values(by=['chunks'], ascending=False).to_csv('data/merge_stats.csv', index=False)


chunks_data = get_chunks_info(chunks_ids)
chunks_data.to_csv('data/chunks_info.csv', index=False)







