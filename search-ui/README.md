# Local Setup
Run `npm install && npm start`

# Simple docker compose setup
1. `docker network create elastic-network`. Need to ensure this is ran first so that this web service can connect to the elastic backend
2. Go to elastic-backend and run `docker-compose up` first
3. After step 2 is completed, run `docker-compose up` in this directory

# Ideal Deployment
Best approach: Build the react app by `npm run build` and followed by using nginx to host the react app in docker.  

# Boilerplate code
[Elasticsearch Official Site](https://www.elastic.co/docs/reference/search-ui/tutorials-elasticsearch-install-connector)  
Curl command: `curl https://codeload.github.com/elastic/app-search-reference-ui-react/tar.gz/master | tar -xz`  
In the case, where your npm has issue, you can copy the package-lock.json over to replace the one in this directory.  
In `@elastic` package, there was a dependency that imports without adding `.js` extension which some version of npm does not supports with webpack and ESM.  

# Some Versioning
npm: 8.15.0  
node: v16.17.1  