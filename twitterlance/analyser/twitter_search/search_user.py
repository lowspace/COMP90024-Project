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

def user_search(query: str, city: str, api, ID = None):
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
    users = dict() # dict
    count = 0
    # store = {} # dict
    geocode = config.Geocode[city] # get geocode
    if not ID: # ID = None
        first = toJson(api.search(q = query, geocode = geocode, count=1))
    else: # ID != None
        first = toJson(api.search(q = query, geocode = geocode, max_id = ID, count=1))
    # print('first', first)
    if len(first) == 0 and count != 0: # no tweet 
        return True, None
    elif len(first) == 0 and count == 0:
        print('query contains nothing.')
        return False, None
    maxid = str(first[0]['id']-1)
    while True:
        # convert search results into Json file
        try:
            twitter = toJson(api.search(q = query, geocode = geocode, count = 100, max_id = maxid))
        except:
            if count == 10:
                print('????')
                break
            else:
                # save uid locally
                print('try')
                df = pd.DataFrame.from_dict(users, orient='index') # dict to pd
                t = str(datetime.datetime.now()) # time 
                name = city + ' ' + t + '.csv' # to avoid duplication
                path = './' + name 
                df.to_csv(path_or_buf = path, header=True, index=True) # save pd to csv in current dir
                return False, maxid # to be continued
        if len(twitter) != 0 and count != 10: # search query return tweets
            maxid = str(twitter[-1]['id']-1)
            for i in twitter:
                if i['user']['id_str'] not in users.keys(): # have not added under the query
                    count += 1 
                    user = dict()
                    # store[count]['_id'] = i['users']['id_str'] # does the format is right?
                    # store[count]['city'] = city
                    user['_id'] = i['user']['id_str']
                    user['city'] = city
                    print('user is', user, count)
                    users[user['_id']] = user # does the format is right?
                    # if len(store.keys()) == 100: # feed 100 uid to CouchDB
                    #     print(store) # feed this part to CouchDB
                    #     store = {} # empty the store
                    if count == 10: # each city get 10 unique uid
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
    print('save??')
    print(users)
    df = pd.DataFrame.from_dict(users, orient='index') # dict to pd
    t = str(datetime.datetime.now()) # time 
    name = city + ' ' + t + '.csv' # to avoid duplication
    path = './' + name 
    df.to_csv(path_or_buf = path, header=True, index=True) # save pd to csv in current dir
    return True, maxid

if __name__ == '__main__':
    # each city may use different tokens to complete the search task
    # need to exhaust all the cities

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
            job, ID = user_search(' ', city, api, ID)
            if job == True:
                ID = None # initilize the ID
                print('{c} is done.'.format(c = city))
                break # next city
            else:
                print('{t} has been used, max_id is {i}'.format(t = token, i = ID))
                continue # use next token
