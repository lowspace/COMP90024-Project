import json
import tweepy
from tweepy import OAuthHandler
import os
import couchdb.couch as couch
# import couch
import time
# import twitter_search.search_user as search_user
# import twitter_search.search_tweet as search_tweet
# import search_user
# import search_tweet
import datetime

global rate_limit
rate_limit = 10 # how many users we wanna add in this city

c_dict = dict(
    Melbourne = "mel",
    Adelaide = "adl",
    Sydney = "syd",
    Canberra = "cbr",
    Perth = "per", 
    Brisbane = "bne",
    )

def toJson(tweets):
    twitter = []
    for i in tweets:
        twitter.append(i._json)
    return twitter

def search(query: str, city: str, api, ID = None):
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
    ulist = [] # list of uid
    c_id = c_dict[city]
    res = couch.get(f'userdb/_design/cities/_view/{c_id}') # get the id list of this city
    res = res.json()['rows']
    for i in res:
        if i["id"] in ulist:
            continue
        else:
            ulist.append(i["id"])
    count = 0 
    # store = {} # dict
    geocode = couch.geocode()[city] # get geocode
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
                print('try')
                return False, maxid # to be continued
        if len(twitter) != 0 and count != rate_limit: # search query return tweets
            for i in twitter:
                if i['user']['id_str'] not in ulist:
                    ulist.append(i['user']['id_str'])
                    count += 1 
                    user = dict()
                    uid = i['user']['id_str']
                    user['_id'] = uid
                    user['city'] = city
                    try:
                        search_tweet.tweet_search(uid, city, api, None)
                    except:
                        print("search tweet error")
                        return False, maxid # to be continued
                    print('update is done for {id}'.format(id = uid))
                    # transform datetime into Twitter format
                    now_update_timestamp = datetime.datetime.now().astimezone(tz=datetime.timezone.utc).strftime('%a %b %d %H:%M:%S %z %Y')
                    user['update_timestamp'] = now_update_timestamp # assign the update timeline timestamp
                    couch.put(f'userdb/{uid}', user) # save the user 2 CouchDB 
                    print('user is', user, count)
                    t2 = time.time()
                    print('Progress {c}/{t}.'.format(c = count, t = rate_limit))
                    print('Have cost {t:.3f} seconds; average cost time {s:.3f} seconds'.format(t = t2 - t1, s = (t2-t1)/count))
                    print('Estimated time to complete {t:.3f} mins.'.format(t = (rate_limit-count)*(t2-t1)/count/60))  
                    if count == rate_limit: # each city get 10 unique uid
                        break
                maxid = str(twitter[-1]['id']-1)             
        else: # search query return None
            break
    return True, maxid

def run_search(i:int):
    global rate_limit
    rate_limit = i # set the rate_limit for this search
    cities = couch.geocode().keys()
    query = dict(selector = {"type": "search"}, fields = ["consumer_key", "consumer_secret", "access_token_key","access_token_secret"]) 
    res=couch.post(f'tokens/_find', body = query)
    tasks=res.json()['docs']
    tokens={}
    for i in range(0,len(tasks)):
        tokens[i]=tasks[i]
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
            job, ID = search(' ', city, api, ID)
            if job == True:
                ID = None # initilize the ID
                print('{c} is done.\n\n'.format(c = city))
                break # next city
            else:
                print('{t} has been used, max_id is {i}'.format(t = token, i = ID))
                continue # use next token

# if __name__ == '__main__':
#     # each city may use different tokens to complete the search task
#     # need to exhaust all the cities

#     cities = couch.geocode().keys()
#     tokens = config.token
#     ID = None

#     for city in cities:
#         for token in tokens.keys():
#             # set api
#             consumer_key = tokens[token]['consumer_key']
#             consumer_secret = tokens[token]['consumer_secret']
#             access_token_key =  tokens[token]['access_token_key']
#             access_token_secret =  tokens[token]['access_token_secret']
#             auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#             auth.set_access_token(access_token_key, access_token_secret)
#             api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
#             # find the users
#             job, ID = search(' ', city, api, ID)
#             if job == True:
#                 ID = None # initilize the ID
#                 print('{c} is done.\n\n'.format(c = city))
#                 break # next city
#             else:
#                 print('{t} has been used, max_id is {i}'.format(t = token, i = ID))
#                 continue # use next token