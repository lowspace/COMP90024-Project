import tweepy
import couchdb.couch as couch
import time
from django.conf import settings

global total_num_retrieve_tweets
total_num_retrieve_tweets = 0

def toJson(tweets):
    tweet = []
    for i in tweets:
        tweet.append(i._json)
    return tweet

def search_user(query: str, city: str, api, rate_limit = 10, latest_id = None, count = 0):
    """
    This function tends to obtain the uid of the tweets with the query
    Input:
        query = what we wann search
        city = couch.geocode().keys()
        latest_id = str, of the last tid
        count = how many brand new users have benn added, breakpoint
    Output:
        1. save the uid into CouchDB 
        2. save the uid locally (for now)
    """
    ulist = [] # list of uid
    res = couch.get(f'users/_all_docs') # get the id list of all
    res = res.json()['rows']
    for row in res:
        if row["id"] in ulist:
            continue
        else:
            ulist.append(row["id"])
    city_dict = couch.geocode() # get city {city_name: geocode, }
    geocode = city_dict[city] # get geocode
    if not latest_id: # latest_id = None
        first = toJson(api.search(q = query, geocode = geocode, count=66)) # consider loss tweets
    else: # latest_id != None
        first = toJson(api.search(q = query, geocode = geocode, max_id = latest_id, count=66))
    # print('NEW first', first)
    if len(first) == 0 and count < rate_limit:
        print('NEW query contains nothing, move to next token.')
        return False, latest_id, count
    maxid = str(first[0]['id']-1)
    t1 = time.time()
    while True:
        if count >= rate_limit: # 
            break
        try:
            # convert search results into Json file
            tweets = toJson(api.search(q = query, geocode = geocode, count = 200, max_id = maxid))
        except:
            print(f'NEW Have retrieved {count}/{rate_limit}, but unable to continue on this token.')
            return False, maxid, count # to be continued
        if len(tweets) != 0 and count < rate_limit: # search query return tweets
            for tweet in tweets: # add brand new users to save list
                new_users = []
                if tweet['user']['id_str'] not in ulist:
                    ulist.append(tweet['user']['id_str'])
                    user = dict()
                    uid = tweet['user']['id_str']
                    user['_id'] = uid
                    user['city'] = city
                    user['update_timestamp'] = None # assign None to the timestamp
                    new_users.append(user)
                   #print('NEW new user is', user)
            retries = 0
            success = False
            while retries < 5:
                try:
                    res = couch.bulk_save('users', new_users)
                    if res.status_code == 201: # ensure save into couchdb
                        success = True
                        break
                    else:
                        print(f'NEW Retries {retries}, {res.status_code} at user_search.')
                except Exception as e: # connection error
                    print(f'NEW Retries {retries}, user saving progress: {str(e)}')
                    time.sleep(10)
                retries += 1
            if success == False:
                print("NEW user search failed at connection error at {maxid}.")
            else:
                t2 = time.time()
                count += len(new_users)
                print('NEW Progress {c}/{t}.'.format(c = count, t = rate_limit))
                print('NEW Have cost {t:.3f} seconds; average cost time {s:.3f} seconds'.format(t = t2 - t1, s = (t2-t1)/count if count != 0 else 0))
                print('NEW Estimated time to complete {t:.3f} mins.'.format(t = (rate_limit-count)*(t2-t1)/count/60 if count != 0 else 0))  
                maxid = str(tweets[-1]['id']-1)             
        else: # search query return None
            print(f'NEW Have retrieved {count}/{rate_limit}, but unable to query more.')
            break
    return True, maxid, count

def get_api(tokens, i): 
    consumer_key = tokens[i]['consumer_key']
    consumer_secret = tokens[i]['consumer_secret']
    access_token_key = tokens[i]['access_token_key']
    access_token_secret = tokens[i]['access_token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

def run_search(i:int):
    rate_limit = i # set the rate_limit for this search
    cities = couch.geocode().keys()
    query = dict(selector = {"type": "search"}, fields = ["consumer_key", "consumer_secret", "access_token_key","access_token_secret"]) 
    res = couch.post(f'tokens/_find', body = query)
    tokens = res.json()['docs']
    tokens = tokens * 10

    # for user 
    for city in cities:
        latest_id = None  # where last round of search stopped 
        count = 0 # how many users have been added in this city
        for i in range(len(tokens)):
            api = get_api(tokens, i)
            # find the users
            job, latest_id, count = search_user(' ', city, api, rate_limit, latest_id, count)
            if job == True:
                print('NEW {c} is done.\n\n'.format(c = city))
                break # next city
            else:
                print(f'NEW token {i} has been used, max_id is {latest_id}, have added {count} users.')
    print("NEW USER SEARCH COMPLETED.\n\n")

    return True