from django.urls import include, path
from rest_framework import routers
from . import views

# https://www.django-rest-framework.org/api-guide/routers/
router = routers.DefaultRouter()
router.register(r'tweets', views.TweetViewSet, basename="Tweet")
router.register(r'users', views.UserViewSet, basename="User")

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

t =     {
  "_id": "_design/test",
  "views": {
    "new-view": {
      "map": "function (doc) {\n  sport = ['wrestling', 'weights', 'skiing', 'water polo', 'volleyball', 'tennis', 'team handball', 'table tennis', 'swimming', 'surfing', 'sprinting', 'skating', 'soccer', 'skateboarding', 'shooting', 'rugby', 'rowing', 'rodeo', 'racquetball', 'squash', 'pole vault', 'running', 'martial arts', 'jumps', 'lacrosse', 'ice hockey', 'jump', 'gymnastics', 'golf', 'football', 'fishing', 'field hockey', 'fencing', 'equestrian', 'diving', 'running', 'cycling', 'curling', 'cheerleading', 'canoe', 'kayak', 'bull', 'bareback', 'bronc riding', 'boxing', 'bowling', 'bobsledding', 'luge', 'billiards', 'basketball', 'baseball', 'softball', 'badminton', 'racing', 'archery']\n  for (var i=0; i<55;i++){\n  if (doc.val.text.toLowerCase().includes(sport[i]))\n   {emit(doc._id, 1); break}}\n}",
      "reduce": "_count"
    }
  },
  "language": "javascript",
  "options": {
    "partitioned": true
  }
}
print("\n\n\n?>??\n\n\n")
couch.put('tweetdb/_design/test', body=t)