import json
import tweepy
from tweepy import OAuthHandler
import pandas as pd
import datetime
import config 
import couch as couch
import time

global rate_limit

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
    users = [] # list of {uid:, city:,}
    ulist = [] # list of uid
    count = 0 
    rate_limit = 500 # how many users we wanna count in this city
    # store = {} # dict
    geocode = config.Geocode[city] # get geocode
    if not ID: # ID = None
        first = toJson(api.search(q = query, geocode = geocode, count=66)) # consider loss tweets
    else: # ID != None
        first = toJson(api.search(q = query, geocode = geocode, max_id = ID, count=66))
    # print('first', first)
    if len(first) == 0 and count != 0: # no tweet 
        print('something wrong')
        return True, None
    elif len(first) == 0 and count == 0:
        print('query contains nothing.')
        user_search('covid', city, api, ID) # can it work well??
        return False, None
    maxid = str(first[0]['id']-1)
    t1 = time.time()
    while True:
        # convert search results into Json file
        try:
            twitter = toJson(api.search(q = query, geocode = geocode, count = 200, max_id = maxid))
        except:
            if count == rate_limit:
                print('unable to search new tweets, but meet the rate requirement.')
                break
            else:
                # save uid locally
                print('try')
                # df = pd.DataFrame.from_dict(users, orient='index') # dict to pd
                # t = str(datetime.datetime.now()) # time 
                # name = city + ' ' + t + '.csv' # to avoid duplication
                # path = './twitterlance/analyser/twitter_search/' + name 
                # df.to_csv(path_or_buf = path, header=True, index=True) # save pd to csv in current dir
                # name = city + ' ' + t + '.json' # to json
                # path = './twitterlance/analyser/twitter_search/' + name 
                # with open(path, 'w') as output: # save as json
                #     json.dump(users, output)
                couch.bulk_save('userdb', users)
                return False, maxid # to be continued
        if len(twitter) != 0 and count != rate_limit: # search query return tweets
            maxid = str(twitter[-1]['id']-1)
            for i in twitter:
                if i['user']['id_str'] not in ulist:
                # if i['user']['id_str'] not in users.keys(): # have not added under the query
                    ulist.append(i['user']['id_str'])
                    count += 1 
                    user = dict()
                    # store[count]['_id'] = i['users']['id_str'] # does the format is right?
                    # store[count]['city'] = city
                    user['_id'] = i['user']['id_str']
                    user['city'] = city
                    # user_json = json.dumps(user)
                    # couch.save('userdb', user) # save each tweet into CouchDB
                    print('user is', user, count)
                    # users[user['_id']] = user # does the format is right?
                    users.append(user)
                    # if len(store.keys()) == 100: # feed 100 uid to CouchDB
                    #     print(store) # feed this part to CouchDB
                    #     store = {} # empty the store
                    if count == rate_limit: # each city get 10 unique uid
                        # if len(store.keys()) != 0:
                        #     print(store) # feed this part to CouchDB
                        #     store = {} # empty the store
                        break
            t2 = time.time()
            print('Progress {c}/{t}.'.format(c = count, t = rate_limit))
            print('Have cost {t:.3f} seconds; average cost time {s:.3f} seconds'.format(t = t2 - t1, s = (t2-t1)/count))
            print('Estimated time to complete {t:.3f} mins.'.format(t = (rate_limit-count)*(t2-t1)/count/60))
            print('\n')                    
        else: # search query return None
            # if store: # len(store) < 100, but query return None
            #     print(store) feed this part to CouchDB
            #     store = {}
            # else:
            #     break
            break
    # save uid locally
    # print(users)
    # df = pd.DataFrame.from_dict(users, orient='index') # dict to pd
    # t = str(datetime.datetime.now()) # time 
    # name = city + ' ' + t + '.csv' # to avoid duplication
    # path = './twitterlance/analyser/twitter_search/' + name 
    # df.to_csv(path_or_buf = path, header=True, index=True) # save pd to csv in current dir
    # name = city + ' ' + t + '.json' # to json
    # path = './twitterlance/analyser/twitter_search/' + name 
    # with open(path, 'w') as output: # save as json
    #     json.dump(users, output)
    couch.bulk_save('userdb', users) # save 2 CouchDB at once
    print('success to save {c}/{t} users into CouchDB'.format(c = count, t = rate_limit))
    t2 = time.time()
    print('{c} has cost {t:.3f} seconds; average {s:.3f} seconds for each user'.format(c = city, t = t2 - t1, s = (t2-t1)/count))
    print('\n')  
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