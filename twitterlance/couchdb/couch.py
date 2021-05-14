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
    res = put(f'{path}?rev={rev}', document)
    if res.status_code == 409 and retries < max_retries: 
        time.sleep(2)
        return upsertdoc(path, document, max_retries, retries + 1)
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

    cities = dict (
        Adelaide= "-34.9998826,138.3309816,40km",
        Sydney = "-33.8559799094,151.20666584,50km",
        Melbourne = "-37.8142385,144.9622775,40km" ,
        Perth = "-32.0391738, 115.6813561, 40km",
        Canberra ="-35.2812958,149.124822,40km",
        Brisbane =  "-27.3812533, 152.713015, 40km",
    )

    # Add necessary data
    for key, value in cities: 
        output.append(post('cities', {'_id': key, 'geocode': value}).json())

    return output

def geocode():
    return get('cities/_all_docs?include_docs=true')