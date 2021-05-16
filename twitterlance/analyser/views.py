from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from django.shortcuts import HttpResponse
from django.conf import settings 
from collections import Counter
import json, time, os
import couchdb.couch as couch

# https://www.django-rest-framework.org/api-guide/viewsets/
# https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.QueryDict.urlencode
class TweetViewSet(viewsets.ViewSet):

    # GET analyser/sports/
    def list(self, request):
        actions = {
            'tweets/:id': 'Get single tweet',
            'stats': 'Get the stats of tweets',
            'sports': 'sport tweets total'
        }
        return Response(actions)

    # GET analyser/tweets/:id
    def retrieve(self, request, pk=None):
        res = couch.get(f'tweetdb/{pk}')
        return Response(couch.get('twitter', pk).json())

    # GET analyser/tweets/stats/
    @action(detail=False, methods=['get'], name="Get the stats of tweets")
    def stats(self, request):
        count = {}
        for city in couch.geocode().keys():
            res = couch.get(f'tweetdb/_partition/{city}')
            count[city] = res.json()["doc_count"]
        count["total_tweets"] = sum(count.values())
        return HttpResponse(json.dumps({"tweet_stats": count}))
    
    # GET analyser/tweets/sports/ sport related tweets
    @action(detail=False, methods=['get'], name="sport tweets total")
    def sports(self, request):
        # count = 0
        res1 = {}
        for city in couch.geocode().keys():
            # res = couch.get(f'tweetdb/_partition/{city}/_design/filter/_view/new-view')
            res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/total')
            res1[city]=res.json()['rows'][0]["value"]
            # count += res.json()['rows'][0]["value"]
        return HttpResponse(json.dumps(res1))
    
class UserViewSet(viewsets.ViewSet):

    # GET analyser/users/
    def list(self, request):
        actions = {
            'stats': 'Stats of users.',
            'rank': 'Get the sporst enthusiasts rank'
        }
        return Response(actions)

    # GET analyser/users/stats
    @action(detail=False, methods=['get'], name="Get the stats of users")
    def stats(self, request):
        t1 = time.time()
        count = {}
        for city in couch.geocode().keys():
            print(city)
            res = couch.get(f'userdb/_design/cities/_view/{city}')
            # count[city] = res.json()["doc_count"]
            if res.json()['rows']:
                count[city] = res.json()['rows'][0]["value"]   
        count["total_users"] = sum(count.values())
        t2 = time.time()
        count["time"] = t2 - t1
        return Response({"user_stats": count})

    # GET analyser/users/rank
    @action(detail=False, methods=['get'], name="Get the rank of the enthusiasts")
    def rank(self, request):
        res = couch.get('conclusions/user_rank')
        return Response(res.json())

class SportViewSet(viewsets.ViewSet):

    # GET analyser/sports/
    def list(self, request):
        actions = {
            'stats_all': 'All sport counts in all cities cross all time.',
            ':year': 'All sport counts in all cities cross in the year number',
            'rank_top3': 'Top 3 sports in all cities cross all time.',
            'yearly_stats': 'Sport relevant tweets num of each year in all cities.'
        }
        return Response(actions)

    # GET analyser/sports/stats_all
    @action(detail=False, methods=['get'], name="Get the static_stats of sports")
    def stats_all(self, request):
        t1 = time.time()
        count = {}
        sum_all = {}
        for city in couch.geocode().keys():
            res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/total')
# <<<<<<< HEAD
#             res = Counter(res.json()['rows'][0]["value"])
#             sum_all[city] = sum(res.values())
#             count[city] = res
#         total = Counter()  # all sports
# =======
            if res.json()['rows']:
                res = Counter(res.json()['rows'][0]["value"])
                sum_all[city] = sum(res.values())
                count[city] = res
        total = Counter() # all sports
        for k in count.keys():
            total += count[k]
        count['total'] = total
        sum_all['total'] = sum(sum_all.values())
        count['sum'] = sum_all
        t2 = time.time()
        count["time"] = t2 - t1
        return HttpResponse(json.dumps(count))

    # GET analyser/sports/rank_top3
    @action(detail=False, methods=['get'], name="Get the top 3 sports in each city across all time")
    def rank_top3(self, request):
        count = {}
        for city in couch.geocode().keys():
            res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/total')
            if res.json()['rows']:
                res = Counter(res.json()['rows'][0]["value"])
                top3 = {}
                for i in res.most_common(3):
                    top3[i[0]] = i[1]
                count[city] = top3
        return HttpResponse(json.dumps(count))

    # GET analyser/sports/stats_yearly
    @action(detail=False, methods=['get'], name="Get the 2019, 2020, 2021 tweets of sports")
    def stats_yearly(self, request):
        count = {}
        for city in ["Melbourne", "Sydney", "Canberra", "Adelaide"]:
            time_line = {}
            for time_stamp in ['2019', '2020', '2021']:
                res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/{time_stamp}')
                res = Counter(res.json()['rows'][0]["value"])
                time_line[time_stamp] = sum(res.values())
            count[city] = time_line
        return HttpResponse(json.dumps(count))

    # GET analyser/sports/rank_top3
    @action(detail=False, methods=['get'], name="Get the top 3 sports in each city across all time")
    def rank_top3(self, request):
        count = {}
        for city in ["Melbourne", "Sydney", "Canberra", "Adelaide"]:
            res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/total')
            res = Counter(res.json()['rows'][0]["value"])
            top3 = {}
            for i in res.most_common(3):
                top3[i[0]] = i[1]
            count[city] = top3
        return HttpResponse(json.dumps(count))

    # GET analyser/sports/yearly_stats
    @action(detail=False, methods=['get'], name="Get the 2019, 2020, 2021 tweets of sports in each city")
    def yearly_stats(self, request):
        count = {}
        for city in couch.geocode().keys():
            time_line = {}
            for time_stamp in ['2019', '2020', '2021']:
                res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/{time_stamp}')
                if res.json()['rows']:
                    res = Counter(res.json()['rows'][0]["value"])
                    time_line[time_stamp] = sum(res.values())
            count[city] = time_line
        return HttpResponse(json.dumps(count))

    # GET analyser/sports/:year Get the year tweets of sports
    def retrieve(self, request, pk=None):
        count = {}

        if pk is None or not isinstance(pk, int):
            return Response(0)
        else: 
            pk = int(pk)

        for city in ["Melbourne", "Sydney", "Canberra", "Adelaide"]:
            res = couch.get(f'tweetdb/_partition/{city}/_design/sports/_view/{pk}')

            if res.json()['rows']:
                res = Counter(res.json()['rows'][0]["value"])
            else:
                res = Counter()
            count[city] = res
        total = Counter() # all sports
        for k in count.keys():
            total += count[k]
        count['total'] = total
        return Response(count)

