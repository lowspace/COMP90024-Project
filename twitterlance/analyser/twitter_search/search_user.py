import json
import tweepy
from tweepy import OAuthHandler
import pandas as pd
import datetime

import config

def toJson(tweets):
    twitter = []
    for i in tweets:
        twitter.append(i._json)
    return twitter

def user_search(query: str, city: str, ID = None, api):
    """
    This function tends to obtain the uid of the tweets with the query
    Input:
        query = what we wann search
        city = 'Melbourne', 'Sydney', 'Canberra', 'Adelaide'
        ID = str, of the last tid
    Output:
        1. save the uid into CouchDB 
        2. save the uid locally (for now)
    """
    assert city in ('Melbourne', 'Sydney', 'Canberra', 'Adelaide'), "The city only accepts 'Melbourne', 'Sydney', 'Canberra', and 'Adelaide'."
    user = {} # dict
    # store = {} # dict
    geocode = Geocode[city] # get geocode
    if not ID: # ID = None
        first = toJson(api.search(q = query, geocode = geocode, count=1))
    else: # ID != None
        first = toJson(api.search(q = query, geocode = geocode, max_id = ID, count=1))
    if len(first) == 0: # no tweet 
        return None
    maxid = str(first[0]['id']-1)
    count = 0
    while True:
        # convert search results into Json file
        try:
            twitter = toJson(api.search(q = query, geocode = geocode, count = 100, max_id = maxid))
        except:
            if count = 10000:
                break
            else:
                # save uid locally
                df = pd.DataFrame.from_dict(user, orient='index') # dict to pd
                t = str(datetime.datetime.now()) # time 
                name = city + ' ' + t + '.csv' # to avoid duplication
                path = './' + name 
                df.to_csv(path_or_buf = path, header=True, index=True) # save pd to csv in current dir
                return False, maxid # to be continued
        if len(twitter) != 0 and count = 10000: # search query return tweets
            maxid = str(twitter[-1]['id']-1)
            for i in twitter:
                if i['user']['id_str'] not in user.keys(): # have not added under the query
                    count += 1 
                    # store[count]['_id'] = i['user']['id_str'] # does the format is right?
                    # store[count]['city'] = city
                    user[count]['_id'] = i['user']['id_str'] # does the format is right?
                    user[count]['city'] = city
                    # if len(store.keys()) == 100: # feed 100 uid to CouchDB
                    #     print(store) # feed this part to CouchDB
                    #     store = {} # empty the store
                    if count == 10000: # each city get 10000 unique uid
                        # if len(store.keys()) != 0:
                        #     print(store) # feed this part to CouchDB
                        #     store = {} # empty the store
                        break
                       
        else: # search query return None
            # if store: # len(store) < 100, but query return None
            #     print(store) feed this part to CouchDB
            #     store = {}
            # else:
            #     break
            break
    # save uid locally
    df = pd.DataFrame.from_dict(user, orient='index') # dict to pd
    t = str(datetime.datetime.now()) # time 
    name = city + ' ' + t + '.csv' # to avoid duplication
    path = './' + name 
    df.to_csv(path_or_buf = path, header=True, index=True) # save pd to csv in current dir
    return True, maxid

    for city in Geocode.keys():
        auth = tweepy.OAuthHandler(Geocode[city][1], Geocode[city][2])
        auth.set_access_token(Geocode[city][3], Geocode[city][4])
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        result = tweet_search(" ",Geocode[city][0], api)
        if result !=None:
            users = result[1]
            for user in users:
                user_search(user, api)

if __name__ == '__main__':
    print(config.token.keys())