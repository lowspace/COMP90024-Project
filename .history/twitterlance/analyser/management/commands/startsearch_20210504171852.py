import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json, requests, time, docker

import couchdb.couch as couch
import twitter_search.search_user as search_user
import twitter_search.search_tweet as search_tweet
import twitter_stream.stream as stream
import twitter_search.config as config
import tweepy

class Command(BaseCommand):
    help = 'Initialise the databses required by this app'

    def handle(self, *args, **options): 
        # each city may use different tokens to complete the search task
        # need to exhaust all the cities

        def user_job():
            cities = config.Geocode.keys()
            tokens = config.token
            ID = None

            for city in cities:
                for token in tokens.keys():
                    # set api
                    consumer_key = tokens[token]['consumer_key']
                    consumer_secret = tokens[token]['consumer_secret']
                    access_token_key =  tokens[token]['access_token_key']
                    access_token_secret =  tokens[token]['access_token_secret']
                    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                    auth.set_access_token(access_token_key, access_token_secret)
                    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
                    # find the users
                    job, ID = search_user.user_search(' ', city, api, ID)
                    if job == True:
                        ID = None # initilize the ID
                        print('{c} is done.'.format(c = city))
                        break # next city
                    else:
                        print('{t} has been used, max_id is {i}'.format(t = token, i = ID))
                        continue # use next token
            print('\n\n\nUser search has completed.')
        
        def timeline_job():
            cities = config.Geocode.keys()
            tokens = config.token
            ID = None

            t0 = time.time()
            for city in cities:
                # read id from csv
                # file_name = city + '.csv'
                # city_path = os.path.join(cwd, file_name) # get the city foloder path
                # with open(city_path, 'r') as f:
                #     ###
                #     # how to read this csv? the csv save without lose information, but open will
                #     ###
                # get users in that city
                users = []
                ###
                # !!!???: this query always returns a warning: warning":"no matching index found, create an index to optimize
                #           query time". REF: https://docs.couchdb.org/en/stable/api/database/find.html#creating-selector-expressions
                ###
                query = dict(selector = {"city": city}, fields = ["_id", "city"], limit = search.rate_limit)
                response = couch.post(path = 'userdb/_find', body = query) # get users list of dict
                json_data = response.json()['docs'] # load response as json
                # print(json_data)
                for i in json_data: # get the user list
                    users.append(i['_id'])
                t1 = time.time()
                for i in range(len(users)): # user = uid
                    for token in tokens.keys():
                        # set api
                        consumer_key = tokens[token]['consumer_key']
                        consumer_secret = tokens[token]['consumer_secret']
                        access_token_key =  tokens[token]['access_token_key']
                        access_token_secret =  tokens[token]['access_token_secret']
                        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
                        auth.set_access_token(access_token_key, access_token_secret)
                        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
                        # crwal the timeline
                        job, ID = search_tweet.tweet_search(users[i], city, api, ID)
                        if job == True:
                            ID = None # initilize the ID
                            print('{u} in {c} is done.'.format(u = users[i], c = city))
                            break # next user
                        else:
                            print('move to next token and continue to search {u} in {c}.'.format(u = users[i], c = city))
                            continue # use next token 
                    t2 = time.time()
                    print('Have retrieved {c:,} tweets.'.format(c = total_num_retrieve_tweets))
                    print('success to save {c}/{t} users into CouchDB'.format(c = i+1, t = len(users)))
                    print('Have cost {t:.3f} seconds in {c}; average cost time {s:.3f} seconds for each user'.format(c = city, t = t2-t1, s = (t2-t1)/(i+1)))
                    print('Total cost time is {t:.3f}.'.format(t = t0 - t2))
                    print('Estimated time to complete {t:.3f} mins.'.format(t = (len(users)-i-1)*(t2-t1)/(i+1)/60))
                    print('\n')
            print('\n\n\Timeline search has completed.')

        user_job()
        timeline_job()
        print('Congratulation!! The search task is completed.')


