## Scripts:
<table>
    <thead>
        <tr>
            <th>Execution order</th>
            <th>Script</th>
            <th>Input</th>
            <th>Output</th>
            <th>Purpose</th>
        </tr>
    </thead>
    <tr>
        <td>-1</td>
        <td>dataCollection.py</td>
        <td>Conflicts database, Github API, github_keys, data/INITIAL_DATASET.csv</td>
        <td>data/result.json</td>
        <td>Script used to generate the dataset file containing the conflicting chunks information. Not required if using the provided JSON dataset.</td>
    </tr>
    <tr>
        <td>0</td>
        <td>extract_data.py</td>
        <td>result.json, Conflicts database</td>
        <td>dataset.json</td>
        <td>Adds complementary data to the JSON dataset file. Not required if using the provided JSON dataset.</td>
    </tr>
    <tr>
        <td>1</td>
        <td>download_dataset_file.py</td>
        <td>Google Drive (repository)</td>
        <td>data/dataset.json, data/result.json, data/INITIAL_DATASET.csv</td>
        <td>Downloads the JSON dataset file containing the conflicting chunks information.</td>
    </tr>
    <tr>
        <td>2</td>
        <td>partial_order.py</td>
        <td>dataset.json</td>
        <td>data/partial_order_result.csv</td>
        <td>Script used to check the partial order in the conflicting chunks resolution lines.</td>
    </tr>
    <tr>
        <td>3</td>
        <td>select_chunk_sample.py</td>
        <td>data/partial_order_result.csv</td>
        <td>data/violate_partial_order_sample.csv</td>
        <td>Script used to select a subsample of the conflicting chunks that violate the partial order to be analyzed manually.</td>
    </tr>
    <tr>
        <td>3</td>
        <td>v1_v2_percentage.py</td>
        <td>data/partial_order_result.csv</td>
        <td>data/resolution_composition.csv</td>
        <td>Script to analyze the composition of the conflicting chunks resolution lines.</td>
    </tr>
    <tr>
        <td></td>
        <td>duplicated_lines.py</td>
        <td>dataset.json</td>
        <td>data/has_duplication_result.csv</td>
        <td>(DEPRECATED) Script used to analyze if duplicated lines from the chunk are used in the resolution.</td>
    </tr>
    <tr>
        <td></td>
        <td>inspect_util.py</td>
        <td>data/dataset.json</td>
        <td></td>
        <td>Script used to support the manual analysis of conflicting chunks.</td>
    </tr>
    <tr>
        <td></td>
        <td>debug_chunk.py</td>
        <td>data/dataset.json</td>
        <td></td>
        <td>Script for manually debugging other scripts.</td>
    </tr>
</table>



## Notebooks:

<table>
    <thead>
        <tr>
            <th>Execution order</th>
            <th>Notebook</th>
            <th>Input</th>
            <th>Output</th>
            <th>Purpose</th>
        </tr>
    </thead>
    <tr>
        <td></td>
        <td>inspect_chunk.ipynb</td>
        <td></td>
        <td></td>
        <td>Notebook used to inspect chunks manually.</td>
    </tr>
    <tr>
        <td>1</td>
        <td>find_malformed_chunks.ipynb</td>
        <td>data/dataset.json</td>
        <td>data/malformed_chunks.csv</td>
        <td>Notebook to filter malformed chunks in the dataset.</td>
    </tr>
    <tr>
        <td>2</td>
        <td>partial_order_analysis.ipynb</td>
        <td>data/partial_order_result.csv, data/malformed_chunks.csv</td>
        <td></td>
        <td>Notebook to perform analysis using the collected partial order data.</td>
    </tr>
    <tr>
        <td>3</td>
        <td>violation_inspection_analysis.ipynb</td>
        <td>data/violate_partial_order_inspection.csv (generated after manual analysis of chunks' sample)</td>
        <td></td>
        <td>Notebook for analyzing cases where the partial order is violated.</td>
    </tr>
    <tr>
        <td>4</td>
        <td>resolution_composition_analysis.ipynb</td>
        <td>data/resolution_composition.csv</td>
        <td></td>
        <td>Notebook for analyzing the composition of conflicting chunks resolution lines.</td>
    </tr>
    
</table>





