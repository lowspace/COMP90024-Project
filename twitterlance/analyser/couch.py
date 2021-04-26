import requests, uuid, json
from django.conf import settings

class Couch:
    def __init__(self):
        self.base_url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@localhost:5984'

    def new_id(self):
        return uuid.uuid4().hex

    def get(self, path='', body=''):
        print(f'{self.base_url}/{path}')
        return requests.get(f'{self.base_url}/{path}', json=body)
    
    def put(self, path='', body=''):
        return requests.put(f'{self.base_url}/{path}', json=body)

    def post(self, path='', body=''):
        return requests.post(f'{self.base_url}/{path}', json=body)

    def head(self, path=''):
        return requests.head(f'{self.base_url}/{path}')
