from pyspark import SparkContext, SparkConf
from operator import add
import requests, time

conf = SparkConf().setAppName('user rank')
sc = SparkContext(conf=conf)

cities = {
    'Sydney': [], 
    'Melbourne': [],
    'Adelaide': [],
    'Canberra': []
}

for city in cities.keys(): 
    res = requests.get(f'http://user:pass@couchdb:5984/tweets/_partition/{city}/_design/sports/_view/sports_score')
    if res.status_code == 200:
        rows = res.json().get('rows')
        scrdd = sc.parallelize(rows)
        rank = scrdd.map(lambda row: (row['key'], row['value'])).reduceByKey(add).sortBy(lambda a: a[1], False)
        cities[city] = rank.collect()[:100]

result = {'_id': 'user_rank', 'result': cities, 'updated_at': time.ctime()}


res = requests.head(f'http://user:pass@couchdb:5984/conclusions')
if res.status_code != 200: 
    requests.put(f'http://user:pass@couchdb:5984/conclusions')

res = requests.head(f'http://user:pass@couchdb:5984/conclusions/user_rank')
if res.status_code != 200: 
    res = requests.post(f'http://user:pass@couchdb:5984/conclusions/',json=result)
    print(res.json())
else: 
    retries = 0
    success = False
    while retries < 5:
        rev = requests.head(f'http://user:pass@couchdb:5984/conclusions/user_rank').headers['ETag'].strip('"')
        updateres = requests.put(f'http://user:pass@couchdb:5984/conclusions/user_rank?rev={rev}',json=result)
        if updateres.status_code == 201:
            success = True
            print(updateres.json())
            break
        else: 
            
            print(updateres.json())
            retries += 1
            time.sleep(2)

