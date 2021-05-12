from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from analyser import views

urlpatterns = [
    path('analyser/', include('analyser.urls')),
    path('admin/', admin.site.urls),
    url(r'^home/', views.home, name="home"),
    url(r'^statistics/', views.statistics, name="statistics"),
    url(r'^map/', views.map, name="map"),
    url(r'^about/', views.about, name="about"),
    url(r'^mappage/', views.mappage, name="mappage"),
    url(r'^:9000/', views.manage, name="manage"),
    url(r'^Haproxy/', views.Haproxy, name="Haproxy"),
    url(r'^:8080/', views.Spark, name="Spark"),
]
