from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
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
            'stats': 'Get the stats of tweets',
            'sports': 'sport tweets total'
        }
        return Response(actions)

    # GET analyser/tweets/:id
    def retrieve(self, request, pk=None):
        return Response(couch.get('twitter', pk).json())

    # GET analyser/tweets/stats/
    @action(detail=False, methods=['get'], name="Get the stats of tweets")
    def stats(self, request):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        count = {}
        for city in couch.geocode().keys():
            res = couch.get(f'tweets/_partition/{city}')
            count[city] = res.json()["doc_count"]
        count["total_tweets"] = sum(count.values())
        return Response({"tweet_stats": count})
    
    # GET analyser/tweets/sports/ sport related tweets
    @action(detail=False, methods=['get'], name="sport tweets total")
    def sports(self, request):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        # count = 0
        res1 = {}
        for city in couch.geocode().keys():
            res = couch.get(f'tweets/_partition/{city}/_design/sports/_view/total')
            if len(res.json().get('rows', [])) > 0:
                res1[city]=res.json().get('rows', [])[0]["value"]
        return Response(res1)
    
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
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})
            
        count = {}
        for city in couch.geocode().keys():
            res = couch.get(f'users/_design/cities/_view/{city}')
            if res.status_code == 200 and res.json().get('rows', []):
                count[city] = res.json().get('rows', [])[0]["value"]   
        count["total_users"] = sum(count.values())
        return Response({"user_stats": count})

    # GET analyser/users/rank
    @action(detail=False, methods=['get'], name="Get the rank of the enthusiasts")
    def rank(self, request):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        res = couch.get('conclusions/user_rank')
        rank = []
        cities = res.json().get('result', {})
        for city, scores in cities.items():
            for score in scores:
                user = {
                    'name': score[0],
                    'score': score[1],
                    'city': city
                } 
                rank.append(user)

        rank.sort(key=lambda x : x['score'], reverse=True)
 
        print(f'[rank] {rank}')               
        if len(rank) > 0:
            rank[0]['name'] = '???? ' + rank[0]['name']
            rank[1]['name'] = '???? ' + rank[1]['name']
            rank[2]['name'] = '???? ' + rank[2]['name']
        return Response(rank)
class SportViewSet(viewsets.ViewSet):

    # GET analyser/sports/
    def list(self, request):
        actions = {
            'stats_all': 'All sport counts in all cities cross all time.',
            '<year>-<year>': 'All sport counts in all cities between the years',
            'rank_top3': 'Top 3 sports in all cities cross all time.'
        }
        return Response(actions)

    # GET analyser/sports/stats_all
    @action(detail=False, methods=['get'], name="Get the static_stats of sports")
    def stats_all(self, request):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        count = {}
        sum_all = {}
        print(f'[stats_all] cities={couch.geocode().keys()}')
        for city in couch.geocode().keys():
            res = couch.get(f'tweets/_partition/{city}/_design/sports/_view/total')
            if res.json().get('rows', []):
                res = Counter(res.json().get('rows', [])[0]["value"])
                sum_all[city] = sum(res.values())
                count[city] = res
        total = Counter() # all sports
        for k in count.keys():
            total += count[k]
        count['total'] = total
        sum_all['total'] = sum(sum_all.values())
        count['sum'] = sum_all
        return Response(self.deduplicate(count))
    
    def get_merger(self):
        return {
            'afl': 'footy', 
            'rugby': 'footy', 
            'jump': 'jumps', 
            'ran': 'run', 
            'jog': 'run', 
            'bike': 'cycling',
            'bicycle': 'cycling',
            'f1': 'racing',
        }

    def deduplicate(self, cities):
        merge_to = self.get_merger()
        for city in cities.keys(): 
            if city == 'sum':
                continue
            for to_remove, to_add in merge_to.items():
                cities[city][to_add] = cities[city].get(to_add, 0) + cities[city].pop(to_remove, 0)
        return cities


    # GET analyser/sports/rank_top3
    @action(detail=False, methods=['get'], name="Get the top 3 sports in each city across all time")
    def rank_top3(self, request):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        count = {}
        for city in couch.geocode().keys():
            res = couch.get(f'tweets/_partition/{city}/_design/sports/_view/total')
            if res.json().get('rows', []):
                res = Counter(res.json().get('rows', [])[0]["value"])
                merge_to = self.get_merger()
                for to_remove, to_add in merge_to.items():
                    res[to_add] = res.get(to_add, 0) + res.pop(to_remove, 0)
                top3 = {}
                for i in res.most_common(3):
                    top3[i[0]] = i[1]
                count[city] = top3
        return Response(count)

    # GET analyser/sports/year-year Get the year tweets of sports
    def retrieve(self, request, pk=None):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        count = {}

        if pk is None or len(pk.split('-')) != 2:
            return Response({"error": 'pk is not in a form of <year number>-<year number>'})
        
        start = int(pk.split('-')[0])
        end = int(pk.split('-')[1])

        count = {}
        for city in couch.geocode().keys():
            time_line = {}
            for time_stamp in range(start, end+1):
                res = couch.get(f'tweets/_partition/{city}/_design/sports/_view/{time_stamp}')
                if len(res.json().get('rows', [])) > 0:
                    res = Counter(res.json()['rows'][0]["value"])
                    time_line[time_stamp] = sum(res.values())
            count[city] = time_line
        return Response(count)

