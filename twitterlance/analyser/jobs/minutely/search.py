"""
Jobs to run every minute. 
"""

from django.conf import settings
from django.core.cache import caches
from django_extensions.management.jobs import MinutelyJob
from couchdb import couch


class Job(MinutelyJob):
    help = "Node heartbeats."

    def execute(self):
        res = couch.get('jobs/search').json()
        print(res)
        if res['status'] == 'ready':
            res['status'] = 'running'
            couch.put('jobs/search', res)
            run_search(res['new_users'])
            res['status'] = 'idle'
            res['updated_at'] = couch.now()
            couch.put('jobs/search', res)