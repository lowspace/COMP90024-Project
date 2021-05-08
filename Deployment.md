# Local Development
Docker network host mode does not work on mac because the host runs on a VM on mac. 
## CouchDB 
```
cd <couchdb data directory>
docker run -p 5984:5984 -p 4369:4369 -p 9100-9200:9100-9200 -e COUCHDB_USER=user -e COUCHDB_PASSWORD=pass -e NODENAME=127.0.0.1 -v $PWD:/opt/couchdb/data --name couchdb -d couchdb:3.1.1
```

## Django Server
```
Python manage.py runserver
```

## uWSGI
```
docker build -t yangzy3/twitterlance .
docker run -p 80:80 yangzy3/twitterlance
```

## Push Image
```
docker build -t yangzy3/twitterlance .
docker push yangzy3/twitterlance
```

# Cloud Deployment

## MRC
```
sudo echo "HTTP_PROXY=http://wwwproxy.unimelb.edu.au:8000/" | sudo tee -a /etc/environment
sudo echo "HTTPS_PROXY=http://wwwproxy.unimelb.edu.au:8000/" | sudo tee -a /etc/environment
sudo echo "http_proxy=http://wwwproxy.unimelb.edu.au:8000/" | sudo tee -a /etc/environment
sudo echo "https_proxy=http://wwwproxy.unimelb.edu.au:8000/" | sudo tee -a /etc/environment
sudo echo "no_proxy=localhost,127.0.0.1,localaddress,172.16.0.0/12,.melbourne.rc.MRC.org.au,.storage.unimelb.edu.au,.cloud.unimelb.edu.au" | sudo tee -a /etc/environment
```

## Mount Disk 
Run on all nodes
```
sudo mkfs.ext4 /dev/vdb
sudo mkdir /data
sudo mount -t auto /dev/vdb /data
sudo adduser ubuntu docker
sudo rm -rf /data/*
sudo mkdir -p /data/opt/couchdb/data
sudo mkdir -p /data/opt/couchdb/etc/local.d
sudo chown -R :docker /data/opt
```

## Docker Swarm 
```
sudo apt-get update
sudo apt install docker.io vim python3 python3-pip -y
sudo chmod 666 /var/run/docker.sock
sudo systemctl restart docker
# Re-login to get permission
docker swarm init --advertise-addr <IP>
```

## MRC Proxy
```
sudo mkdir -p /etc/systemd/system/docker.service.d
echo "[Service]" | sudo tee -a /etc/systemd/system/docker.service.d/http-proxy.conf
echo "Environment="HTTP_PROXY=http://wwwproxy.unimelb.edu.au:8000/" | sudo tee -a /etc/systemd/system/docker.service.d/http-proxy.conf
echo "Environment="HTTPS_PROXY=http://wwwproxy.unimelb.edu.au:8000/" | sudo tee -a /etc/systemd/system/docker.service.d/http-proxy.conf
echo "Environment="NO_PROXY=localhost,127.0.0.1,localaddress,172.16.0.0/12,.melbourne.rc.MRC.org.au,.storage.unimelb.edu.au,.cloud.unimelb.edu.au" | sudo tee -a /etc/systemd/system/docker.service.d/http-proxy.conf
```

## Deployment 
On the main manager instance:
```
docker run -it -d -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock dockersamples/visualizer
docker run -it -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer
docker run -p 15984:5984 -e COUCHDB_USER=user -e COUCHDB_PASSWORD=pass -e NODENAME=127.0.0.1 -v /data/opt/couchdb/data:/opt/couchdb/data -v /data/opt/couchdb/etc/local.d:/opt/couchdb/etc/local.d --name couchdb_backup -d couchdb:3.1.1
docker node update --label-add couchdb=true instance-2
docker stack deploy -c docker-compose.yml twitterlance
```
Run on all instances outside of main manager: 
```
python3 reconsolidate.py
```
Load databases
```
curl -X POST http://localhost/analyser/couchdb 
```
Set up continous replication to backup
```
curl --header "Content-Type: application/json" user:pass@127.0.0.1:5984/_replicate -d '{"continuous":true,"source":"twitters","target":"user:pass@10.152.0.4:5984/twitters"}'
```

## Start service 
```
docker stack rm twitterlance
docker stack deploy -c docker-compose.yml twitterlance
docker service ps twitterlance_couchdb
docker service logs twitterlance_couchdb
```

# Manual Tests
```
curl http://127.0.0.1:80/analyser
curl http://user:pass@127.0.0.1:5984/_membership
curl -X PUT http://user:pass@127.0.0.1:5984/_users
curl -X PUT http://user:pass@127.0.0.1:5984/_replicator
curl -X PUT http://user:pass@127.0.0.1:5984/_global_changes
curl -X PUT http://user:pass@127.0.0.1:5984/tweets/1 -d '{"1": 2}'
```

yangzy3@instance-3:~$ curl http://user:pass@127.0.0.1:5984/tweets/_all_docs
{"total_rows":1,"offset":0,"rows":[
{"id":"1","key":"1","value":{"rev":"1-341d395a07d5adf9a714afe3a6a9f508"}}
]}
yangzy3@instance-3:~$ curl http://user:pass@127.0.0.1:5984/tweets/_all_docs
{"total_rows":1,"offset":0,"rows":[
{"id":"1","key":"1","value":{"rev":"1-341d395a07d5adf9a714afe3a6a9f508"}}
]}
yangzy3@instance-3:~$ curl http://user:pass@127.0.0.1:5984/tweets/_all_docs
{"total_rows":1,"offset":0,"rows":[
{"id":"1","key":"1","value":{"rev":"1-341d395a07d5adf9a714afe3a6a9f508"}}
]}
yangzy3@instance-3:~$ curl http://user:pass@127.0.0.1:5984/tweets/_all_docs
{"total_rows":1,"offset":0,"rows":[
{"id":"1","key":"1","value":{"rev":"1-341d395a07d5adf9a714afe3a6a9f508"}}
]}
yangzy3@instance-3:~$ curl http://user:pass@127.0.0.1:5984/_membership
{"all_nodes":["couchdb@twitterlance_couchdb.1.uucupd2w28xrhznlgup2nxhuf","couchdb@twitterlance_couchdb.2.sba63apne554uamt5o8eyfagf"],"cluster_nodes":["couchdb@twitterlance_couchdb.1.uucupd2w28xrhznlgup2nxhuf","couchdb@twitterlance_couchdb.2.sba63apne554uamt5o8eyfagf"]}
yangzy3@instance-3:~$ curl http://user:pass@127.0.0.1:5984/_membership
{"all_nodes":["couchdb@twitterlance_couchdb.1.uucupd2w28xrhznlgup2nxhuf","couchdb@twitterlance_couchdb.2.sba63apne554uamt5o8eyfagf"],"cluster_nodes":["couchdb@twitterlance_couchdb.1.uucupd2w28xrhznlgup2nxhuf","couchdb@twitterlance_couchdb.2.sba63apne554uamt5o8eyfagf"]}