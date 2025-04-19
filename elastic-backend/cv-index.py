from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import BulkIndexError
from elastic_transport import ConnectionError

import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm

import os

LOCALHOST = "127.0.0.1"
urls = os.environ.get("ES_HOSTS", LOCALHOST)

server_urls = [f'http://{url}:9200' for url in (urls.split(',') if urls != LOCALHOST else [urls])]
print(f"{server_urls=}")
data_filepath = '../data/final_cv-valid-dev.csv'
index_name = 'cv-transcriptions'

es = Elasticsearch(server_urls)
total_retries = 10
retries = total_retries
wait_time = 10
is_connected = False
# The server need time to start up, hence we will retries for 10 times and wait 1 second after each failed attempt
# Make this a little more robust
while not is_connected and retries:
    try:
        es.info()
        is_connected = True
        break
    except ConnectionError:
        retries -= 1
        print(f"Failed to connect {total_retries-retries} times. Retry in {wait_time} seconds")
        time.sleep(wait_time)
    except Exception as e:
        raise e

if not is_connected:
    exit(f'Cannot connect to elastic search url {server_urls}')

print(f"Connected to Elasticsearch server ({server_urls})")

# For simplicity, I will always reset the index. Means delete all first and create new index.
# If required to keep previous indices, we can do es.indices.exists(index_name) to check if the index exists before creating.
es.indices.delete(index=index_name, ignore_unavailable=True)
es.indices.create(
    index = index_name
    , settings = {
        "index": {
            "number_of_shards": 2
            , "number_of_replicas": 2
        }
    }
    , body={
        "mappings": {
            "dynamic": True, 
            "properties": { # Explicitly set duration as string,  so that it can be searched on elastic search UI
                "duration": {
                    "type": "text",
                    "fields": {
                        "as_float": { # Keep a float type for sorting purpose
                            "type": "float",
                        }
                        , "keyword" : {
                            "type" : "keyword",
                            "ignore_above" : 256
                        }
                    }
                }
            }
        }
    }
)

def bulk_insert(rows: pd.DataFrame):
    # Clean up the empty values like NaN with None
    rows = rows.replace({pd.NA: None, pd.NaT: None, float("nan"): None}).astype(object)
    actions = [
        {
            '_index': index_name
            , '_id': record['filename']
            , '_source': {
                k: v for k, v in record.items() if k != 'filename'
            }
        }  
        for record in rows.to_dict(orient='records') # List of dictionary
    ]

    try:
        helpers.bulk(es, actions)
    except BulkIndexError as e:
        print("Some documents failed to index.")
        for err in e.errors[:5]:  # show only first 5
            print(err)
        raise e
    return len(actions)

batch_size = 512 # Should not be too big consider that elasticsearch server might not be able to handle it

# Reading data batch by batch such that it can work for very large dataset
# Using bulk insert and multithreading can further speed up the process
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for rows in pd.read_csv(data_filepath, chunksize=batch_size):
        futures.append(executor.submit(bulk_insert, rows))

    for future in tqdm.tqdm(as_completed(futures), total=len(futures), desc="Processing"):
        print(f"Inserted {future.result()} records.")