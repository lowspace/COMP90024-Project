from django.urls import include, path
from rest_framework import routers
from . import views

# https://www.django-rest-framework.org/api-guide/routers/
router = routers.DefaultRouter()
router.register(r'tweets', views.TweetViewSet, basename="Tweet")
router.register(r'users', views.UserViewSet, basename="User")
router.register(r'sports', views.SportViewSet, basename="Sport")
<<<<<<< HEAD
# router.register(r'aurin', views.AurinViewSet, basename="Aurin") 
=======
router.register(r'aurin', views.AurinViewSet, basename="Aurin")
router.register(r'yearly', views.YearlySportsTweetsViewSet, basename="Yearly")

>>>>>>> 35a62bc79a249d727829a8da480b407465d4b451

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
