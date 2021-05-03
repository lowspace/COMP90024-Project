import couch

couch.create('try-no-parition') # default = False

couch.create('try-parition', True)

couch.create('tweetdb', True)

couch.create('userdb', False)