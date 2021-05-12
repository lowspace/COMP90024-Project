from background_task import background
import requests

@background(schedule=5)
def test():
    requests.put('http://user:pass@34.87.251.230:5984/jobs')
    res = requests.get('http://user:pass@34.87.251.230:5984/jobs/search')
    if res.status_code != 200: 
        requests.put('http://user:pass@34.87.251.230:5984/jobs/search')
