from background_task import background
from couchdb import couch
import subprocess, time

def all():
    user_rank()

@background(schedule=60)
def user_rank():
    res = couch.get('jobs/user_rank')
    if res.status_code == 200 and res.json().get('status') != 'ready':
        return

    subprocess.Popen('spark-submit --master spark://spark:7077 --class endpoint /code/static/spark/sport.py', shell=True)
    doc = {'_id': 'user_rank', 'status': 'running', 'result': 'Job submitted.', 'updated_at':time.ctime()}
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
        doc = {'_id': 'user_rank', 'status': 'done', 'result': 'Job submitted.', 'updated_at':time.ctime()}
        couch.upsertdoc('jobs/user_rank', doc)

