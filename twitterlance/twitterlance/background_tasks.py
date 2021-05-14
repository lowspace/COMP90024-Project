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

import requests
from twitter_search.search_new import run_search
from twitter_search.search_update import run_update
import datetime 

# https://django-background-tasks.readthedocs.io/en/latest/

@background(schedule=5)
def test():
    requests.put('http://user:pass@34.87.251.230:5984/jobs')
    res = requests.get('http://user:pass@34.87.251.230:5984/jobs/search')
    if res.status_code != 200: 
        requests.put('http://user:pass@34.87.251.230:5984/jobs/search')

@background(schedule=60)
def start_search_job():
    # res['status'] = ['ready', 'running', 'done',]
    res = couch.get('jobs/search').json()
    print(res)
    if res['status'] == 'ready':
        res['status'] = 'running'
        couch.put('jobs/search', res)
        run_search(res['new_users'])
        res['status'] = 'done'
        update_timestamp = datetime.datetime.now().astimezone(tz=datetime.timezone.utc).strftime('%a %b %d %H:%M:%S %z %Y')
        res['updated_at'] = update_timestamp
        couch.put('jobs/search', res)

@background(schedule=60)
def start_update_job():
    # res['status'] = ['wait', 'ready', 'running', 'done',]
    res = couch.get('jobs/search').json()
    print(res)
    if res['status'] == 'ready':
        res['status'] = 'running'
        couch.put('jobs/update', res)
        run_update()
        res['status'] = 'done'
        update_timestamp = datetime.datetime.now().astimezone(tz=datetime.timezone.utc).strftime('%a %b %d %H:%M:%S %z %Y')
        res['updated_at'] = update_timestamp
        couch.put('jobs/update', res)
