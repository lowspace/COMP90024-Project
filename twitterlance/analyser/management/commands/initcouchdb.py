import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json, requests, time

class Command(BaseCommand):
    help = 'Initialise the databses required by this app'

    def wait_for_node(self, ip):
        print(f'Verifying connection to {ip}...')
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{ip}:5984/'
        status = 408
        while status != 200:
            try: 
                res = requests.head(url, timeout=10)
                status = res.status_code
                print(f'Response {ip} {res.status_code}')
            except Exception as e:
                print(f'Cannot connect to {ip}: {e}')
                time.sleep(5)

    def enable_cluster_mode(self):
        print(f'Enabling cluster mode...')
        self.wait_for_node(settings.COUCHDB_COORDINATION_NODE)
        node_count = len(settings.COUCHDB_NODES)
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_cluster_setup'
        body = {"action": "enable_cluster", "bind_address":"0.0.0.0", "username": settings.COUCHDB_USERNAME, "password": settings.COUCHDB_PASSWORD, "node_count": node_count}
        res = requests.post(url, json=body)
        print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.text} {res.status_code}')
    
    def add_node(self, ip):
        print(f'Adding node {ip} to cluster...')
        self.wait_for_node(ip)
        self.wait_for_node(settings.COUCHDB_COORDINATION_NODE)
        node_count = len(settings.COUCHDB_NODES)
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_cluster_setup'
        body = {"action": "enable_cluster", "bind_address":"0.0.0.0", "username": settings.COUCHDB_USERNAME, "password": settings.COUCHDB_PASSWORD, "port": 5984, "node_count": node_count, "remote_node": ip, "remote_current_user": settings.COUCHDB_USERNAME, "remote_current_password": settings.COUCHDB_PASSWORD }
        res = requests.post(url, json=body)
        print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.text} {res.status_code}')
        
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_node/_local/_nodes/couchdb@{ip}'
        requests.put(url, json={})
        print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.text} {res.status_code}')
    
    def finish_cluster_setup(self):
        print('Finishing cluster setup...')
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_cluster_setup'
        res = requests.get(url)
        print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.text} {res.status_code}')
        if res.json().get('state') != 'cluster_enabled':
            res = requests.post(url, json={"action": "finish_cluster"})
            print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.text} {res.status_code}')
    
    def init_default_cluster(self):
        print('Initialising cluster mode...')
        self.enable_cluster_mode()

        # Add default nodes
        for ip in settings.COUCHDB_NODES:
            if ip != settings.COUCHDB_COORDINATION_NODE:
                self.add_node(ip)
        
        self.finish_cluster_setup()

    def create_db(self, name):
        print(f'Creating db {name}')
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/'
        res = requests.head(f'{url}{name}')
        print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.status_code}')
        if res.status_code == 404:
            res = requests.put(f'{url}{name}')
            print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.text} {res.status_code}')
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
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/'

        print(f'Creating design document geo...')
        res = requests.head(f'{url}twitter/_design/geo/')
        print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.status_code}')
        if res.status_code == 404:
            res = requests.put(f'{url}twitter/_design/geo/', json=self.get_design_geo())
            print(f'Response {settings.COUCHDB_COORDINATION_NODE} {res.text} {res.status_code}')
            assert res.status_code in [201, 202], 'design document "geo" cannot be created.'

    def handle(self, *args, **options): 

        self.init_default_cluster()
        self.create_db('_users')
        self.create_db('_replicator')
        self.create_db('_global_changes')
        self.create_db('twitter')
        self.create_design_docs()
        self.stdout.write(self.style.SUCCESS('Successfully initilised CouchDB.'))
            