import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json, requests, time, docker
import couchdb.couch as couch
import twitter_stream.stream as stream

class Command(BaseCommand):
    help = 'Initialise the databses required by this app'

    def handle(self, *args, **options):

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

        # connect local CouchDB dataset
        server = "http://admin:Aa123456789@localhost:5984"
        couch.base_url = server

        # Loop to save the tweets that meet the requirements in CouchDB

        while True:
            try:
                myStream = stream.tweepy.Stream(auth=stream.api.auth, listener=stream.MyStreamListener())
                myStream.filter(locations=stream.overall)

            except Exception as e:
                print(e)


