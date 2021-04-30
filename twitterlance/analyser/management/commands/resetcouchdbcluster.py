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
    
    def delete_nodes(self):
        print('Deleting cluster nodes...')
        self.wait_for_node(settings.COUCHDB_COORDINATION_NODE)
        for ip in settings.COUCHDB_NODES:
            url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{ip}:5984/_membership'
            res = requests.get(url)
            print(f'Response {ip} {res.text} {res.status_code}')
            for node in res.json().get('cluster_nodes'):
                if ip not in node: 
                    self.wait_for_node(ip)
                    url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{ip}:5984/_node/_local/_nodes/{node}'
                    res = requests.get(url)
                    print(f'Response {ip} {res.text} {res.status_code}')
                    rev = res.json().get('_rev')
                    print(f'Deleting node {node} {rev}')
                    url = f'http://{settings.COUCHDB_USERNAME}:{settings.COUCHDB_PASSWORD}@{ip}:5984/_node/_local/_nodes/{node}?rev={rev}'
                    print(url)
                    res = requests.delete(url)
                    print(f'Response {ip} {res.text} {res.status_code}')

    def handle(self, *args, **options): 
        self.delete_nodes()
        self.stdout.write(self.style.SUCCESS('Successfully initilised CouchDB.'))
            