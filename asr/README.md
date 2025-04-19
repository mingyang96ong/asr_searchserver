# asr api
For this api, it has only two api. The main task that it does is to transcript audio to text.  
1. ping  
- Endpoint: `/ping`  
- Method: `GET`  
- Returns: `"pong"`  
- Example:
```bash
$ curl localhost:8001/ping
pong
```
2. asr  
- Endpoint: `/asr`  
- Method: `POST`  
- Headers: `'Content-Type:multipart/form-data'`  
- Parameters: `file: the audio file`  
- Returns: `{'transcription': 'THIS IS THE TEXT TRANSCRIPTED', 'duration': '20.1'}`  
- Example: 
```bash
$ curl -F "file=@/path/to/audiofile" localhost:8001/asr -H 'content-type: multipart/form-data'
{"duration":"5.06","transcription":"BE CAREFUL WITH YOUR PROGNOSTICATIONS SAID THE STRANGER"}
```

# Setup (Important for Local Test)
1. Create a conda environment first (Run `conda create -n asr_api python=3.9.21 pip` in bash terminal)
2. Activate the environment (Run `conda activate asr_api` in bash terminal)
3. Install the requirements packages (Run `pip install -r requirements.txt` in the bash terminal)

# Locally Run Server
Run `bash start_server_locally.sh`

# Locally Test Curl Commands (Same as Docker/Colima way)
1. Ping and Pong (`curl localhost:8001/ping` -> "pong")
2. Send audio file to transcript (`curl -F "file=@/path/to/audiofile" localhost:8001/asr -H 'content-type: multipart/form-data'`)

# Build Docker Environment (Simple)
#### Simple way for MacOS
1. Make sure you have `colima` installed
2. Run `create_docker_in_mac.sh` in bash terminal

#### Tedious way
1. Import `AudioProcessor` class from `model.py`
2. Instantiate the `AudioProcessor()` once to download the pretrained model into a cached folder for copying to docker image
3. Build the docker image (Run `docker build -t "your desired image name and tag" .`)


# Start the docker
#### Colima (MacOS way)
1. Make sure you run `colima start --memory 8 --cpu 4`
2. Run `docker run -d -p 127.0.0.1:8001:8001 asr_api:v1`

#### Docker
1. Run `docker run -m 8g --cpus=4 -d -p 127.0.0.1:8001:8001 asr_api:v1`

# cv-decode
1. For MacOS, you are recommended to run local test server as Metal Performance Shader (GPU-like device on Mac) cannot run in docker environment (Linux VM cannot run MPS).
2. For other operating systems, you may choose any approach to start the server.
3. Feel free to modify anything within the `Configurable Variables` in `cv-decode.py`
4. Simply run `python cv-decode.py`
