from flask import Flask, request, make_response
from http import HTTPStatus
from os.path import splitext, basename, exists
import os

from model import AudioProcessor

import json

app = Flask(__name__)

# Hard code for now
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r') as f:
    config = json.load(f)

DOWNLOAD_DIR = config['DOWNLOAD_DIR']
# END OF HARDCODE

processor = AudioProcessor()

@app.route('/ping', methods=['GET'])
def ping():
    # Just allow you to ping and pong back
    return "pong"


@app.route('/asr', methods=['POST'])
def asr():
    """
    Accepts a POST request that contains an audio file 'file' in multipart/form-data

    Returns:
    flask.wrappers.Response: Response with the 'transcription' and 'duration' of the audio file
    """
    assert 'file' in request.files, "Please pass in your 'file' to be transcribe in your request"
    
    if request.content_type[:len('multipart/form-data')] != 'multipart/form-data':
        return make_response('Invalid request', HTTPStatus.BAD_REQUEST)
    
    f = request.files['file'] 

    download_path, err = download(f)

    if err:
        return err, HTTPStatus.BAD_REQUEST
    
    try:
        transcription, duration = processor.decode(download_path)
    except Exception as e:
        print(e)
    finally:
        if os.path.exists(download_path):
            os.remove(download_path)

    # Building the response
    body = {'transcription': transcription, 'duration': '{:.2f}'.format(duration)}
    resp = make_response(body, HTTPStatus.OK)
    resp.headers['content-type'] = 'application/json'

    

    return resp

from soundfile import _formats as audio_formats
import werkzeug

import datetime
from typing import Tuple

def download(f: werkzeug.datastructures.FileStorage, download_dir: str = DOWNLOAD_DIR) -> Tuple[str, str]:
    """
    Takes in file object and checks for correct audio types

    Parameters:
    f (werkzeug.datastructures.FileStorage): file to be downloaded to the server

    Returns:
    Tuple [str, str]: The final downloaded audio file path on the server and error message. 
    Filepath would be empty if there is an error. If there is no error, error message will be empty.

    Example:
    >>> download(f, download_dir)
    ('/code/tmp/download_audio.mp3', '')
    """
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    f = request.files['file'] 

    raw_basefile, raw_baseext = splitext(f.filename)
    if raw_baseext[1:].upper() not in audio_formats:
        return '', f"Wrong audio format '{raw_baseext}'. Valid format are {audio_formats}"
    
    download_path = os.path.join(download_dir, f.filename)

    if os.path.exists(download_path):
        # Use another filename with timestamp suffix-ed
        # Should be sufficient to handle the case
        new_filename = f"{raw_basefile}_{int(datetime.datetime.now().timestamp())}{raw_baseext}"
        download_path = os.path.join(download_dir, new_filename)
    
    f.save(download_path)

    if not os.path.exists(download_path): # Download fail for some reason
        return '', f"Server is unable to download the file. Please try again later for '{f.filename}.'"
    
    return download_path, ''