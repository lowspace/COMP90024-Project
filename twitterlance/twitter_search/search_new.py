import json
import tweepy
from tweepy import OAuthHandler
import os
import couchdb.couch as couch
import time
import datetime


global total_num_retrieve_tweets
total_num_retrieve_tweets = 0



def toJson(tweets):
    tweets = []
    for i in tweets:
        tweets.append(i._json)
    return tweets

def search_user(query: str, city: str, api, rate_limit = 10, latest_id = None):
    """
    This function tends to obtain the uid of the tweets with the query
    Input:
        query = what we wann search
        city = couch.geocode().keys()
        latest_id = str, of the last tid
    Output:
        1. save the uid into CouchDB 
        2. save the uid locally (for now)
    """
    ulist = [] # list of uid
    res = couch.get(f'userdb/_design/cities/_view/{city}') # get the id list of this city
    res = res.json()['rows']
    for row in res:
        if row["id"] in ulist:
            continue
        else:
            ulist.append(row["id"])
    count = 0 
    city_dict = couch.geocode() # get city {city_name: geocode, }
    geocode = city_dict[city] # get geocode
    if not latest_id: # latest_id = None
        first = toJson(api.search(q = query, geocode = geocode, count=66)) # consider loss tweets
    else: # latest_id != None
        first = toJson(api.search(q = query, geocode = geocode, max_id = latest_id, count=66))
    # print('first', first)
    if len(first) == 0 and count != 0: # no tweet 
        print('something wrong')
        return True, None
    elif len(first) == 0 and count == 0:
        print('query contains nothing.')
        user_search('covid', city, api, latest_id) # can it work well??
        return False, None
    maxid = str(first[0]['id']-1)
    t1 = time.time()
    while True:
        if count >= rate_limit: # 
            break
        try:
            # convert search results into Json file
            tweets = toJson(api.search(q = query, geocode = geocode, count = 200, max_id = maxid))
        except:
                print(f'Have retrieved {count}/{rate_limit}, but unable to continue in this token.')
                return False, maxid # to be continued
        if len(tweets) != 0 and count < rate_limit: # search query return tweets
            for tweet in tweets:
                if tweet['user']['id_str'] not in ulist:
                    ulist.append(tweet['user']['id_str'])
                    count += 1 
                    user = dict()
                    uid = tweet['user']['id_str']
                    user['_id'] = uid
                    user['city'] = city
                    print('update is done for {id}'.format(id = uid))
                    # transform datetime into Twitter format
                    user['update_timestamp>π'] = couch.now() # assign the update timeline timestamp
                    couch.put(f'userdb/{uid}', user) # save the user 2 CouchDB 
                    print('user is', user, count)
                    t2 = time.time()
                    print('Progress {c}/{t}.'.format(c = count, t = rate_limit))
                    print('Have cost {t:.3f} seconds; average cost time {s:.3f} seconds'.format(t = t2 - t1, s = (t2-t1)/count))
                    print('Estimated time to complete {t:.3f} mins.'.format(t = (rate_limit-count)*(t2-t1)/count/60))  
                    if count >= rate_limit: # each city get rate_limit unique uid
                        break
            maxid = str(tweets[-1]['id']-1)             
        else: # search query return None
            print(f'Have retrieved {count}/{rate_limit}, but unable to query more.')
            break
    return True, maxid

