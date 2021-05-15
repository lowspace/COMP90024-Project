from background_task import background
import subprocess, datetime
from django.conf import settings
from couchdb import couch
from twitter_search.search_new import run_search
from twitter_search.search_update import run_update
# https://django-background-tasks.readthedocs.io/en/latest/



@background(schedule=5)
def heartbeat():
    print('heartbeat')
    res = couch.head(f'nodes/{settings.DJANGO_NODENAME}')
    print(res.json())
    if res.status_code != 200: 
        couch.post(f'nodes/', {'_id': settings.DJANGO_NODENAME, 'heartbeat': 1, 'updated_at':couch.now()})
    else: 
        body = res.json()
        if isinstance(body['heartbeat'], int):
            body['heartbeat'] += 1
        else: 
            body['heartbeat'] = 1
        couch.updatedoc(f'nodes/{settings.DJANGO_NODENAME}', body)

@background(schedule=60)
def user_rank():
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

@background(schedule=60)
def start_stream():
    # TODO: Use registered hostname status and only run on one instance
    pass

@background(schedule=60)
def start_search_job():
    # TODO: Use registered hostname status and its array index to parallelise
    res = couch.get('jobs/search').json()
    print(res)
    if res['status'] == 'ready':
        res['status'] = 'running'
        couch.put('jobs/search', res)
        run_search(res['new_users'])
        res['status'] = 'idle'
        res['updated_at'] = couch.now()
        couch.put('jobs/search', res)

@background(schedule=60)
def start_update_job():
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
