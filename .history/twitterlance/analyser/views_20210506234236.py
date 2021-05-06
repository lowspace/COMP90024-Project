from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from django.core.management import call_command
# from django.http import
import couchdb.couch as couch
# import twitter_search.search_tweet as search
import twitter_stream.stream as stream
import json
from django.shortcuts import HttpResponse
from collections import Counter

# https://www.django-rest-framework.org/api-guide/viewsets/
# https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.QueryDict.urlencode
class TweetViewSet(viewsets.ViewSet):

    # GET analyser/tweets?options 
    # Add include_docs=true
    def list(self, request):
        url = f'tweetdb/_all_docs'
        if len(request.query_params) > 0: 
            url += f'?{request.query_params.urlencode()}'
        res = couch.get(url)
        return Response(res.json())

    # GET analyser/tweets/:id
    def retrieve(self, request, pk=None):
        res = couch.get(f'tweetdb/{pk}')
        return Response(couch.get('twitter',pk).json())

    # GET analyser/tweets/stats
    @action(detail=False, methods=['get'], name="Get the stats of tweets")
    def stats(self, request):
        count = {}
        for city in ["Melbourne", "Sydney", "Canberra", "Adelaide"]:
            res = couch.get(f'tweetdb/_partition/{city}')
            count[city] = res.json()["doc_count"]
        count["total_tweets"] = sum(count.values())
        # count["res"] = Response({"tweet_stats": 12312})
        return Response({"tweet_stats": count})

    # GET analyser/tweets/box_tweets?lat_min=-9.1457534&lat_max=-0.4000327&lon_min=134.505904&lon_max=141.0549412
    @action(detail=False, methods=['get'], name="Get Tweets within box")
    def box_tweets(self, request):
        if request.query_params is None:
            return Response({"error": "query is missing"})
        params = request.query_params
        lon_min = params.get('lon_min')
        lon_max = params.get('lon_max')
        lat_min = params.get('lat_min')
        lat_max = params.get('lat_max')
        if None in [lon_min, lon_max, lat_min, lat_max]:
            return Response({"error": f"lon_min, lon_max, lat_min, lat_max are missing: {[lon_min, lon_max, lat_min, lat_max]}"})
        query = f'lat_min:[{lat_min} TO 0] AND lat_max:[-90 TO {lat_max}] AND lon_min:[{lon_min} TO 180] AND lon_max:[0 TO {lon_max}]'
        res = couch.get(f'twitter/_design/geo/_search/box?q={query}')
        return Response({'total_rows': int(res.json()['total_rows'])})

    # GET analyser/tweets/demo
    @action(detail=False, methods=['get'], name="demo")
    def demo(self, request):
        var = {'twitter':6666,'user':606,'sport':99}
        return HttpResponse(json.dumps(var))

    @action(detail=False, methods=['get'], name="demo time")
    def demotime(self, request):
        time1 = time.strftime("%a %b %d %H:%M:%S %Y", time.localtime())
        print(time1)
        return HttpResponse(json.dumps(time1))

    # GET analyser/tweets/sum
    @action(detail=False, methods=['get'], name="Xin test ")
    def sum(self, request):
        res = couch.get('tiny_tweets/_partition/Melbourne/_design/simon/_view/new-view')
        return Response({'a':res.json()})
    
    # GET sport related tweets
    @action(detail=False, methods=['get'], name="sport tweets total")
    def sports(self, request):
        res = couch.get('tweetdb/_partition/Melbourne/_design/filter/_view/new-view')
        return Response(res.json())
   
    # GET a month of tweets
    @action(detail=False, methods=['get'], name="month tweets total")
    def month(self, request):
        res = couch.get('twitters/_design/time/_view/timefilt')
        return Response(res.json())
    
class UserViewSet(viewsets.ViewSet):

    # GET analyser/tweets?options 
    # Add include_docs=true
    def list(self, request):
        url = f'userdb/_all_docs'
        if len(request.query_params) > 0: 
            url += f'?{request.query_params.urlencode()}'
        res = couch.get(url)
        return Response(res.json())

    # GET analyser/users/stats
    @action(detail=False, methods=['get'], name="Get the stats of users")
    def stats(self, request):
        count = {}
        for city in ["mel", "syd", "cbr", "adl"]:
            res = couch.get(f'userdb/_design/wei/_view/{city}')
            # count[city] = res.json()
            count[city] = res.json()["total_rows"]
        count["total_users"] = sum(count.values())
        count['info'] = couch.get(f'userdb/_design/wei').json()
        count['test'] = Response({"asf": 123}).data
        return Response({"user_stats": count})

class SportViewSet(viewsets.ViewSet):

    # GET analyser/sports/static_stats
    @action(detail=False, methods=['get'], name="Get the static_stats of sports")
    def static_stats(self, request):
        count = {}
        for city in ["Melbourne", "Sydney", "Canberra", "Adelaide"]:
            res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/total')
            val[sport] = res.json()['rows'][0]["value"]
            count[city] = val
        total = Counter() # all sports
        for k in count.keys():
            total += count[k]
        t2 = time.time()
        count['total'] = total
        count['time'] = t2 - t1
        return Response(count)

    @action(detail=False, methods=['get'], name="try")
    def try1(self, request):
        res = couch.get(f'tweetdb/_partition/Melbourne/_design/sports/_view/total')
        res = res.json()
        return Response(res)

class AurinViewSet(viewsets.ViewSet):
    def list(self, request):
        url = f'aurin/_all_docs'
        if len(request.query_params) > 0: 
            url += f'?{request.query_params.urlencode()}'
        res = couch.get(url)
        return Response(res.json())

    # Get /analyser/aurin/aurin/
    @action(detail=False, methods=['get'], name="Get aurin")
    def aurin(self,request):
        #res = requests.get("http://34.87.251.230:5984/aurin/_design/xin/_view/aurinInfo")
        res = couch.get(f'aurin/_design/xin/_view/aurinInfo')
        return Response(res.json())


class YearlySportsTweetsViewSet(viewsets.ViewSet):
    def list(self, request):
        url = f'aurin/_all_docs'
        if len(request.query_params) > 0: 
            url += f'?{request.query_params.urlencode()}'
        res = couch.get(url)
        return Response(res.json())
    
    @action(detail=False, methods=['get'], name="Get yearly sports tweets")
    def sport_tweet_yearly(self, request):
        count = {}
        for city in ["Melbourne", "Sydney", "Canberra", "Adelaide"]:
            for year in [2019,2020,2021]:
                res = couch.get(f'tiny_tweets/_partition/{city}/_design/xin/_view/sportsTweets{year}_total')
                #res = requests.get(f"http://34.87.251.230:5984/tiny_tweets/_partition/{city}/_design/xin/_view/sportsTweets2019_total")
                value = res.json()["rows"]
                if value:
                    count[city][year] = res.json()["rows"][0]["value"]
                else:
                    count[city][year]=0
        count[f"total_sports_tweets"] = sum(count.values())
        #count['info'] = couch.get(f'tiny_tweets/_design/xin').json()
        return Response(count)
        


#
# class ManagerViewSet(viewsets.ViewSet):
#     # POST analyser/couchdb
#     @action(detail=False, methods=['post'], name="Initialisation")
#     def couchdb(self, request):
#         call_command('initcouchdb')
