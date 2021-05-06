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

t =    {'_id': '_design/sports',
 'views': {'wrestling': {'reduce': '_count',
   'map': "function (doc) {sport = 'wrestling' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'weights': {'reduce': '_count',
   'map': "function (doc) {sport = 'weights' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'skiing': {'reduce': '_count',
   'map': "function (doc) {sport = 'skiing' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'water polo': {'reduce': '_count',
   'map': "function (doc) {sport = 'water polo' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'volleyball': {'reduce': '_count',
   'map': "function (doc) {sport = 'volleyball' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'tennis': {'reduce': '_count',
   'map': "function (doc) {sport = 'tennis' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'team handball': {'reduce': '_count',
   'map': "function (doc) {sport = 'team handball' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'table tennis': {'reduce': '_count',
   'map': "function (doc) {sport = 'table tennis' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'swimming': {'reduce': '_count',
   'map': "function (doc) {sport = 'swimming' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'surfing': {'reduce': '_count',
   'map': "function (doc) {sport = 'surfing' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'sprinting': {'reduce': '_count',
   'map': "function (doc) {sport = 'sprinting' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'skating': {'reduce': '_count',
   'map': "function (doc) {sport = 'skating' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'soccer': {'reduce': '_count',
   'map': "function (doc) {sport = 'soccer' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'skateboarding': {'reduce': '_count',
   'map': "function (doc) {sport = 'skateboarding' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'shooting': {'reduce': '_count',
   'map': "function (doc) {sport = 'shooting' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'rugby': {'reduce': '_count',
   'map': "function (doc) {sport = 'rugby' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'rowing': {'reduce': '_count',
   'map': "function (doc) {sport = 'rowing' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'rodeo': {'reduce': '_count',
   'map': "function (doc) {sport = 'rodeo' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'racquetball': {'reduce': '_count',
   'map': "function (doc) {sport = 'racquetball' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'squash': {'reduce': '_count',
   'map': "function (doc) {sport = 'squash' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'pole vault': {'reduce': '_count',
   'map': "function (doc) {sport = 'pole vault' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'running': {'reduce': '_count',
   'map': "function (doc) {sport = 'running' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'martial arts': {'reduce': '_count',
   'map': "function (doc) {sport = 'martial arts' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'jumps': {'reduce': '_count',
   'map': "function (doc) {sport = 'jumps' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'lacrosse': {'reduce': '_count',
   'map': "function (doc) {sport = 'lacrosse' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'ice hockey': {'reduce': '_count',
   'map': "function (doc) {sport = 'ice hockey' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'jump': {'reduce': '_count',
   'map': "function (doc) {sport = 'jump' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'gymnastics': {'reduce': '_count',
   'map': "function (doc) {sport = 'gymnastics' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'golf': {'reduce': '_count',
   'map': "function (doc) {sport = 'golf' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'football': {'reduce': '_count',
   'map': "function (doc) {sport = 'football' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'fishing': {'reduce': '_count',
   'map': "function (doc) {sport = 'fishing' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'field hockey': {'reduce': '_count',
   'map': "function (doc) {sport = 'field hockey' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'fencing': {'reduce': '_count',
   'map': "function (doc) {sport = 'fencing' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'equestrian': {'reduce': '_count',
   'map': "function (doc) {sport = 'equestrian' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'diving': {'reduce': '_count',
   'map': "function (doc) {sport = 'diving' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'cycling': {'reduce': '_count',
   'map': "function (doc) {sport = 'cycling' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'curling': {'reduce': '_count',
   'map': "function (doc) {sport = 'curling' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'cheerleading': {'reduce': '_count',
   'map': "function (doc) {sport = 'cheerleading' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'canoe': {'reduce': '_count',
   'map': "function (doc) {sport = 'canoe' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'kayak': {'reduce': '_count',
   'map': "function (doc) {sport = 'kayak' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'bull': {'reduce': '_count',
   'map': "function (doc) {sport = 'bull' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'bareback': {'reduce': '_count',
   'map': "function (doc) {sport = 'bareback' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'bronc riding': {'reduce': '_count',
   'map': "function (doc) {sport = 'bronc riding' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'boxing': {'reduce': '_count',
   'map': "function (doc) {sport = 'boxing' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'bowling': {'reduce': '_count',
   'map': "function (doc) {sport = 'bowling' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'bobsledding': {'reduce': '_count',
   'map': "function (doc) {sport = 'bobsledding' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'luge': {'reduce': '_count',
   'map': "function (doc) {sport = 'luge' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'billiards': {'reduce': '_count',
   'map': "function (doc) {sport = 'billiards' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'basketball': {'reduce': '_count',
   'map': "function (doc) {sport = 'basketball' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'baseball': {'reduce': '_count',
   'map': "function (doc) {sport = 'baseball' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'softball': {'reduce': '_count',
   'map': "function (doc) {sport = 'softball' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'badminton': {'reduce': '_count',
   'map': "function (doc) {sport = 'badminton' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'racing': {'reduce': '_count',
   'map': "function (doc) {sport = 'racing' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"},
  'archery': {'reduce': '_count',
   'map': "function (doc) {sport = 'archery' if (doc.val.text.toLowerCase().includes(sport)) {emit(doc._id, 1);}}"}},
 'language': 'javascript',
 'options': {'partitioned': True}}

couch.put('tweetdb/_design/sports', body=t)