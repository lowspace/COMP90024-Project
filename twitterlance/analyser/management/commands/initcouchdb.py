import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json, requests, time, docker

class Command(BaseCommand):
    help = 'Initialise the databses required by this app'

    def connect(self):
        self.stdout.write(f'Verifying connection to {settings.COUCHDB_ENDPOINT}...')
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_ENDPOINT}:5984/'
        status = 408
        retries = 0
        while status != 200 and retries < 4:
            try: 
                res = requests.head(url, timeout=10)
                status = res.status_code
                self.stdout.write(f'Response {settings.COUCHDB_ENDPOINT} {res.status_code}')
            except Exception as e:
                self.stdout.write(f'Cannot connect to {settings.COUCHDB_ENDPOINT}: {e}')
            time.sleep(5)
            retries += 1

    def create_db(self, name, partitioned):
        self.stdout.write(f'Creating db {name}')
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_ENDPOINT}:5984/'
        res = requests.head(f'{url}{name}')
        self.stdout.write(f'Response {settings.COUCHDB_ENDPOINT} {res.status_code}')
        if res.status_code == 404:
            if partitioned: 
                res = requests.put(f'{url}{name}?partitioned=true')
            else: 
                res = requests.put(f'{url}{name}')
            self.stdout.write(f'Response {settings.COUCHDB_ENDPOINT} {res.text} {res.status_code}')
            assert res.status_code in [201, 202], f'database "{name}" cannot be created.'
    
    def get_design_geo(self):
        f = open(f'{settings.BASE_DIR}/analyser/design_docs/geo/indexes/box/index.js')
        geo = {
            "_id": "geo",
            "indexes": {
                "box": {
                    "analyzer": "standard",
                    "index": f.read()
                }
            }

        }
        assert geo["indexes"]["box"]["index"] not in [None, '']
        f.close()
        return geo

    def create_design_docs(self):
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_ENDPOINT}:5984/'

        self.stdout.write(f'Creating design document geo...')
        res = requests.head(f'{url}twitter/_design/geo/')
        self.stdout.write(f'Response {settings.COUCHDB_ENDPOINT} {res.status_code}')
        if res.status_code == 404:
            res = requests.put(f'{url}twitter/_design/geo/', json=self.get_design_geo())
            self.stdout.write(f'Response {settings.COUCHDB_ENDPOINT} {res.text} {res.status_code}')
            assert res.status_code in [201, 202], 'design document "geo" cannot be created.'

    def handle(self, *args, **options): 
        self.connect()
        self.create_db('_users', False)
        self.create_db('_replicator', False)
        self.create_db('_global_changes', False)
        self.create_db('tweetdb', True)
        self.create_db('userdb', True)
        self.create_design_docs()
        self.stdout.write(self.style.SUCCESS('Successfully initilised databases.'))
            