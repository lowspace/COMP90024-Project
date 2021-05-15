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
        print('heartbeat')
        res = couch.get(f'nodes/{settings.DJANGO_NODENAME}')
        print(res.status_code)
        if res.status_code != 200: 
            couch.post(f'nodes/', {'_id': settings.DJANGO_NODENAME, 'heartbeat': 1, 'updated_at':couch.now()})
        else: 
            body = res.json()
            if isinstance(body['heartbeat'], int):
                body['heartbeat'] += 1
            else: 
                body['heartbeat'] = 1
            couch.updatedoc(f'nodes/{settings.DJANGO_NODENAME}', body)