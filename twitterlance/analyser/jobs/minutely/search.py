"""
Jobs to run every minute. 
"""

from django.conf import settings
from django.core.cache import caches
from django_extensions.management.jobs import MinutelyJob
from couchdb import couch
from twitter_search import search_new
import time, random


class Job(MinutelyJob):
    help = "Search Twitter Users (use 'update' for tweets)."

    def do(self):
        print('Search Job')
        time.sleep(random.randint(1, 10))  # Delay to avoid the possibility of conflicts
        res = couch.get(f'jobs/search/')
        if res.status_code == 404: 
            print("Have not found the search file in jobs database.")
            return 
        
        doc = res.json()
        status = doc.get('status', 'empty')
        print(f'Status {status}')
        if status != 'ready':
            return  

        print('Adding to the nodes list...')
        if settings.DJANGO_NODENAME not in doc['nodes']:
            doc['nodes'].append(settings.DJANGO_NODENAME) # Add this instance to nodes list

        # only allow 1 node to run
        doc['status'] = 'running'
        
        print(f'Update job status: {doc}')
        couch.updatedoc(f'jobs/search/', doc)
        
        rate_limit = doc['new_users']
        try:
            rate_limit = int(rate_limit)
        except:
            rate_limit = 1

        print(f'Running on rate limit {rate_limit}')

        search_new.run_search(rate_limit)

        print('Job completed.')

        # Job done on this node
        doc = couch.get(f'jobs/search/').json()
        if settings.DJANGO_NODENAME in doc['nodes']:
            doc['nodes'].remove(settings.DJANGO_NODENAME)
        
        print(doc['nodes'])

        if len(doc['nodes']) == 0: 
            doc['status'] = 'idle'

        doc['result'] = f'Job done. Last node: {settings.DJANGO_NODENAME}.'
        couch.updatedoc(f'jobs/search/', doc)

    def execute(self):
        try: 
            self.do()
        except Exception as e: 
            print(str(e))