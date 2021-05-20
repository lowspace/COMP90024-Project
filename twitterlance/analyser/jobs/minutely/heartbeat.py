
from django.conf import settings
from django.core.cache import caches
from django_extensions.management.jobs import MinutelyJob
from couchdb import couch
import requests, sys

# Every minute, the current instance will push a heartbeat to couchdb, showing it is alive. The docker service 1 will remove the disconnected nodes. 
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
            doc['updated_at'] = couch.now()
            couch.updatedoc(f'nodes/{settings.DJANGO_NODENAME}', doc)
        
        task_slot = settings.DJANGO_NODENAME.split('.')[1]

        # Remove disconnected
        if task_slot != '1':
            return 
        
        to_remove = []
        res = couch.get(f'nodes/_all_docs')
        if res.status_code == 200: 
            rows = res.json()['rows']
            for row in rows:
                nodename = row['id']
                try: 
                    res = requests.get(f'http://{nodename}')
                except: 
                    print(f'{nodename} cannot be connected.')
                    to_remove.append(nodename)


        for node in to_remove: 
            res = couch.head(f'nodes/{node}')
            rev = res.headers['ETag'].replace('\"', '')
            res = couch.delete(f'nodes/{node}', rev)


    def execute(self):
        try: 
            self.do()
        except Exception as e: 
            print(str(e))