class AurinViewSet(viewsets.ViewSet):
    # GET /aurin/
    def list(self, request):
        res = couch.get(f'aurin/_design/cities/_view/aurinInfo')
        return Response(res.json())

# Jobs statuses in Couchdb. Background tasks will periodically check the statuses to  
# start the jobs. 
class JobsViewSet(viewsets.ViewSet):

    # GET analyser/jobs/
    def list(self, request):
        actions = {
            'all': 'Stats of users.',
            'search': 'Get the sporst enthusiasts rank',
            'update': 'Get the sporst enthusiasts rank',
            'stream': 'Get the sporst enthusiasts rank',
            'user_rank': 'Get the sporst enthusiasts rank'
        }
        return Response(actions)

    # GET analyser/jobs/nodename
    @action(detail=False, methods=['get'], name="Get the current instance node name")
    def nodename(self, request):
        return Response(settings.DJANGO_NODENAME)

    # GET /analyser/jobs/all/
    @action(detail=False, methods=['get'], name="Get statuses of all jobs")
    def all(self, request):
        return Response(couch.get(f'jobs/_all_docs').json())

    # GET /analyser/jobs/search/
    # GET /analyser/jobs/update/
    # GET /analyser/jobs/stream/
    def retrieve(self, request, pk=None):
        if pk is None: 
            return Response({'error': 'job name is missing'})
        return Response(couch.get(f'jobs/{pk}').json())

    # PUT /analyser/jobs/search/ -d {"new_users": 1000}
    # PUT /analyser/jobs/update/
    # PUT /analyser/jobs/stream/
    def update(self, request, pk=None):
        try: 
            # get new users and timelines
            if pk == 'search': 
                return self.start_search(request)
            
            # update existing user timelines
            elif pk == 'update':
                return self.start_update()
            
            # start streaming
            elif pk == 'stream':
                return self.start_stream()

            else: 
                return Response({'error': f'Invalid job name {pk}'}) 
        except Exception as e: 
            return Response(str(e)) 

    def start_search(self, request): 
        new_users = request.data.get('new_users') if request.data is not None else None
        if isinstance(new_users, int): 
            new_users = int(new_users)
        else: 
            return Response({'error': 'Parameter new_users is not provided'}, 403)

        res = couch.get('jobs/search')
        if res.status_code == 200 and res.json().get('status') != 'idle':
            return Response(res.json(), 403)
        else: 
            doc = res.json()
            doc['status'] = 'ready'
            doc['new_users'] = new_users
            doc['result'] = 'Job Submitted.'
            response = couch.upsertdoc('jobs/search', doc)
            return Response(response.json(), response.status_code)

    def start_stream(self):
        res = couch.get('jobs/stream')
        if res.status_code == 200 and res.json().get('status') != 'idle':
            return Response(res.json(), 403)
        else: 
            doc = res.json()
            doc['status'] = 'ready'
            doc['result'] = 'Job Submitted.'
            response = couch.upsertdoc('jobs/stream', doc)
            return Response(response.json(), response.status_code)
    
    def start_update(self):
        res = couch.get('jobs/update')
        if res.status_code == 200 and res.json().get('status') != 'idle':
            return Response(res.json(), 403)
        else: 
            doc = res.json()
            doc['status'] = 'ready'
            doc['result'] = 'Job Submitted.'
            response = couch.upsertdoc('jobs/update', doc)
            return Response(response.json(), response.status_code)

class InitialiserViewSet(viewsets.ViewSet):
    # GET analyser/initialiser/
    def list(self, request):
        actions = {
            'couchdb': 'Initialise couchdb'
        }
        return Response(actions)

    # PUT analyser/initialiser/couchdb
    @action(detail=False, methods=['put'], name="Initialisation CouchDB Views")
    def couchdb(self, request):
        res = couch.get('jobs/couchdb')
        if res.status_code == 200 and res.json().get('status') != 'ready':
            return Response(res.json(), 403)
        else: 
            result = couch.migrate()
            res = couch.get('jobs/couchdb')
            doc = res.json()
            doc['status'] = 'idle'
            doc['result'] = result
            print(doc)
            response = couch.upsertdoc('jobs/couchdb', doc)
            return Response(response.json(), response.status_code)


