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
        time.sleep(random.randint(1, 10))  # Delay to avoid the possibility of conflicts
        res = couch.get(f'jobs/search/')
        if res.status_code == 404: 
            print("[search] Have not found the search file in jobs database.")
            return 
        
        doc = res.json()
        status = doc.get('status', 'empty')
        print(f'[search] search status: {status}')
  
        if status != 'ready':
            return  

        print('[search] Search starting...')
        if settings.DJANGO_NODENAME not in doc['nodes']:
            doc['nodes'].append(settings.DJANGO_NODENAME) # Add this instance to nodes list

        # only allow 1 node to run
        doc['status'] = 'running'
        
        print(f'[search] Update job status: {doc}')
        couch.updatedoc(f'jobs/search/', doc)
        
        rate_limit = doc['new_users']
        try:
            rate_limit = int(rate_limit)
        except:
            rate_limit = 1

        print(f'[search] Running on rate limit {rate_limit}')

        try: 
            search_new.run_search(rate_limit)
        except AssertionError: 
            print('[search] User interruptted.')

        print('[search] Job completed.')

        # Job done on this node
        doc = couch.get(f'jobs/search/').json()
        if settings.DJANGO_NODENAME in doc['nodes']:
            doc['nodes'].remove(settings.DJANGO_NODENAME)
        
        print(f'[search] {doc["nodes"]}')

        if len(doc['nodes']) == 0: 
            doc['status'] = 'idle'

        doc['result'] = f'Job done. Last node: {settings.DJANGO_NODENAME}.'
        couch.updatedoc(f'jobs/search/', doc)

    def execute(self):
        try: 
            self.do()
        except Exception as e: 
            print(f'[search] {str(e)}')