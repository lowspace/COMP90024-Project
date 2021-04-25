from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from .couch import Couch
import json

# https://www.django-rest-framework.org/api-guide/viewsets/
# https://docs.djangoproject.com/en/3.2/ref/request-response/#django.http.QueryDict.urlencode
class MapViewSet(viewsets.ViewSet):
    def __init__(self, **args):
        super().__init__(**args)
        self.database = 'twitter'
        self.couch = Couch()

    #GET analyser/tweets?options
    def list(self, request):
        url = f'{self.database}/_all_docs'
        if len(request.query_params) > 0: 
            url += f'?{request.query_params.urlencode()}'
        res = self.couch.get(url)
        return Response(res.json())

    #GET analyser/tweets/:id
    def retrieve(self, request, pk=None):
        res = self.couch.get(f'{self.database}/{pk}')
        return Response(self.couch.get('twitter',pk).json())

    #GET analyser/tweets/box_tweets?lat_min=-9.1457534&lat_max=-0.4000327&lon_min=134.505904&lon_max=141.0549412
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
        res = self.couch.get(f'{self.database}/_design/geo/_search/box?q={query}')
        return Response({'total_rows': int(res.json()['total_rows'])})
