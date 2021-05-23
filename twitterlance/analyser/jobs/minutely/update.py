"""
Jobs to run every minute. 
"""

from django.conf import settings
from django.core.cache import caches
from django_extensions.management.jobs import MinutelyJob
from couchdb import couch
from twitter_search import search_update
import requests, time, random


class Job(MinutelyJob):
    help = "Update Twitter."

    def do(self):
        time.sleep(random.randint(1, 10))  # Delay to avoid the possibility of conflicts
        res = couch.get(f'jobs/update/')
        if res.status_code == 404: 
            print("[update] Have not found the search file in jobs database.")
            return 
        doc = res.json()
        if doc['status'] != 'ready':
            return

        all_nodes = couch.get('nodes/_all_docs').json().get('rows', [])

        if settings.DJANGO_NODENAME not in doc['nodes']:
            doc['nodes'].append(settings.DJANGO_NODENAME) # Add this instance to nodes list
        
        if len(all_nodes) == len(doc['nodes']):
            doc['status'] = 'running'

        couch.updatedoc(f'jobs/update/', doc)

        print('[update] Update starting...')
        search_update.run_update()
        # Job done on this node
        doc = couch.get(f'jobs/update/').json()
        if settings.DJANGO_NODENAME in doc['nodes']:
            doc['nodes'].remove(settings.DJANGO_NODENAME)
        if len(doc['nodes']) == 0: 
            doc['status'] = 'idle'
        doc['result'] = f'Job done. Last node: {settings.DJANGO_NODENAME}.'
        couch.updatedoc(f'jobs/update/', doc)

    def execute(self):
        try: 
            self.do()
        except Exception as e: 
            print(f'[update]{str(e)}')