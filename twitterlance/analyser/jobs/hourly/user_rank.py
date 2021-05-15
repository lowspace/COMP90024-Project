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
        # TODO: Use registered hostname status and only run on one instance
        res = couch.get('jobs/user_rank')
        if res.status_code == 200 and res.json().get('status') != 'ready':
            return 

        subprocess.Popen('spark-submit --master spark://spark:7077 --class endpoint /code/static/spark/sport.py', shell=True)
        doc = {'_id': 'user_rank', 'status': 'running', 'result': 'Job submitted.', 'updated_at': couch.now()}
        couch.upsertdoc('jobs/user_rank', doc)

        res = couch.get('jobs/user_rank')
        submitted_at = None
        if res.status_code == '200':
            submitted_at = res.json()['updated_at']

        res = couch.get('conclusions/user_rank')
        completed_at = None
        if res.status_code == '200':
            completed_at = res.json()['updated_at']
        
        if None not in [completed_at, submitted_at] and completed_at > submitted_at:
            doc = {'_id': 'user_rank', 'status': 'idle', 'result': 'Job submitted.', 'updated_at': couch.now()}
            couch.upsertdoc('jobs/user_rank', doc)