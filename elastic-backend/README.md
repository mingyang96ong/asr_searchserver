# elastic-backend
It is elastic search service

# Disclaimer
1. Ran docker with colima, so there are some settings that specifically used for colima

# Local Single Node Setup
### Setup Elasticsearch Server from Docker
```bash
docker run -d -p 127.0.0.1:9200:9200 --name elasticsearch
-e "discovery.type=single-node" \
-e "xpack.security.enabled=false" \
-e "network.host=0.0.0.0" \
-e "http.cors.enabled=true" \
-e "http.cors.allow-origin=http://localhost:3000" \
-e "http.cors.allow-headers=Origin,Content-Type,Accept,Authorization,x-elastic-client-meta" \
-e "http.cors.allow-credentials=true" \
docker.elastic.co/elasticsearch/elasticsearch:8.11.3
```

### Subsequent Starting Elasticsearch Server from Docker
```bash
docker run -d -p 9200:9200 \
-e "discovery.type=single-node" \
-e "xpack.security.enabled=false" \
-e "network.host=0.0.0.0" \
-e "http.cors.enabled=true" \
-e "http.cors.allow-origin=http://localhost:3000" \
-e "http.cors.allow-headers=Origin,Content-Type,Accept,Authorization,x-elastic-client-meta" \
-e "http.cors.allow-credentials=true" \
docker.elastic.co/elasticsearch/elasticsearch:8.11.3
```

### Local install NGINX for macOS
1. `brew install nginx`
2. Look for nginx config via `brew info nginx`
3. Start nginx `brew services start nginx`
4. To stop nginx `brew services stop nginx`
5. To reload nginx `nginx -s reload`

### Manual data adding to Elastic Server (Refer to Setup conda environment for cv-index.py)
1. Activate the conda environment and install `requirements.txt`
2. Run `python cv-index.py`

# Deployment Setup (2 nodes cluster, if you are not using search-ui)
1. Install `docker-compose` for your operating system
2. You need to run `docker network create elastic-network` for search-ui to connect with this elastic search index server
3. Run `docker-compose up`

# Setup conda environment for cv-index.py
1. `conda create -n es_backend python=3.9.21 pip`
2. `conda activate es_backend`
3. `pip install -r requirements.txt`

# Test the index in the Elasticsearch Server
`curl 127.0.0.1:9200/cv-transcriptions/_search`

# Test with query filter in Elasticsearch Server
1. Search for results that contains `'BE'` in `generated_text` column
```bash
curl -X GET 127.0.0.1:9200/cv-transcriptions/_search \
-H 'Content-Type: application/json' \
-d'{
    "query": {
        "match": {
            "generated_text": "BE"
        }
    }
}'
```
2. Same query with url only `127.0.0.1:9200/cv-transcriptions/_search?q=generated_text:BE`
3. Get data with `127.0.0.1:9200/cv-transcriptions/_search`