from background_task import background
import requests, subprocess

@background(schedule=5)
def test():
    requests.put('http://user:pass@34.87.251.230:5984/jobs')
    res = requests.get('http://user:pass@34.87.251.230:5984/jobs/search')
    if res.status_code != 200: 
        requests.put('http://user:pass@34.87.251.230:5984/jobs/search')

@background(schedule=86400)
def spark_best_users():
    result = subprocess.Popen('spark-submit --master spark://spark:7077 --class endpoint /code/static/spark/sport.py', shell=True)