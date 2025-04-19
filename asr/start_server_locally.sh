#/bin/bash

app="asr_api"
port=8001

cleanup(){
    tmp_path=$(jq .DOWNLOAD_DIR $(dirname ${app})/config.json -r)
    
    if [[ -d ${tmp_path} ]]; then
        rm -r ${tmp_path}
    fi
}

# If you started colima, you need to stop it (MPS don't work on Linux VM, so we cannot use gunicorn here)
colima stop

# Deploy way of start server 
pushd $(dirname ${app})
# gunicorn $(basename ${app}):app --workers 1 --threads 2 --bind localhost:${port}
# Local test start server
flask -A "${app}" run -p ${port}

trap cleanup EXIT