from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
from .couch import Couch
import json

# https://www.django-rest-framework.org/api-guide/viewsets/
class CommentViewSet(viewsets.ViewSet):

    def list(self, request):
        couch = Couch()
        return Response(couch.get('comment', '_all_docs').json())

    def create(self, request):
        couch = Couch()
        return Response(couch.put('comment', request.query_params).json())

    def retrieve(self, request, pk=None):
        couch = Couch()
        return Response(couch.get('comment',pk).json())