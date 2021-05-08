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

res = requests.get('http://user:pass@127.0.0.1:5984/_all_dbs')
for db in res.json(): 
    res = requests.post(f'http://user:pass@127.0.0.1:5984/{db}/_sync_shards')
    print(res.text)