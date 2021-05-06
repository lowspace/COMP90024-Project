from django.urls import include, path
from rest_framework import routers
from . import views

# https://www.django-rest-framework.org/api-guide/routers/
router = routers.DefaultRouter()
router.register(r'tweets', views.TweetViewSet, basename="Tweet")
router.register(r'users', views.UserViewSet, basename="User")
router.register(r'sports', views.SportViewSet, basename="Sport")
router.register(r'aurin', views.AurinViewSet, basename="Aurin")
<<<<<<< HEAD
router.register(r'yearly', views.YearlySportsTweetsViewSet, basename="Yearly")


=======
>>>>>>> 55acf1291754e7b15f507d447b1e070ab92563ef

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]