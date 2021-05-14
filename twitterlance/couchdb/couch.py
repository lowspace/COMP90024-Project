import requests, uuid, time
from django.conf import settings

# Module with functions serve a Singleton
base_url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_ENDPOINT}'

# Generate a new uuid for CouchDB document
def new_id():
    return uuid.uuid4().hex

# Basic GET request. path is the url after base_url
def get(path='', body=''):
    return requests.get(f'{base_url}/{path}', json=body)

# Basic PUT request. path is the url after base_url
def put(path='', body=''):
    return requests.put(f'{base_url}/{path}', json=body)

# Basic POST request. path is the url after base_url
def post(path='', body=''):
    return requests.post(f'{base_url}/{path}', json=body)

# Basic HEAD request. path is the url after base_url
def head(path=''):
    return requests.head(f'{base_url}/{path}')

# Save a single document (dict that has _id as key)
def save(database, document):
    return requests.put(f'{base_url}/{database}/{document.get("_id")}', json=document)

# Save a list of documents (list of dict)
def bulk_save(database, documents):
    return requests.post(f'{base_url}/{database}/_bulk_docs', json={"docs": documents})

# Create a database
def createdb(path='', partition=False, body=''):
    if partition:
        path += '?partitioned=true'
    return requests.put(f'{base_url}/{path}', json=body)

# Create or update with automatic conflict resolution for updates 
def upsertdoc(path='', document={}):
    res = head(path)
    if res.status_code != 200: 
        return put(path, document)
    else: 
        return updatedoc(path, document)
        

# update document with with automatic conflict resolution for updates
# Do not set retries
def updatedoc(path='', document='', max_retries=5, retries=0):
    res = head(path)
    if res.status_code != 200: 
        return res

    rev = res.headers["ETag"].strip('"')
    while True: 
        res = put(f'{path}?rev={rev}', document)
        if res.status_code == 409 and retries < max_retries: 
            time.sleep(2)
            upsertdoc(path, document, max_retries, retries + 1)
        else: 
            return res

# Initialise the necessary databases and design documents
def migrate():
    output = []

    # Add databases
    output.append(createdb('_users', False).json())
    output.append(createdb('_replicator', False).json())
    output.append(createdb('_global_changes', False).json())
    output.append(createdb('jobs', False).json())
    output.append(createdb('cities', False).json())
    output.append(createdb('userdb', False).json())
    output.append(createdb('tweetdb', True).json())

    # Add necessary data
    output.append(post('cities', {'_id': 'Melbourne'}).json())
    output.append(post('cities', {'_id': 'Sydney'}).json())
    output.append(post('cities', {'_id': 'Brisbane'}).json())
    output.append(post('cities', {'_id': 'Perth'}).json())
    output.append(post('cities', {'_id': 'Adelaide'}).json())
    output.append(post('cities', {'_id': 'Canberra'}).json())

    return output

