import requests, docker, os,configparser

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


def reshard():
    # Get local node
    local_nodes = []
    client = docker.from_env()
    networks = client.networks.list(greedy=True)
    for network in networks: 
        if network.name == 'twitterlance_default':
            for container in network.attrs['Containers'].values():
                if 'twitterlance_couchdb' == container['Name'].split('.')[0]:
                    node = 'couchdb@' + container['Name']
                    local_nodes.append(node)

    print(f'CouchDB node on this host: {local_nodes}')
    assert len(local_nodes) == 1, f'The host should have and only have 1 CouchDB node' 

    local_node = local_nodes[0]

    # Get nodes in cluster
    res = requests.get(f'http://{COUCHDB_USERNAME}:{COUCHDB_PASSWORD}@{COUCHDB_ENDPOINT}/_membership')
    cluster_nodes = res.json().get('cluster_nodes')
    print(f'Current nodes: {cluster_nodes}')

    # Get all local shards 
    try: 
        local_shards = os.listdir('/data/opt/couchdb/data/shards')
    except FileNotFoundError: 
        print('No shard exists on this host.')
        return

    # Update shard metadata
    res = requests.get('http://user:pass@127.0.0.1:5984/_all_dbs')
    for db in res.json(): 
        res = requests.get(f'http://user:pass@127.0.0.1:5984/_node/_local/_dbs/{db}')
        shards = res.json()
        
        if 'by_node' not in shards: 
            continue
        
        # Remove nodes not in cluster
        to_remove = []
        for node in shards['by_node']:
            if node not in cluster_nodes: 
                to_remove.append(node)
        for node in to_remove:
            for shard in shards['by_node'].pop(node, None):
                shards['changelog'].append(['remove', shard, node])

        # Add local node shards list      
        if local_node not in shards['by_node']:   
            shards['by_node'][local_node] = []
        
        # Remove shards not on local database      
        to_remove = []
        for shard in shards['by_node'][local_node]: 
            if shard not in local_shards:
                to_remove.append(shard)
                shards['changelog'].append(['remove', shard, node])
        for r in to_remove:
            shards['by_node'][local_node].remove(r)

        # Add local shards to local node  
        for shard in local_shards:
            shards['by_node'][local_node].append(shard)
            shards['changelog'].append(['add', shard, local_node])
        
        # Rebuild empty node lists by range based on by_node
        shards['by_range'] = {}
        for node in shards['by_node']:
            for shard in shards['by_node'][node]:
                shards['by_range'][shard] = []

        # add nodes to shard-node lists based on by_node
        for node in shards['by_node']:
            for shard in shards['by_node'][node]:
                shards['by_range'][shard].append(node)

        print(f'New Shards: \n{shards}')
        requests.put(f'http://user:pass@127.0.0.1:5984/_node/_local/_dbs/{db}', json=shards)
        print(res.text)


# https://docs.couchdb.org/en/stable/cluster/sharding.html#updating-cluster-metadata-to-reflect-the-new-target-shard-s
if __name__ == '__main__':
    reshard()