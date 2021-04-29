import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json, requests, time
import couchdb.couch as couch

class Command(BaseCommand):
    help = 'Initialise the databses required by this app'

    def wait_for_node(self, ip):
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{ip}:5984/'
        status = 408
        while status != 200:
            try: 
                res = requests.head(url, timeout='10')
                status = res.status_code
                print(f'{ip} response {status}')
            except:
                print(f'Cannot connect to {ip}')
                time.sleep(5)
            

    def enable_cluster_mode_on_master(self):
        self.wait_for_node(settings.COUCHDB_COORDINATION_NODE)
        node_count = len(settings.COUCHDB_NODES)
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_cluster_setup'
        body = {"action": "enable_cluster", "bind_address":"0.0.0.0", "username": settings.COUCHDB_USERNAME, "password": settings.COUCHDB_PASSWORD, "node_count": node_count}
        res = requests.post(url, json=body)
        

    
    def add_node(self, ip):
        self.wait_for_node(ip)
        node_count = len(settings.COUCHDB_NODES)
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_cluster_setup'
        body = {"action": "enable_cluster", "bind_address":"0.0.0.0", "username": settings.COUCHDB_USERNAME, "password": settings.COUCHDB_PASSWORD, "port": 5984, "node_count": node_count, "remote_node": ip, "remote_current_user": settings.COUCHDB_USERNAME, "remote_current_password": settings.COUCHDB_PASSWORD }
        requests.post(url, json=body)
        
        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_cluster_setup'
        body = {"action": "add_node", "host": ip, "port": 5984, "username": settings.COUCHDB_USERNAME, "password": settings.COUCHDB_PASSWORD}
        requests.post(url, json=body)

        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_cluster_setup'
        body = {"action": "finish_cluster"}
        requests.post(url, json=body)

        url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{settings.COUCHDB_COORDINATION_NODE}:5984/_membership'
        res = requests.get(url)
        assert len(res.json().get('cluster_nodes')) == node_count, f'Failed to add node {ip}' 
    
    def init_cluster_mode(self):
        self.enable_cluster_mode_on_master()
        node_count = len(settings.COUCHDB_NODES)
        for ip in settings.COUCHDB_NODES:
            if ip != settings.COUCHDB_COORDINATION_NODE:
                self.add_node(ip)
            
    
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
    
    def initialised(self):
        # Already initialised? 
        self.wait_for_node(settings.COUCHDB_ENDPOINT)
        try: 
            res = couch.head('init')
            if res.status_code in [200, 201]:
                return True
            else: 
                res = couch.put('init')
                assert res.status_code in [200, 201], 'database "init" cannot be created: ' + res.text
        except requests.exceptions.ConnectionError: 
            print("Unable to connect to CouchDB")
        return False

    def create_db(self, name):
        # Create twitter database
        res = couch.head(name)
        if res.status_code == 404:
            res = couch.put(name)
            assert res.status_code in [200, 201], f'database "{name}" cannot be created: ' + res.text
        elif res.status_code == 200: 
            print(f'{name} already exists.')
        else: 
            raise Exception('error code ' + res.status_code)
    
    def create_design_docs(self):
        # Create design documents
        res = couch.head(f'twitter/_design/geo/')
        if res.status_code == 404:
            res = couch.put(f'twitter/_design/geo/', body=self.get_design_geo())
            assert res.status_code in [200, 201], 'design document "geo" cannot be created: ' + res.text
        elif res.status_code != 200: 
            raise Exception(res.status_code)

    def handle(self, *args, **options): 
        if self.initialised(): 
            return True
        self.init_cluster_mode()
        self.create_db('_users')
        self.create_db('_replicator')
        self.create_db('twitter')
        self.create_design_docs()
        self.stdout.write(self.style.SUCCESS('Successfully initilised design documents'))