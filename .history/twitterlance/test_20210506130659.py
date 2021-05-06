from couchdb import couch

t = {
  "views": {
    "test": {
      "map": "function (doc) { sport = ['wrestling', 'weights', 'skiing', 'water polo', 'volleyball', 'tennis', 'team handball', 'table tennis', 'swimming', 'surfing', 'sprinting', 'skating', 'soccer', 'skateboarding', 'shooting', 'rugby', 'rowing', 'rodeo', 'racquetball', 'squash', 'pole vault', 'running', 'martial arts', 'jumps', 'lacrosse', 'ice hockey', 'jump', 'gymnastics', 'golf', 'football', 'fishing', 'field hockey', 'fencing', 'equestrian', 'diving', 'running', 'cycling', 'curling', 'cheerleading', 'canoe', 'kayak', 'bull', 'bareback', 'bronc riding', 'boxing', 'bowling', 'bobsledding', 'luge', 'billiards', 'basketball', 'baseball', 'softball', 'badminton', 'racing', 'archery'] for (var i=0; i<55;i++){ if (doc.val.text.toLowerCase().includes(sport[i])) {emit(doc._id, 1); break}} }",
    }
  }
}
couch.put('tweetdb/_partition/Melbourne/_design/test', json=t)