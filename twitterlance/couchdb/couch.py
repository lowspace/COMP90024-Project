import requests, uuid, json
from django.conf import settings

# Module with functions serve a Singleton
<<<<<<< HEAD
base_url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_ENDPOINT}:5984'
base_url = f'http://user:pass@h34.87.251.230:5984:5984'
=======
base_url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_ENDPOINT}'
>>>>>>> 54e4b0dbb4869c8937760a50917161bfa017fe2e

# Generate a new uuid for CouchDB document
def new_id():
    return uuid.uuid4().hex

# Basic GET request. path is the url after base_url
<<<<<<< HEAD
def get(path='', body=''): 
    # path = path.lstrip('/')
=======
def get(path='', body=''):
>>>>>>> 54e4b0dbb4869c8937760a50917161bfa017fe2e
    return requests.get(f'{base_url}/{path}', json=body)

# Basic PUT request. path is the url after base_url
def put(path='', body=''):
<<<<<<< HEAD
    # path = path.lstrip('/')
=======
>>>>>>> 54e4b0dbb4869c8937760a50917161bfa017fe2e
    return requests.put(f'{base_url}/{path}', json=body)

# Basic POST request. path is the url after base_url
def post(path='', body=''):
<<<<<<< HEAD
    # path = path.lstrip('/')
=======
>>>>>>> 54e4b0dbb4869c8937760a50917161bfa017fe2e
    return requests.post(f'{base_url}/{path}', json=body)

# Basic HEAD request. path is the url after base_url
def head(path=''):
<<<<<<< HEAD
    # path = path.lstrip('/')
=======
>>>>>>> 54e4b0dbb4869c8937760a50917161bfa017fe2e
    return requests.head(f'{base_url}/{path}')

# Save a single document (dict)
def save(database, document):
    database = database.lstrip('/')
    return requests.put(f'{base_url}/{database}/{document.get("_id")}', json=document)

# Save a list of documents (list of dict)
def bulk_save(database, documents):
    database = database.lstrip('/')
    return requests.post(f'{base_url}/{database}/_bulk_docs', json={"docs": documents})

# Create a databse
def create(path='', partition=False, body=''):
    if partition:
        path += '?partitioned=true'
        print(path)
    return requests.put(f'{base_url}/{path}', json=body)