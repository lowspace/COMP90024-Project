"""
Jobs to run every minute. 
"""

from django.conf import settings
from django.core.cache import caches
from django_extensions.management.jobs import MinutelyJob
from couchdb import couch
from twitter_search import search_new
import requests, time, random


class Job(MinutelyJob):
    help = "Node heartbeats."

    def do(self):
        time.sleep(random.randint(1, 30))  # Delay to avoid the possibility of conflicts
        res = couch.get(f'jobs/search/')
        if res.status_code == 404: 
            print("Have not found the search file in jobs database.")
            return 
        doc = res.json()
        if doc['status'] != 'ready':
            return
        doc['status'] = 'running'
        doc['nodes'].append(settings.DJANGO_NODENAME) # Add this instance to nodes list
        couch.updatedoc(f'jobs/search/', doc)
        # Run the job
        rate_limit = doc['new_users']
        try:
            rate_limit = int(rate_limit)
        except:
            rate_limit = 1
        search_new.run_search(rate_limit)
        # Job done on this node
        doc = couch.get(f'jobs/search/').json()
        if settings.DJANGO_NODENAME in doc['nodes']:
            doc['nodes'].remove(settings.DJANGO_NODENAME)
        if len(doc['nodes']) == 0: 
            doc['status'] = 'idle'
        doc['result'] = f'Job done. Last node: {settings.DJANGO_NODENAME}.'
        couch.updatedoc(f'jobs/search/', doc)

    def execute(self):
        try: 
            do()
        except Exception as e: 
            sys.stderr.write(str(e))