# Automatic Speech Recognition API + Elastic Search Server

# Deployment of Elastic Search Server
Deployment URL: [Deployment Link] (Removed)  

## Data Used (I will put the data here since I won't be upload this dataset)
[Original Source](https://www.dropbox.com/scl/fi/i9yvfqpf7p8uye5o8k1sj/common_voice.zip?rlkey=lz3dtjuhekc3xw4jnoeoqy5yu&dl=0) | 
[Kaggle](https://www.kaggle.com/datasets/mozillaorg/common-voice)  

## AWS EC2 Deployment Prerequisite
1. Firstly, you need to know free-tier is not enough to run this server.
2. Minimum requirement is 6GB memory. Free Tier only provides 1GB memory.
3. You need to generate your own `final_cv-valid-dev.csv` file which is used for the elastic search index
   1. Download the dataset and unzip it as `data` in this directory
   2. `cd asr` and run asr api (Follow the README.md in asr directory)
   3. Run `cv-decode.py` to get `final_cv-valid-dev.csv` (it will be saved in `./data` directory)

## AWS EC2 Deployment 
1. Create an account on AWS and look for EC2
2. Launch an instance (Linux OS)
3. Ensure your inbound rules to be SSH port (22), port 8080 (NGINX port) and port 3000 to connectable from any IP for easy configuration.
4. Set key-pair and you should get the RSA file.
   1. Firstly, move it to `~/.ssh`
   2. Secondly, `chmod 400 ${ssh_file}`
5. Find out the public IP which is your public IPV4 address for your EC2 instance
6. For fast transfer, you can simply tar all `elastic-backend` and tar all `search-ui` (without node_modules)
   1. `tar -czvf elastic-backend.tar elastic-backend`
   2. `tar -czvf search-ui.tar search-ui`
   3. `sftp -i ~/.ssh/${ssh_file} ec2-user@<your public ip ec2 instance>`
      1. For convenient ssh/sftp, you can modify your `~/.ssh/config`. Follow the steps at the page below.
   4. `put elastic-backend.tar .`
   5. `put search-ui.tar  .`
   6. `put data/final_cv-valid-dev.csv .`
      1. For this file (data/final_cv-valid-dev.csv),  you need to download the data set above
      2. Go to `asr` and run `bash start_server_locally.sh`
      3. After the server is started, run `python cv-decode.py`
      4. The whole process should take around 15 minutes at most
   7. Exit the sftp
7.  Ssh into the EC2 instance: `ssh -i ~/.ssh/${ssh_file} ec2-user@<your public ip ec2 instance>`
8. Setup the terminal: `echo "PS1='\H \$(pwd) \$ '" >> ~/.bashrc`
9.  Update the package installer: `sudo yum update -y`
10. Install docker: `sudo yum install docker -y`
11. Install docker-compose: `sudo curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | jq -r .tag_name)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`
12. Modify permission of docker-compose: `sudo chmod +x /usr/local/bin/docker-compose`
13. Start docker: `sudo systemctl start docker`
14. Change current user group: `sudo usermod -aG docker $USER`
15. Refresh the terminal (without logging out): `newgrp docker`
16. Set the minimum vm map (default: 65536) for Elasticsearch Index Server: `sudo sysctl -w vm.max_map_count=262144`
17. Create the docker network: `docker network create elastic-network`
18. Untar all the files and move the files
    1.  `tar -zxvf elastic-backend.tar`
    2.  `tar -zxvf search-ui.tar`
    3.  `rm *.tar`
    4.  `mkdir data`
    5.  `mv final_cv-valid-dev.csv data`
19. Modify docker-compose.yaml
    1.  Under `elastic-backend`, change all `"http.cors.allow-origin='http://localhost:3000'"` into `"http.cors.allow-origin='http://<EC2 instance public domain>:3000'"`
    2.  Under `search-ui`, change `"REACT_APP_ES_HOST=http://localhost:8080"` into `"REACT_APP_ES_HOST=http://<EC2 instance public domain>:8080"`
    3.  `<EC2 instance public domain>` should look something like `http://ec2-14-113-123-45.ap-southeast-1.compute.amazonaws.com`
20. Start the elastic-backend: `cd elastic-backend && docker-compose up -d && cd ..`
21. Start the search-ui (Make sure elastic-backend docker compose is fully completed): `cd search-ui && docker-compose up -d`
   
## AWS SSH Quick Setup Config
```
Host aws_ec2
   HostName <Public IPv4 Address of EC2>
   IdentityFile "/path/to/your_key.pem"
   User ec2-user
```
Future ssh/sftp can be `ssh aws_ec2` or `sftp aws_ec2`