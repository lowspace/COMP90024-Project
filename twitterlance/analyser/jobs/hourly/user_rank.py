"""
Jobs to run every minute. 
"""
import subprocess, time, random
from django.conf import settings
from django.core.cache import caches
from django_extensions.management.jobs import HourlyJob
from couchdb import couch


class Job(HourlyJob):
    help = "Node heartbeats."

    def execute(self):
        # This job only runs on 1 instance
        if settings.DJANGO_NODENAME.split('.')[1] != '1':
            return

        res = couch.get('jobs/user_rank')
        doc = res.json()
        if doc.get('status', None) != 'ready' and len(doc.get('instances', [])) != 0:
            return 
        doc.get('status') = 'idle'
        doc.get('result') = 'Job submitted. check 8080.'
        doc.get('updated_at') = couch.now()
        couch.updatedoc('jobs/user_rank', doc)

        subprocess.Popen('spark-submit --master spark://spark:7077 --class endpoint /code/static/spark/sport.py', shell=True)