"""
Jobs to run every minute. 
"""

from django.conf import settings
from django.core.cache import caches
from django_extensions.management.jobs import MinutelyJob
from couchdb import couch
from twitter_stream import stream
import  time, random


class Job(MinutelyJob):
    help = "Streaming Twitter."

    def do(self):
        time.sleep(random.randint(1, 10))  # Delay to avoid the possibility of conflicts
        res = couch.get(f'jobs/stream/')
        if res.status_code == 404: 
            print("Have not found the stream doc in jobs database.")
            return 
        doc = res.json()

        status = doc.get('status', '')

        if status != 'ready':
            return 

        doc['status'] = 'running'
        doc['nodes'].append(settings.DJANGO_NODENAME) # Add this instance to nodes list

        res = couch.put(f'jobs/stream/', doc)
        print(f'Stream starting...')
        
        stream.run()
        # Job done on this node
        doc = couch.get(f'jobs/stream/').json()
        if settings.DJANGO_NODENAME in doc['nodes']:
            doc['nodes'].remove(settings.DJANGO_NODENAME)
        if len(doc['nodes']) == 0: 
            doc['status'] = 'idle'
        doc['result'] = f'Job done. Last node: {settings.DJANGO_NODENAME}.'
        couch.updatedoc(f'jobs/stream/', doc)

    def execute(self):
        try: 
            if '.' in settings.DJANGO_NODENAME and settings.DJANGO_NODENAME.split('.')[1] == '1':
                self.do()
        except Exception as e: 
            print(str(e))