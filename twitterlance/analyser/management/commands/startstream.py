import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json, requests, time, docker
import couchdb.couch as couch
import twitter_stream.stream as stream

class Command(BaseCommand):
    help = 'Initialise the databses required by this app'

    def handle(self, *args, **options):

        try:
            stream.api.verify_credentials()
            print("Authentication OK")
        except:
            print("Error during authentication")

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