def search_tweet(user: dict, api, timeline_limit= 3000):
    """
    The function crawls timeline of the uid
    Input:
        user = dict of user
        timeline_limit = 3000
        api = api
    """

    def tweet_2_dict(t, city: str):
        """
        convert one tweet to a dict = {'_id':, 'uid', 'city', 'val'}
        Input = tweet_dict
        Output = structured tweet_dict
        """
        d = {}
        d['_id'] = city + ':' + t['id_str'] # parition _id
        d['uid'] = t['user']['id_str']
        d['city'] = city
        d['val'] = t
        return d

    uid = user['_id']
    city = user['city']
    tweets = [] # return object
    try:
        new_tweets = toJson(api.user_timeline(user_id = uid, count = 200))
    except:
        print("First trial failed, we can try another token.")
        return False

    while True: # get the tweets
        if len(new_tweets) == 0: # no tweet returns
            break
        if len(new_tweets) == 200:
            maxid = str(new_tweets[-1]['id'] - 1)
            for tweet in new_tweets:
                tweet = tweet_2_dict(tweet, city) # convert tweet to be structured
                tweets.append(tweet)
            if len(tweets) >= timeline_limit: # some users have a large timeline
                print("for each user, retrieve {l} tweets maximally".format(l = timeline_limit))
                break
            try:
                new_tweets = api.user_timeline(user_id = uid, count = 200, max_id = maxid)
                new_tweets = toJson(new_tweets)
            except:
                print("Error occurs in the progress at tid, {t} of uid,{u}".format(t = maxid, u = uid))
                return False # move to next token
        else:
            for tweet in new_tweets:
                tweet = tweet_2_dict(tweet, city) # convert tweet to be structured
                tweets.append(tweet)
            break

    retries = 0
    while retries < 5:
        try:
            tweetres = couch.bulk_save('tweetdb', tweets)
            if tweetres.status_code == 201: # ensure save into couchdb
                user['update_timestamp'] = couch.now() # update timestamp
                userres = couch.updatedoc(f'userdb/{uid}', user)
                if userres.status_code in [200, 201, 202]: 
                    global total_num_retrieve_tweets
                    total_num_retrieve_tweets += len(tweets)
                    print('the length of the timeline is {l}'.format(l = len(tweets)))
                    print(f'done at the {retries} retries.')
                    return True
                else:
                    print(f'Retries {retries}, {userres.status_code} at userres.')
            else:
                print(f'Retries {retries}, {tweetres.status_code} at tweetres.')
        except Exception as e: # connection error
            print(f'Retries {retries}, tweets saving progress: {str(e)}')
            time.sleep(10)
        retries += 1
    print("search tweet failed at connection error at the last.")
    return False

def get_api(tokens, i): 
    consumer_key = tokens[i]['consumer_key']
    consumer_secret = tokens[i]['consumer_secret']
    access_token_key = tokens[i]['access_token_key']
    access_token_secret = tokens[i]['access_token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def run_search(i:int):
    rate_limit = i # set the rate_limit for this search
    cities = couch.geocode().keys()
    query = dict(selector = {"type": "search"}, fields = ["consumer_key", "consumer_secret", "access_token_key","access_token_secret"]) 
    res = couch.post(f'tokens/_find', body = query)
    tokens = res.json()['docs']
    tokens = tokens * 10

    latest_id = None  # where last round of search stopped 

    # for user 
    for city in cities:
        for i in range(len(tokens)):
            api = get_api(tokens, i): 
            # find the users
            job, latest_id = search_user(' ', city, api, rate_limit, latest_id)
            if job == True:
                latest_id = None # reset the latest_id
                print('{c} is done.\n\n'.format(c = city))
                break # next city
            else:
                print(f'token {i} has been used, max_id is {latest_id}.')
    print("\n\nUSER SEARCH COMPLETED.\n\n")

    time.sleep(600) # wait for data compaction

    # get ulist of all users
    users = []
    for row in couch.get('userdb/_all_docs?include_docs=true').json()['rows']:
        users.append(row['doc'])

    # Get node index
    index = -1
    rows = couch.get('nodes/_all_docs').json()['rows']
    if rows is None:
        index = 0
    else: 
        for row in rows: 
            if row['id'] == settings.DJANGO_NODENAME:
                index += 1
    workers = len(rows) if rows is not None else 1

    # assign node to corresponding block 
    interval = len(users)//(workers)
    assign_list = []
    for i in range(workers):
        assign_list.append(i * interval)
    assign_list.append(len(users))

    start = assign_list[index] # closed at left, open at the right
    end = assign_list[index + 1] -1 

    print(f'search start from user {start} ends at user {end}.')

    users = users[start:end]

    # for timelines of users
    for user in users:
        for i in range(len(tokens)):
            api = get_api(tokens, i): 
            # find the users
            job = search_tweet(user, api, 3000)
            if job == True:
                print('{u} in {c} is done.'.format(u = user["_id"], c = user['city']))
                break # next user
            else:
                print('move to next token and continue to search {u} in {c}.'.format(u = user["_id"], c = user['city']))
