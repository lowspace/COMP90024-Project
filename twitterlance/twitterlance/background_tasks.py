from background_task import background
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