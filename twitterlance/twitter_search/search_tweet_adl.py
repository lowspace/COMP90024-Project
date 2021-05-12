import json
import tweepy
from tweepy import OAuthHandler
import os
# import twitter_search.config as config
import config
# import couchdb.couch as couch
import couch
import time
import datetime
import sys

global total_num_retrieve_tweets, total_memory_cost, timeline_limit

total_num_retrieve_tweets = 0
total_memory_cost = 0
timeline_limit = 3000 # for each user, retrieve 3000 tweets maximally for the first time

def toJson(tweets):
    twitter = []
    for i in tweets:
        twitter.append(i._json)
    return twitter

def tweet_search(uid: str, city: str, api, ID: str):
    """
    The function crawls timeline of the uid
    Input:
        uid = uid
        city = city
        ID = tid in that uid's timeline
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

    def de_dup(ts: list) -> list:
        """
        remove the duplication tweets in this list
        Input = a list of structured tweet list
        Ouput = a list of structured tweet list after de_duplication
        """
        tid_set = set()
        new_ts = []
        for t in ts: 
            if t['_id'] not in tid_set: # new tid adds to the set
                tid_set.add(t['_id'])
                new_ts.append(t) # append new id tweet
            else:
                print("there is a duplication in ID {i}.".format(i = t['_id']))
        return new_ts

    def save_as_json(ts: list, uid: str, city: str):
        """
        save the de_duplication structured tweet list to a json file for one user
        """
        cwd = os.getcwd() # get current dir
        city_path = os.path.join(cwd, city) # get the city foloder path
        try:
            os.mkdir(city_path) # create the folder for the city
        except:
            pass
        file_name = uid + '.json' # file name format = uid.json
        file_path = os.path.join(city_path, file_name) # get file path
        with open(file_path, "w", encoding='utf-8') as output: # write to json
                json.dump(ts, output)

    tweets = [] # return object
    global timeline_limit 
    try:
        new_tweets = toJson(api.user_timeline(user_id = uid, count = 200))
    except:
        print("First trial failed, we can try another token.")
        ID = None
        return False, ID

    while True: # get the tweets
        if len(new_tweets) == 0: # no tweet returns
            break
        if len(new_tweets) == 200:
            maxid = str(new_tweets[-1]['id']-1)
            for tweet in new_tweets:
                tweet = tweet_2_dict(tweet, city) # convert tweet to be structured
                tweets.append(tweet)
            # # divide the new_tweets into the first 100 part and the second 100 part
            # #   and feed the 100 tweets into CouchDB once
            # first = []
            # for tweet in new_tweets[:100]: 
            #     # shape the tweet data structure
            #     ???
            #     first.append(tweet)
            # # feed the first to CouchDB
            # ???
            # second = []
            # for tweet in new_tweets[100:]: 
            #     # shape the tweet data structure
            #     ???
            #     second.append(tweet)
            #     first.append(tweet)
            # # feed the second to CouchDB
            # ???
            # if len(tweets) >= 400: 
            #     break
            if len(tweets) >= timeline_limit: # some users have a large timeline
                print("for each user, retrieve {l} tweets maximally".format(l = timeline_limit))
                break
            try:
                new_tweets = api.user_timeline(user_id =uid, count=200, max_id=maxid)
                new_tweets = toJson(new_tweets)
            except:
                print("Error occurs in the progress at tid, {t} of uid,{u}".format(t=maxid, u = uid) )
                return False, maxid
        else:
            for tweet in new_tweets:
                tweet = tweet_2_dict(tweet, city) # convert tweet to be structured
                tweets.append(tweet)
            # res = []
            # for tweet in new_tweets:
            #     # shape the tweet data structure
            #     ???
            #     res.append(tweet)
            # # feed the res to CouchDB
            # ???
            break
    # save the file as json
    # de duplication
    tweets = de_dup(tweets)
    # save_as_json(tweets, uid, city)
    couch.bulk_save('tweetdb', tweets)
    global total_num_retrieve_tweets
    total_num_retrieve_tweets += len(tweets)
    global total_memory_cost
    total_memory_cost += sys.getsizeof(tweets) # sum the memory of the tweets
    print('the length of the timeline is {l}'.format(l = len(tweets)))
    print('done at the last')
    return True, None

if __name__ == '__main__':

    cities = dict(
    # the string must contain 0 space
    Adelaide  = "-34.9998826,138.3309816,40km",
    # Sydney = "-33.8559799094,151.20666584,50km",
    # Melbourne = "-37.8142385,144.9622775,40km" ,
    # Perth = "-32.0391738, 115.6813561, 40km",
    # Canberra ="-35.2812958,149.124822,40km",
    # Brisbane =  "-27.3812533, 152.713015, 40km",
    # Hobart ="-42.8823389, 147.3110468, 40km",
)
    tokens = config.token
    ID = None

    c_dict = dict(
    Melbourne = "mel",
    Adelaide = "adl",
    Sydney = "syd",
    Canberra = "cbr",
    Perth = "per", 
    Brisbane = "bne",
    )

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
        c_id = c_dict[city]
        limit = couch.get(f'userdb/_design/cities/_view/{c_id}') # get the total user num of this city
        limit = limit.json()["total_rows"] + 1
        query = dict(selector = {"city": city}, fields = ["_id", "city", 'update_timestamp', '_rev'], limit = limit) 
        response = couch.post(path = 'userdb/_find', body = query) # get users list of dict
        json_data = response.json()['docs'] # load response as json
        for i in json_data: # get the user list
            if i['update_timestamp'] == None:
                users.append(i) # update the timeline
                continue
            previous_update_timestamp = i['update_timestamp']
            previous_update_timestamp = datetime.datetime.strptime(previous_update_timestamp, '%a %b %d %H:%M:%S %z %Y')
            previous_update_timestamp = previous_update_timestamp.astimezone(tz=None).strftime('%Y-%m-%d %H:%M:%S')
            if datetime.datetime.now() - datetime.datetime.fromisoformat(previous_update_timestamp) > datetime.timedelta(days=7):
                users.append(i) # update the timeline
                continue
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
                job, ID = tweet_search(users[i]["_id"], city, api, ID)
                if job == True:
                    ID = None # initilize the ID
                    print('{u} in {c} is done.'.format(u = users[i]["_id"], c = city))
                    break # next user
                else:
                    print('move to next token and continue to search {u} in {c}.'.format(u = users[i]["_id"], c = city))
                    continue # use next token 
            # transform datetime into Twitter format
            now_update_timestamp = datetime.datetime.now().astimezone(tz=datetime.timezone.utc).strftime('%a %b %d %H:%M:%S %z %Y')
            users[i]["update_timestamp"] = now_update_timestamp # assign the update timeline timestamp
            post_id = users[i]["_id"]
            couch.put(f'userdb/{post_id}', users[i]) # update the information in userdb
            t2 = time.time()
            print('Have retrieved {c:,} tweets, they cost {f:.3f} MB memory'.format(c = total_num_retrieve_tweets, f = total_memory_cost/(1024**2)))
            print('success to save {c}/{t} users into CouchDB'.format(c = i+1, t = len(users)))
            print('Have cost {t:.3f} seconds in {c}; average cost time {s:.3f} seconds for each user'.format(c = city, t = t2-t1, s = (t2-t1)/(i+1)))
            print('Total cost time is {t:.3f} mins.'.format(t = (t2 - t0)/60))
            print('Estimated time to complete {t:.3f} mins.'.format(t = (len(users)-i-1)*(t2-t1)/(i+1)/60))
            print('\n')