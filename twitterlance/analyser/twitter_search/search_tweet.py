import json
import tweepy
from tweepy import OAuthHandler
import os
import config
import couch as couch

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
        d['_id'] = t['id_str']
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
    save_as_json(tweets, uid, city)
    couch.bulk_save('twitter', tweets)
    print('the length of the timeline is {l}'.format(l = len(tweets)))
    print('done at the last')
    return True, None

if __name__ == '__main__':

    cities = config.Geocode.keys()
    tokens = config.token
    cwd = os.getcwd() # get current dir
    ID = None

    users = []
    response = couch.get(path = 'userdb/_all_docs', body = '') # get users list of dict
    json_data = response.json()['rows'] # load response as json
    for i in json_data: # get the user list
        users.append(i['id'])  

    for city in cities:
        # read id from csv
        # file_name = city + '.csv'
        # city_path = os.path.join(cwd, file_name) # get the city foloder path
        # with open(city_path, 'r') as f:
        #     ###
        #     # how to read this csv? the csv save without lose information, but open will
        #     ###
        for user in users: # user = uid
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
                job, ID = tweet_search(user, city, api, ID)
                if job == True:
                    ID = None # initilize the ID
                    print('{u} in {c} is done.'.format(u = user, c = city))
                    break # next user
                else:
                    print('move to next token and continue to search {u} in {c}.'.format(u = user, c = city))
                    continue # use next token 