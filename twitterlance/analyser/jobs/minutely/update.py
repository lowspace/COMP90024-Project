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
        print('Update job')
        time.sleep(random.randint(1, 30))  # Delay to avoid the possibility of conflicts
        res = couch.get(f'jobs/update/')
        if res.status_code == 404: 
            print("Have not found the search file in jobs database.")
            return 
        doc = res.json()
        if doc['status'] != 'ready':
            return
        if res.status_code == 200 and len(res.get('rows', [])) == len(doc['nodes']):
            doc['status'] = 'running'
        doc['nodes'].append(settings.DJANGO_NODENAME) # Add this instance to nodes list
        couch.updatedoc(f'jobs/update/', doc)
        # Run the job
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
            print(str(e))