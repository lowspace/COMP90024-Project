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
        # TODO: Use registered hostname status and its array index to parallelise
        res = couch.get('jobs/search').json()
        print(res)
        if res['status'] == 'ready':
            res['status'] = 'running'
            couch.put('jobs/update', res)
            run_update()
            res['status'] = 'idle'
            res['updated_at'] = couch.now()
            couch.put('jobs/update', res)