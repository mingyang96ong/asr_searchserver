import os
import requests

from typing import Tuple

import pandas as pd

import tqdm

# Technically, this can do some level of multi threading to speed up, if the server is able process the request fast
from concurrent.futures import ThreadPoolExecutor, wait, as_completed

# Configurable Variable
AUDIO_SOURCE_DIR = "../data/cv-valid-dev/cv-valid-dev"
RAW_DATA_FILE = '../data/cv-valid-dev.csv'
API = "http://localhost:8001/asr"
OUTPUT_FILE = f"final_{os.path.basename(RAW_DATA_FILE)}" # Prepend final_ before the RAW_DATA_FILE
# End of Configurable Variables

def read_and_send_request(full_path: str) -> Tuple:
    """
    Takes in audio absolute file path and send to the API (Here, API is hardcoded)

    Parameters:
    full_path (str): audio absolute file path

    Returns:
    Tuple [str, str, str]: (Full download path, response json, error message)

    Example:
    >>> read_and_send_request('/code/audio.mp3')
    ('/code/audio.mp3', 'THIS IS COOL', '')
    """
    with open(full_path, 'rb') as f:
        files = {'file': f}
        resp = requests.post(API, files=files)
    
    if resp.status_code != 200:
        return (full_path, None, 'bugged') 

    return (full_path, resp.json(), '')

if __name__ == '__main__':

    all_files = os.listdir(AUDIO_SOURCE_DIR)

    print(f"There are {len(all_files)} audio files.")

    data_df = pd.read_csv(RAW_DATA_FILE)

    transcripted_info = {
        'filename': []
        , 'generated_text': []
        , 'duration': []
    }
    failed = []

    with ThreadPoolExecutor(max_workers = 5) as executor:
        print('Creation of threads to send files')
        futures = [executor.submit(read_and_send_request, os.path.join(AUDIO_SOURCE_DIR, audio_file)) for audio_file in tqdm.tqdm(all_files)]
        print('Completed in queuing the threads for files transfer')

        for future in tqdm.tqdm(as_completed(futures), total=len(all_files), desc="Processing"):
            filepath, result, err = future.result()
            filename = os.path.basename(filepath)
            if err:
                failed.append(filename)
            else:
                transcripted_info['filename'].append(filename)
                transcripted_info['generated_text'].append(result["transcription"])
                transcripted_info['duration'].append(result["duration"])

    # Manual fix the filename column
    transcripted_df = pd.DataFrame.from_dict(transcripted_info)
    transcripted_df['filename'] = os.path.basename(AUDIO_SOURCE_DIR) + '/' + transcripted_df['filename']
    # End of manual fix filename column
    
    # Drop if column already exists
    data_df.drop('generated_text', errors='ignore', inplace=True, axis=1)
    data_df.drop('duration', errors='ignore', inplace=True, axis=1)

    final = pd.merge(data_df, transcripted_df, on = 'filename', how='left')
    save_name = os.path.join(
        os.path.dirname(RAW_DATA_FILE)
        , OUTPUT_FILE
    )
    final.to_csv(save_name, index=False, header=True)
    