from github import Github
import pandas as pd
import base64
import urllib.request
import psycopg2
import time
import datetime
import json


githubTokens = []
with open('github_keys') as file:
    githubTokens = [line.rstrip('\n') for line in file]


g=Github(githubTokens[0])


def getGitPath(chunk_id):
    conn = None
    rows = None
    gitPath = ''
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost")
        cur = conn.cursor()

        project_name = row['searchurl'].split("/")[-1]
        project_owner = row['searchurl'].split("/")[-2]
        chunk_id = row['chunk_id']
        query = "SELECT path FROM public.conflictingchunk as cd inner join conflictingfile as cf on cd.conflictingfile_id = cf.id        WHERE cd.id = "+str(chunk_id)
        cur.execute(query)
        result = cur.fetchone()
        path = result[0]
        gitPath = path[path.index(project_name) + len(project_name):]
#         print(index, end="\r")
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        conn.close()
    return gitPath
    
    
def getFileSize(code):
    return len(code.split("\n"))

def getChunkContent(chunkId):
    conn = None
    rows = None
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost")
        cur = conn.cursor()
        query = "SELECT content FROM public.conflictingcontent where conflictingchunk_id ="+str(chunkId)
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

def getSolutionContent(chunkId):
    conn = None
    rows = None
    try:
        conn = psycopg2.connect("dbname=gleiph user=heleno password=heleno host=localhost")
        cur = conn.cursor()
        query = "SELECT content from solutioncontent where conflictingchunk_id ="+str(chunkId)
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        conn.close()
        if(rows is not None):
            content = ""
            size = len(rows)
            initial = 2
            ending = size - 3
            count = 0
            for row in rows:
                if(count > initial and count < ending):
                    content += row[0] + "\n"
                count += 1
            return content
        return rows

def getChunkAbsoluteSize(beginLine, endLine):
    return (endLine - beginLine) + 1
    
def getLeftChunkCode(chunkCode):
    lines = chunkCode.split("\n")
    leftChunk = ""
    start = False
    for line in lines:
        if("<<<<<<<" in line):
            start = True
            continue
        if("=======" in line):
            break
        if(start == True):
            leftChunk+=line+"\n"
    return leftChunk
    
def getRightChunkCode(chunkCode):
    lines = chunkCode.split("\n")
    rightChunk = ""
    start = False
    for line in lines:
        if("=======" in line):
            start = True
            continue
        if(">>>>>>>" in line):
            break
        if(start == True):
            rightChunk+=line+"\n"
    return rightChunk 

def getIndex(line, code, vector):
    for i in range(len(code)):
        codeLine = code[i]
#         print('solutionLine= {}'.format(solutionLine))
        if(line == codeLine and i+1 not in vector):
            return i

def getSolutionVector(v1, v2, solution):
    space = v1.splitlines() + v2.splitlines()
    vector = []
    solutionLines = solution.splitlines()
    for line in solutionLines:
#         print('vector= {}'.format(vector))
        index = getIndex(line, space, vector)
        if(index != None):
            vector.append(index+1)

    if(len(vector) > 0):
        return vector 


df = pd.read_csv("data/INITIAL_DATASET.csv")


filtered = df[df['developerdecision'] == 'Combination']
len(filtered)


repos = {}
data = []
start_time = time.time()
counter = 0
print_every = 20
token_index=0
g=Github(githubTokens[token_index])
token_index+=1
print("Processing start at %s" % (datetime.datetime.now()))
count = 1
for index, row in filtered.iterrows():
    requestsRemaining = g.rate_limiting[0]
    if(requestsRemaining>2):
        try:
            row2 = []
            chunk_id = row['chunk_id']
            url = row['searchurl']
            git_path = getGitPath(chunk_id)
            beginLine = row['beginline']
            endLine = row['endline']
            sha = row['sha']
            base_sha = row['basesha']
            repoName = url.split("/")[-2] + "/" + url.split("/")[-1]
            if(repoName in repos):
                repo = repos.get(repoName)
            else:
                repo = g.get_repo(repoName)
                repos[repoName] = repo
            file = repo.get_contents(git_path, ref=sha)
            fileContent = base64.b64decode(file.content).decode("utf-8")
            chunkContent = getChunkContent(row['chunk_id'])
            leftChunk = getLeftChunkCode(chunkContent)
            rightChunk = getRightChunkCode(chunkContent)
            base_file = repo.get_contents(git_path, ref=base_sha)
            basefileContent = base64.b64decode(base_file.content).decode("utf-8")
            solution = getSolutionContent(chunk_id)
            percentage = index/df.size
            row2.append(chunk_id)
            row2.append(leftChunk)
            row2.append(rightChunk)
            row2.append(basefileContent)
            row2.append(solution)
            vector = getSolutionVector(leftChunk, rightChunk, solution)
    #         print(vector)
            if(vector ==None):
                continue
            row2.append(vector)
#             print(index)
            #print('{} --- {:.2f}% done... Requests remaining: {}'.format(datetime.datetime.now(),percentage, requestsRemaining), end="\r")
    #         print("LeftCC: %d  RightCC: %d  FileCC: %d Absolute size: %d  Relative size: %.2f \
    #      #Position: %d  "% (leftCC, rightCC, fileCC, chunkAbsSize, chunkRelSize, chunkPosition))
        except:
#             print('error')
            pass
        if(counter >= print_every):
            size = len(filtered)
            percentage = (index/size)*100
            intermediary_time = time.time() - start_time
            estimated = ((intermediary_time * 100)/percentage)/60/60
            print('{} --- {:.2f}% done... estimated time to finish: {:.2f} hours. {} of {} rows processed. {} requests '.format(datetime.datetime.now(),percentage, estimated, index, size, requestsRemaining), end="\r")
            counter = 0
        counter = counter+1
        data.append(row2)
    else:
        print("Github API requests exhausted. Waiting 60 seconds and trying again....", end="\r")
        time.sleep(60)
        if(token_index < len(githubTokens)-1):
            g=Github(githubTokens[token_index])
            token_index+=1
        else:
            token_index=0
elapsed_time = time.time() - start_time
print()
print("Processed in %d seconds. Exporting json..." % (elapsed_time))
result_df = pd.DataFrame(data, columns = ['chunk_id','v1', 'v2', 'base', 'solution', 'vector'])
# result_df = pd.merge(df,df2, on='chunk_id')
# result_file = "result.csv"
# result_df.to_csv(result_file)
data_dict = result_df.to_dict(orient="records")
with open('data/result.json', "w+") as f:
    json.dump(data_dict, f, indent=4)





