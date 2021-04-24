from django.urls import include, path
from rest_framework import routers
from . import views

# https://www.django-rest-framework.org/api-guide/routers/
router = routers.DefaultRouter()
router.register(r'comment', views.CommentViewSet, basename="Comment")

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]