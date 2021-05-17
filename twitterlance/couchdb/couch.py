import requests, uuid, time, os, json, datetime
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

def delete(path='', rev=''):
    return requests.delete(f'{base_url}/{path}?rev={rev}')

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
        return updatedoc(path, document, max_retries, retries + 1)
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
    output.append(createdb('nodes', False).json())
    output.append(createdb('cities', False).json())
    output.append(createdb('users', False).json())
    output.append(createdb('tweets', True).json())

    cities = dict (
        Adelaide= "-34.9998826,138.3309816,40km",
        Sydney = "-33.8559799094,151.20666584,50km",
        Melbourne = "-37.8142385,144.9622775,40km" ,
        Perth = "-32.0391738, 115.6813561, 40km",
        Canberra ="-35.2812958,149.124822,40km",
        Brisbane =  "-27.3812533, 152.713015, 40km",
    )

    # Add necessary data
    for key, value in cities.items(): 
        output.append(post('cities', {'_id': key, 'geocode': value}).json())
        time.sleep(0.5)

    # Add default jobs
    output.append(post('jobs/', {'_id': 'search', 'status': 'idle', 'new_users': 0, 'nodes': [], 'result': 'Initialised.', 'updated_at': now()}).json())
    output.append(post('jobs/', {'_id': 'update', 'status': 'idle', 'nodes': [], 'result': 'Initialised.', 'updated_at': now()}).json())
    output.append(post('jobs/', {'_id': 'stream', 'status': 'idle', 'nodes': [], 'result': 'Initialised.', 'updated_at': now()}).json())
    output.append(post('jobs/', {'_id': 'couchdb', 'status': 'ready', 'nodes': [], 'result': 'Initialised.', 'updated_at': now()}).json())
    print(output)

    # Upload views
    couch_path = os.path.join(settings.STATICFILES_DIRS[0], 'couch')
    for file_name in os.listdir(couch_path):
        if file_name.endswith("_view.json"):
            database = file_name.split('__')[0]
            view = file_name.split('__')[1]
            file_path = os.path.join(couch_path, file_name)
            with open(file_path, 'r') as f:
                f = json.load(f)
                print(f'Uploading view {view}')
                res = put(f'{database}/_design/{view}', body=f)
                output.append(res.json())
                print(f'{view} {res.status_code}')
                time.sleep(0.5)
    return output

def geocode():
    res = get('cities/_all_docs?include_docs=true').json()['rows']
    city_dict = {}
    for row in res:
        doc = row['doc']
        city_dict[doc['_id']] = doc['geocode']
    return city_dict

def now():
    return datetime.datetime.now().astimezone(tz=datetime.timezone.utc).strftime('%a %b %d %H:%M:%S %z %Y')