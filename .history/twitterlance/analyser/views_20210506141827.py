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
#
# class ManagerViewSet(viewsets.ViewSet):
#     # POST analyser/couchdb
#     @action(detail=False, methods=['post'], name="Initialisation")
#     def couchdb(self, request):
#         call_command('initcouchdb')
# >>>>>>> 3753208f46022203ee2f511948de7ccebedff376

t =    {"_id": "_design/test",
  "views": {
    'views': {'wrestling': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'wrestling' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'weights': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'weights' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'skiing': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'skiing' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'water polo': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'water polo' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'volleyball': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'volleyball' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'tennis': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'tennis' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'team handball': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'team handball' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'table tennis': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'table tennis' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'swimming': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'swimming' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'surfing': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'surfing' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'sprinting': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'sprinting' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'skating': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'skating' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'soccer': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'soccer' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'skateboarding': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'skateboarding' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'shooting': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'shooting' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'rugby': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'rugby' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'rowing': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'rowing' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'rodeo': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'rodeo' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'racquetball': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'racquetball' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'squash': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'squash' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'pole vault': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'pole vault' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'running': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'running' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'martial arts': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'martial arts' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'jumps': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'jumps' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'lacrosse': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'lacrosse' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'ice hockey': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'ice hockey' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'jump': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'jump' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'gymnastics': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'gymnastics' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'golf': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'golf' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'football': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'football' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'fishing': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'fishing' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'field hockey': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'field hockey' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'fencing': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'fencing' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'equestrian': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'equestrian' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'diving': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'diving' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'cycling': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'cycling' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'curling': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'curling' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'cheerleading': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'cheerleading' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'canoe': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'canoe' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'kayak': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'kayak' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'bull': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'bull' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'bareback': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'bareback' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'bronc riding': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'bronc riding' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'boxing': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'boxing' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'bowling': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'bowling' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'bobsledding': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'bobsledding' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'luge': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'luge' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'billiards': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'billiards' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'basketball': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'basketball' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'baseball': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'baseball' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'softball': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'softball' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'badminton': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'badminton' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'racing': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'racing' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"},
  'archery': {'reduce': '_count',
   'map': "function (doc) {\n  sport = 'archery' \n if (doc.val.text.toLowerCase().includes(sport))\n   {emit(doc._id, 1); break}}\n}"}},
  "language": "javascript",
  "options": {
    "partitioned": True}}
couch.put('tweetdb/_design/test', body=t)