import requests, uuid, time, os, json, datetime
from django.conf import settings

# Module with functions serve a Singleton
base_url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_ENDPOINT}'

# Generate a new uuid for CouchDB document
def new_id():
    return uuid.uuid4().hex

class ExceptionResponse: 
    def __init__(self, body, code=200):
        self.body = body
        self.status_code = code
        self.headers = {}
    
    def json(self):
        if isinstance(self.body, dict):
            return self.body
        else: 
            return {'error': self.body}

    def text(self):
        return self.body

# Basic GET request. path is the url after base_url
def get(path='', body=''):
    try:
        return requests.get(f'{base_url}/{path}', json=body)
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

# Basic PUT request. path is the url after base_url
def put(path='', body=''):
    try:
        return requests.put(f'{base_url}/{path}', json=body)
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

# Basic POST request. path is the url after base_url
def post(path='', body=''):
    try:
        return requests.post(f'{base_url}/{path}', json=body)
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

# Basic HEAD request. path is the url after base_url
def head(path=''):
    try:
        return requests.head(f'{base_url}/{path}')
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

def delete(path='', rev=''):
    try:
        return requests.delete(f'{base_url}/{path}?rev={rev}')
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

# Save a single document (dict that has _id as key)
def save(database, document):
    try:
        return requests.put(f'{base_url}/{database}/{document.get("_id")}', json=document)
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

# Save a list of documents (list of dict)
def bulk_save(database, documents):
    try:
        return requests.post(f'{base_url}/{database}/_bulk_docs', json={"docs": documents})
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

# Create a database
def createdb(path='', partition=False, body=''):
    if partition:
        path += '?partitioned=true'
    try:
        return requests.put(f'{base_url}/{path}', json=body)
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

# Create or update with automatic conflict resolution for updates 
def upsertdoc(path='', document={}):
    try:
        res = head(path)
        if res.status_code != 200: 
            return put(path, document)
        else: 
            return updatedoc(path, document)
    except Exception as e: 
        return ExceptionResponse(str(e), 500)
        
# update document with with automatic conflict resolution for updates
# Do not set retries
def updatedoc(path='', document='', max_retries=5, retries=0):
    try:
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
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

def migrate():
    try:
        return do_migrate()
    except Exception as e: 
        return ExceptionResponse(str(e), 500)

# Initialise the necessary databases and design documents
def do_migrate():
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
    output.append(createdb('tokens', False).json())

    cities = dict (
        Adelaide= "-34.9998826,138.3309816,40km",
        Sydney = "-33.8559799094,151.20666584,50km",
        Melbourne = "-37.8142385,144.9622775,40km",
        Perth = "-32.0391738,115.6813561,40km",
        Canberra ="-35.2812958,149.124822,40km",
        Brisbane = "-27.3812533,152.713015,40km",
    )

    # Add necessary data
    for key, value in cities.items(): 
        output.append(post('cities', {'_id': key, 'geocode': value}).json())
        time.sleep(0.5)

    # Add tokens
    output.append(post('tokens/', {'_id': 'Rkupsy9IRz1LZFn5BnW41HieR', 'consumer_key': 'Rkupsy9IRz1LZFn5BnW41HieR', 'consumer_secret': 'AJGztH99Xj8Ch3ueleBd95nUHS2L30tmmvRjiVEpri1qZyAlc4', 'access_token_key': '1383751844057391107-Tw0FTLNESkWFgq5OB9BkvjvlOjETot', 'access_token_secret': '847AbkKGOcEp1SeiR3wNu5xvBgDaUS0EHd9iIeMx6nv50', 'type': 'search'}).json())
    output.append(post('tokens/', {'_id': 'b9UKdOCbro8FfL4bOK95Argnb', 'consumer_key': 'b9UKdOCbro8FfL4bOK95Argnb', 'consumer_secret': '1vSkkEIB4hdBhuTE7BMtvgjdnuq9h755E38bQzhaf0cdcbS90M', 'access_token_key': '1387659560098275331-hgjcBher08GC4QHuz8XYLq9ApNxKZA', 'access_token_secret': 'UVFS6qpTaUAu8WnfuEYiBpqV7VKZTh3Bjmof8s8Whws1E', 'type': 'search'}).json())
    output.append(post('tokens/', {'_id': 'ieAZ39RX3gAFwCtQ3snmo8PjP','consumer_key': 'ieAZ39RX3gAFwCtQ3snmo8PjP', 'consumer_secret': 'QzeLA7P6LgRjZbfCAsJt6WOquh1Qva9jhBV1iJi83AWBCEXVnO', 'access_token_key': '2795545700-0QggHkc4Fa8Z7c4UYSrnmnlK1tYgPYgDu3koDOQ', 'access_token_secret': 'gehAPtKroC9vpcUIdcVAT46ELVOZOTQMhljRO7LI8Xx5N', 'type': 'search'}).json())
    output.append(post('tokens/', {'_id': 'wku1JIpNi4pXukXp510Hzylj2','consumer_key': 'wku1JIpNi4pXukXp510Hzylj2', 'consumer_secret': 'JZPuJKqMZu929iu8XxgTQAOw0up1LLJj6hKUjFDPE4aSNsp1KP', 'access_token_key': '1382968455989583874-9DiykvjpUlnYtq2fJAgScghh9TMBs2', 'access_token_secret': 'k6C6Yx8LNkNp5FtyG55d6WZ0lwePYbAYAmnkg5xOd65G6', 'type': 'stream'}).json())
    print(output)

    # Add default jobs
    output.append(post('jobs/', {'_id': 'search', 'status': 'idle', 'new_users': 0, 'nodes': [], 'result': 'Initialised.', 'updated_at': now()}).json())
    output.append(post('jobs/', {'_id': 'update', 'status': 'idle', 'nodes': [], 'result': 'Initialised.', 'updated_at': now()}).json())
    output.append(post('jobs/', {'_id': 'stream', 'status': 'idle', 'nodes': [], 'result': 'Initialised.', 'updated_at': now()}).json())
    output.append(post('jobs/', {'_id': 'couchdb', 'status': 'done', 'nodes': [], 'result': 'Initialised.', 'updated_at': now()}).json())
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
                print(f'{view} {res.status_code} {res.json()}')
                time.sleep(0.5)
    return output

def geocode():
    try:
        res = get('cities/_all_docs?include_docs=true').json()['rows']
        city_dict = {}
        for row in res:
            doc = row['doc']
            city_dict[doc['_id']] = doc['geocode']
        return city_dict
    except Exception as e: 
        return {}
        
def now():
    return datetime.datetime.now().astimezone(tz=datetime.timezone.utc).strftime('%a %b %d %H:%M:%S %z %Y')