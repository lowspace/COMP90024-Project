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
    help = "Search Twitter."

    def do(self):
        print('Search Job')
        time.sleep(random.randint(1, 30))  # Delay to avoid the possibility of conflicts
        res = couch.get(f'jobs/search/')
        if res.status_code == 404: 
            print("Have not found the search file in jobs database.")
            return 
        
        print(f'Search Job {res.status_code}')
        doc = res.json()
        status = doc.get('status', 'empty')
        all_nodes = len(doc['nodes'])
        print(f'Status {status}')
        if status != 'ready':
            return  

        print('Adding to the nodes list...')
        res = couch.get('nodes/_all_docs')
        if settings.DJANGO_NODENAME not in doc['nodes']:
            doc['nodes'].append(settings.DJANGO_NODENAME) # Add this instance to nodes list

        # Check if all nodes are running
        job_nodes = len(res.json().get('nodes', []))
        print(f'all nodes: {all_nodes} job nodes: {job_nodes}')
        if res.status_code == 200 and job_nodes == all_nodes:
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
        if len(doc['nodes']) == 0: 
            doc['status'] = 'idle'
        doc['result'] = f'Job done. Last node: {settings.DJANGO_NODENAME}.'
        couch.updatedoc(f'jobs/search/', doc)

    def execute(self):
        try: 
            self.do()
        except Exception as e: 
            print(str(e))