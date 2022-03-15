import pandas as pd

df = pd.read_csv('data/resolution_composition.csv')
print(len(df))

malformed_chunks = pd.read_csv('data/malformed_chunks.csv')
malformed_chunks = malformed_chunks['chunk_id'].unique()
print(f'Removing {len(malformed_chunks)} malformed chunks')
df = df[~df['chunk_id'].isin(malformed_chunks)]
print(f'Total number of chunks: {len(df)}')

df = df[df['v1_percentage']!= -1]
print(len(df))

selected_chunks_ids = df['chunk_id'].unique()

with open('data/selected_chunks.txt', 'w') as file:
    file.write("\n".join(str(item) for item in selected_chunks_ids))