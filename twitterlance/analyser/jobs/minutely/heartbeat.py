"""
Every minute, the current instance will push a heartbeat to couchdb, showing it is alive. The docker service 1 will remove the disconnected nodes. 
"""

from django.conf import settings
from django.core.cache import caches
from django_extensions.management.jobs import MinutelyJob
from couchdb import couch
import requests, sys

class Job(MinutelyJob):
    help = "Node heartbeats."

    def do(self):

        # Add this instance to nodes list
        res = couch.get(f'nodes/{settings.DJANGO_NODENAME}')
        if res.status_code == 404: 
            couch.post(f'nodes/', {'_id': settings.DJANGO_NODENAME, 'heartbeat': 1, 'updated_at':couch.now()})
        else: 
            doc = res.json()
            if isinstance(doc['heartbeat'], int):
                doc['heartbeat'] += 1
            else: 
                doc['heartbeat'] = 1
            couch.updatedoc(f'nodes/{settings.DJANGO_NODENAME}', doc)
        
        # Remove disconnected
        if settings.DJANGO_NODENAME.split('.')[1] != 1:
            return 
        
        to_remove = []
        res = couch.get(f'nodes/_all_docs').json()
        if res.status_code == 200: 
            rows = res['rows']
            for row in rows:
                nodename = row['id']
                try: 
                    res = requests.get(nodename)
                    if res.status_code != 200: 
                        to_remove.append(nodename)
                except: 
                    to_remove.append(nodename)

        for node in to_remove: 
            res = couch.head(f'nodes/{node}')
            res = couch.delete(f'nodes/{node}', res.headers['ETag'])


    def execute(self):
        try: 
            do()
        except Exception as e: 
            sys.stderr.write(str(e))