class AurinViewSet(viewsets.ViewSet):
    # GET /analyser/aurin/
    def list(self, request):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        data = {}
        res = couch.get(f'aurin/_all_docs?include_docs=true').json()
        for row in res['rows']:
            data[row['id']] = row['doc']['features']

        return Response(data)

# Jobs statuses in Couchdb. Background tasks will periodically check the statuses to  
# start the jobs. 
class JobsViewSet(viewsets.ViewSet):

    # GET analyser/jobs/
    def list(self, request):
        actions = {
            'all': 'All job statsuses',
            'search': 'Start twitter harvester',
            'update': 'Start updating users timeline',
            'stream': 'Start streaming tweets',
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
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        jobs = []
        for row in couch.get(f'jobs/_all_docs?include_docs=true').json().get('rows', []):
            jobs.append(row['doc'])
        return Response(jobs)

    # GET /analyser/jobs/search/
    # GET /analyser/jobs/update/
    # GET /analyser/jobs/stream/
    def retrieve(self, request, pk=None):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})
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

    # DELETE /analyser/jobs/search/ 
    # DELETE /analyser/jobs/update/
    # DELETE /analyser/jobs/stream/
    def delete(self, request, pk=None):
        try: 
            # get new users and timelines
            if pk == 'search': 
                return self.stop_search()
            
            # update existing user timelines
            elif pk == 'update':
                return self.stop_update()
            
            # start streaming
            elif pk == 'stream':
                return self.stop_stream()

            else: 
                return Response({'error': f'Invalid job name {pk}'}) 
        except Exception as e: 
            return Response(str(e)) 

    def start_search(self, request): 
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        new_users = request.data.get('new_users', '1') if request.data is not None else None
        try:
            new_users = int(new_users)
        except: 
            return Response({'error': 'Parameter new_users is invalid'}, 403)
        res = couch.get('jobs/search')
        if res.status_code == 200 and res.json().get('status') != 'idle':
            return Response(res.json(), 403)
        else: 
            doc = res.json()
            doc['status'] = 'ready'
            doc['new_users'] = new_users
            doc['result'] = 'Job Submitted.'
            response = couch.updatedoc('jobs/search', doc)
            return Response(response.json(), response.status_code)

    def start_stream(self):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        res = couch.get('jobs/stream')
        if res.status_code == 200 and res.json().get('status') != 'idle':
            return Response(res.json(), 403)
        else: 
            doc = res.json()
            doc['status'] = 'ready'
            doc['result'] = 'Job Submitted.'
            response = couch.updatedoc('jobs/stream', doc)
            return Response(response.json(), response.status_code)
    
    def start_update(self):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        res = couch.get('jobs/update')
        if res.status_code == 200 and res.json().get('status') != 'idle':
            return Response(res.json(), 403)
        else: 
            doc = res.json()
            doc['status'] = 'ready'
            doc['result'] = 'Job Submitted.'
            response = couch.updatedoc('jobs/update', doc)
            return Response(response.json(), response.status_code)
    
    def stop_search(self): 
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        res = couch.get('jobs/search')
        doc = res.json()
        doc['status'] = 'idle'
        doc['nodes'] = []
        doc['result'] = 'Job stopped.'
        response = couch.updatedoc('jobs/search', doc)
        return Response(response.json(), response.status_code)

    def stop_stream(self):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        res = couch.get('jobs/stream')
        doc = res.json()
        doc['status'] = 'idle'
        doc['nodes'] = []
        doc['result'] = 'Job stopped.'
        response = couch.updatedoc('jobs/stream', doc)
        return Response(response.json(), response.status_code)
    
    def stop_update(self):
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

        res = couch.get('jobs/update')
        doc = res.json()
        doc['status'] = 'idle'
        doc['nodes'] = []
        doc['result'] = 'Job stopped.'
        response = couch.updatedoc('jobs/update', doc)
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
        res = couch.head('')
        if res.status_code == 500:
            return Response({'error': res.json()})

       
        result = couch.migrate()
        return Response({'resault': result})


