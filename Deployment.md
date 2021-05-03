# Local Development
Docker network host mode does not work on mac because the host runs on a VM on mac. 
## CouchDB 
```
cd <project directory>
sudo addgroup docker
sudo adduser $(whoami) docker
mkdir ./data
chmod 775 ./data
docker run -p 5984:5984 -p 4369:4369 -p 9100-9200:9100-9200 -e COUCHDB_USER=user -e COUCHDB_PASSWORD=pass -e NODENAME=127.0.0.1 -v ./data:/opt/couchdb/data --name couchdb -d couchdb:3.1.1
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
sudo echo "no_proxy=localhost,127.0.0.1,localaddress,172.16.0.0/12,.melbourne.rc.nectar.org.au,.storage.unimelb.edu.au,.cloud.unimelb.edu.au" | sudo tee -a /etc/environment
```

## Mount Disk 
```
sudo mkfs.ext4 /dev/vdb
sudo mkdir /data
sudo mount -t auto /dev/vdb /data
sudo adduser ubuntu docker
sudo chown :docker /data
sudo chmod 775 /dat
```

## Docker Swarm 
```
sudo apt-get update
sudo apt install docker.io vim python3 python3-pip -y
sudo chmod 775 /var/run/docker.sock
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
echo "Environment="NO_PROXY=localhost,127.0.0.1,localaddress,172.16.0.0/12,.melbourne.rc.nectar.org.au,.storage.unimelb.edu.au,.cloud.unimelb.edu.au" | sudo tee -a /etc/systemd/system/docker.service.d/http-proxy.conf               
sudo systemctl daemon-reload
sudo systemctl restart docker
sudo systemctl show --property=Environment docker
```

## Deployment 
On the main manager instance:
```
docker run -it -d -p 8080:8080 -v /var/run/docker.sock:/var/run/docker.sock dockersamples/visualizer
docker run -it -d -p 9000:9000 -v /var/run/docker.sock:/var/run/docker.sock portainer/portainer
docker run -p 5984:5984 -p 4369:4369 -p 9100-9200:9100-9200 --network host -e COUCHDB_USER=user -e COUCHDB_PASSWORD=pass -e NODENAME=127.0.0.1 -v  src=/data,dst=/opt/couchdb/data --name couchdb_backup -d couchdb:3.1.1
docker node update --availability drain instance-1
docker stack deploy -c docker-compose.yml twitterlance
```
Run on at least n-1 instances outside of main manager: 
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