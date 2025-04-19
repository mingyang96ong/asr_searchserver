#!/bin/bash

model_cached_dir=$(python -c "from model import AudioProcessor;print(AudioProcessor.CACHED_DIRECTORY)")

if ! [[ -d ${model_cached_dir} ]]; then
    echo "Model is not cached. Downloading the model to cached directory"
    python -c "from model import AudioProcessor; AudioProcessor()" # Run the initialisation process, will download the model
    return_status=$?
    if [[ ${return_status} -gt 0 ]]; then
        echo "Something download failed. Return status: ${return_status}"
        exit 1
    fi
    echo "Download is completed"
fi

colima start --memory 8 --cpu 4

# Build docker command
docker build -t "asr_api:v1" .

# Run docker command
# docker run -d -p 127.0.0.1:8001:8001 asr_api:v1

# Test sample command
# curl -F 'file=@/absolute/path/to/audio' localhost:8001 -H 'content-type: multipart/form-data'