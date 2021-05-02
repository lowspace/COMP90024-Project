# This python script looks for isolated couchdb instances on the current docker host and add them to the couchdb cluster.
# Run on all docker swarm node when couchdb is created or rescaled. 

import requests, time, docker, configparser

help = 'Initialise the databses required by this app'

# Load CouchDB endpoint and credentials
config = configparser.ConfigParser()
try:
    config.read("couchdb.conf")
except:
    print("CouchDB Configuration not found")
COUCHDB_USERNAME = config.get('CouchDB', 'username')
COUCHDB_PASSWORD = config.get('CouchDB', 'password')
COUCHDB_ENDPOINT = config.get('CouchDB', 'endpoint')
REPEAT = int(config.get('CouchDB', 'repeat'))

def reconsolidate_cluster():
    # Get all nodes
    all_nodes = []
    client = docker.from_env()
    networks = client.networks.list(greedy=True)
    for network in networks: 
        if network.name == 'twitterlance_default':
            for container in network.attrs['Containers'].values():
                if 'twitterlance_couchdb' == container['Name'].split('.')[0]:
                    node = 'couchdb@' + container['Name']
                    all_nodes.append(node)

    print(f'All nodes on this machine: {all_nodes}')

    for node in all_nodes: 
        count = 0
        while True:
            url = f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/_local/_nodes/{node}'
            res = requests.put(url, json={})
            if res.json().get('error') == 'conflict':
                print(f'{node} already in cluster')
            else: 
                print(f'{node} {res.text}')
            time.sleep(0.5)
            if count > REPEAT and res.json().get('error') is not None:
                break
            count += 1
            
    # Remove disconnected
    res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_membership')
    cluster_nodes = res.json().get('cluster_nodes') + res.json().get('all_nodes') 
    for node in cluster_nodes: 
        res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/{node}')
        if res.json().get('error') == 'nodedown':
            print(f'Removing {node} due to disconnection.')
            while True:
                res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_active_tasks')
                print(f'Checking active tasks: {res.text}')
                if len(res.json()) == 0 or res.json is None: 
                    break
                else: 
                    print(f'Waiting for tasks to complete: {res.json()}')
                    time.sleep(5)
            res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/_local/_nodes/{node}')
            if res.json().get('_rev') is not None: 
                rev = res.json().get('_rev')
                res = requests.delete(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/_local/_nodes/{node}?rev={rev}')
                print(f'Result: {res.text}')

    res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_membership')
    cluster_nodes = res.json().get('cluster_nodes')
    print(f'Current nodes: {cluster_nodes}')


if __name__ == '__main__':
  reconsolidate_cluster()
  print('Successfully reconsolidated CouchDB cluster.')
    