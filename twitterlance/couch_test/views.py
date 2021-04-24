from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action
import json

# https://www.django-rest-framework.org/api-guide/viewsets/
class CommentViewSet(viewsets.ViewSet):
    def list(self, request):
        data = {"params": request.query_params}
        return Response(json.dumps(data))

    def create(self, request):
        data = {"params": request.query_params}
        return Response(json.dumps(data))

    def retrieve(self, request, pk=None):
        data = {"params": request.query_params}
        return Response(json.dumps(data))

    def update(self, request, pk=None):
        data = {"pk": pk}
        return Response(json.dumps(data))

    def partial_update(self, request, pk=None):
        data = {"params": request.query_params}
        return Response(json.dumps(data))

    def destroy(self, request, pk=None):
        data = {"params": request.query_params}
        return Response(json.dumps(data))