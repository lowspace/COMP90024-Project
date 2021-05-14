from pyspark import SparkContext, SparkConf
from operator import add
from datetime import datetime
import requests

cities = {
    'Sydney': [], 
    'Melbourne': [],
    'Adelaide': [],
    'Canberra': []
}



for city, scores in cities.keys(): 
    rows = []
    res = requests.get(f'http://user:pass@34.87.251.230:80/tiny_tweets/_partition/{city}/_design/xin/_view/sports_score')
    if res.status_code == 200:
        rows = res.json().get('rows')
    conf = SparkConf().setAppName('best user')
    sc = SparkContext(conf=conf)
    scrdd = sc.parallelize(rows)
    cities[city] = scrdd.map(lambda row: (row['key'], row['value'])).reduceByKey(add).sortBy(lambda a: a[1][1], False).collect()


