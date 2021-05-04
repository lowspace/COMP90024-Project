import couchdb.couch as couch
couch.create('tweetdb', True)

couch.create('userdb', False)
