# This python script looks for isolated couchdb instances on the current docker host and add them to the couchdb cluster.
# Run recluster on each couchdb nodes, and then run reshard on all couchdb nodes
import requests, time, docker, configparser, os

help = 'Initialise the databses required by this app'

# Load CouchDB endpoint and credentials
config = configparser.ConfigParser()
try:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    config.read(os.path.join(__location__, "couchdb.conf"))
except:
    print("CouchDB Configuration not found")
COUCHDB_USERNAME = config.get('CouchDB', 'username')
COUCHDB_PASSWORD = config.get('CouchDB', 'password')
COUCHDB_ENDPOINT = config.get('CouchDB', 'endpoint')
REPEAT = int(config.get('CouchDB', 'repeat'))

def is_connected(node):
    res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/{node}')
    print(res.text)
    if res.json().get('error') is None:
        return True
    else: 
        return False

def reconsolidate_cluster():
    # Get all nodes
    running_nodes = []
    client = docker.from_env()
    services = client.services.list()
    for service in services:
        for task in service.tasks():
            if 'couchdb' in service.name and task['Status']['State'] == 'running' :
                running_nodes.append(f'couchdb@{service.name}.{task["Slot"]}.{task["ID"]}')

    print(f'CouchDB services: {running_nodes}')
    
    for node in running_nodes:
        for i in range(1, REPEAT):
            print(f'Adding {node}')
            res = requests.post(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_cluster_setup',json={"action": "enable_cluster", "bind_address":"0.0.0.0", "username": "user", "password":"pass", "node_count":len(running_nodes)})
            if res.json().get('reason') is not None and res.json().get('reason') != 'Cluster is already enabled':
                print(res.text) 
                return res.json()
            res = requests.put(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/_local/_nodes/{node}', json={})
            print(res.text)
            time.sleep(0.5)

        
    # Remove disconnected nodes
    res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_membership')
    cluster_nodes = res.json().get('cluster_nodes') + res.json().get('all_nodes') 
    for node in cluster_nodes: 
        if node not in running_nodes:
            print(f'Removing {node} due to disconnection.')
            res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/_local/_nodes/{node}')
            if res.json().get('_rev') is not None: 
                rev = res.json().get('_rev')
                res = requests.delete(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/_local/_nodes/{node}?rev={rev}')
                print(f'Result: {res.text}')

    res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_membership')
    cluster_nodes = res.json().get('cluster_nodes')
    print(f'Current nodes: {cluster_nodes}')

    print('Sync Shards...')
    res = requests.get('http://user:pass@127.0.0.1:5984/_all_dbs')
    for db in res.json(): 
        res = requests.post(f'http://user:pass@127.0.0.1:5984/{db}/_sync_shards')
        print(res.text)

    return len(cluster_nodes) == len(running_nodes)

if __name__ == '__main__':
  reconsolidate_cluster()
    