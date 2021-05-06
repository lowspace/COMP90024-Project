from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from django.core.management import call_command
import couchdb.couch as couch
# import twitter_search.search_tweet as search
import twitter_stream.stream as stream
import json
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
        
    @action(detail=False, methods=['get'], name="test python import")
    def test(self, request):
        call_command('startsearch')
        return Response({search.test(): stream.test()})

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
        sports = ['wrestling', 'weights', 'skiing', 'water polo', 'volleyball', 
            'tennis', 'team handball', 'table tennis', 'swimming', 'surfing', 'sprinting', 
            'skating', 'soccer', 'skateboarding', 'shooting', 'rugby', 'rowing', 'rodeo', 
            'racquetball', 'squash', 'pole vault', 'running', 'martial arts', 'jumps', 'lacrosse', 
            'ice hockey', 'jump', 'gymnastics', 'golf', 'football', 'fishing', 'field hockey', 'fencing', 
            'equestrian', 'diving', 'running', 'cycling', 'curling', 'cheerleading', 'canoe', 'kayak', 'bull', 
            'bareback', 'bronc riding', 'boxing', 'bowling', 'bobsledding', 'luge', 'billiards', 'basketball', 
            'baseball', 'softball', 'badminton', 'racing', 'archery']
        count = {}
        for city in ["Melbourne", "Sydney", "Canberra", "Adelaide"]:
            val = Counter() 
            for sport in sports: # get the count of each sport in every city
                res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/{sport}')
                try:
                    val[sport] = res.json()['rows'][0]["value"]
                else:
                    val[sport] = 0
            count[city] = val
        total = Counter() # all sports
        for k in count.keys():
            total += count[k]
        count['total'] = total
        return Response(count)

    @action(detail=False, methods=['get'], name="try")
    def try1(self, request):
        res = couch.get(f'tweetdb/_partition/Melbourne/_design/sports/_view/golf')
        res = res.json()['rows'][0]["value"]
        return Response(res)



#
# class ManagerViewSet(viewsets.ViewSet):
#     # POST analyser/couchdb
#     @action(detail=False, methods=['post'], name="Initialisation")
#     def couchdb(self, request):
#         call_command('initcouchdb')
# >>>>>>> 3753208f46022203ee2f511948de7ccebedff376