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

    print(f'All nodes: {all_nodes}')

    for node in all_nodes: 
        repeat = 5
        count = 0
        while True:
            url = f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_node/_local/_nodes/{node}'
            res = requests.put(url, json={})
            print(f'{url} {res.json()}')
            time.sleep(1)
            if count > repeat and res.json().get('error') is not None:
                break
            count += 1
    
    # Get cluster nodes
    res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_membership')
    cluster_nodes = res.json().get('cluster_nodes')
    print(f'Cluster nodes: {cluster_nodes}')


if __name__ == '__main__':
  reconsolidate_cluster()
  print('Successfully reconsolidated CouchDB cluster.')
    