from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url
from django.shortcuts import HttpResponse
from analyser import views


urlpatterns = [
    path('analyser/', include('analyser.urls')),
    path('admin/', admin.site.urls),
    url(r'^home/', views.home),
    url(r'^statistics/', views.statistics),
    url(r'^map/', views.map),
    url(r'^about/', views.about),

]