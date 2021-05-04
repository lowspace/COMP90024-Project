import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json, requests, time, docker
import couchdb.couch as couch
import twitter_stream.stream as stream

class Command(BaseCommand):
    help = 'Initialise the databses required by this app'

    def handle(self, *args, **options):

        Syd = [149.928, -34.345, 151.645, -32.976]
        Can = [148.747, -35.926, 149.420, -35.106]
        Mel = [144.312, -38.506, 145.894, -37.160]
        Ade = [138.422, -35.355, 139.052, -34.493]
        overall = [144.312, -38.506, 151.645, -32.976]

        # consumer_key = 'wku1JIpNi4pXukXp510Hzylj2'
        # consumer_secret = 'JZPuJKqMZu929iu8XxgTQAOw0up1LLJj6hKUjFDPE4aSNsp1KP'
        # access_token = '1382968455989583874-9DiykvjpUlnYtq2fJAgScghh9TMBs2'
        # access_token_secret = 'k6C6Yx8LNkNp5FtyG55d6WZ0lwePYbAYAmnkg5xOd65G6'
        #
        # auth = stream.tweepy.OAuthHandler(consumer_key, consumer_secret)
        # auth.set_access_token(access_token, access_token_secret)
        # api = stream.tweepy.API(auth)
        #
        # try:
        #     api.verify_credentials()
        #     print("Authentication OK")
        # except:
        #     print("Error during authentication")

        # Loop to save the tweets that meet the requirements in CouchDB
        while True:
            try:
                myStream = stream.tweepy.Stream(auth=stream.api.auth, listener=stream.MyStreamListener())
                myStream.filter(locations=overall)

            except Exception as e:
                print(e)


