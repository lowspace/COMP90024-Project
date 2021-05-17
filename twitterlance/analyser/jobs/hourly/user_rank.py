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

    # This job only runs on 1 instance
    def execute(self):
        time.sleep(random.randint(1, 30)) # avoid the possibility of couchdb conflicts

        res = couch.get('jobs/user_rank')
        doc = res.json()
        if doc.get('status', None) != 'ready' and len(doc.get('instances', [])) != 0:
            return 
        doc.get('instances').append(settings.DJANGO_HOSTNAME)
        doc.get('status') = 'idle'
        doc.get('result') = 'Job submitted. check 8080.'
        doc.get('updated_at') = couch.now()
        couch.updatedoc('jobs/user_rank', doc)

        subprocess.Popen('spark-submit --master spark://spark:7077 --class endpoint /code/static/spark/sport.py', shell=True)