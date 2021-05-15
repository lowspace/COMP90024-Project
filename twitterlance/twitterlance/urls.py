from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home),
    path('home/', views.home),
    path('about/', views.about),
    path('statistics/', views.statistics),
    path('map/', views.map),
    path('mappage/', views.mappage),
    path('analyser/', include('analyser.urls')),
]
