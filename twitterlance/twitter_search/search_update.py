import tweepy
import couchdb.couch as couch
import time, datetime, random
from django.conf import settings


def toJson(tweets):
    tweet = []
    for i in tweets:
        tweet.append(i._json)
    return tweet

def search_tweet(user: dict, api, timeline_limit= 400):
    """
    The function crawls timeline of the uid
    Input:
        user = dict of user
        timeline_limit = 400 # dafault for 400
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
    except Exception as e:
        print(f"[search] UPDATE First trial failed, we can try another token: {str(e)}")
        return False

    while True: # get the tweets

        # stop the job if the user asked
        res = couch.get(f'jobs/stream/')
        assert res.status_code != 404, '[search] Job not found in Jobs.'
        assert res.json().get('status', '') != 'idle', '[search] Job stopped.'

        if len(new_tweets) == 0: # no tweet returns
            break
        if len(new_tweets) == 200:
            maxid = str(new_tweets[-1]['id'] - 1)
            for tweet in new_tweets:
                tweet = tweet_2_dict(tweet, city) # convert tweet to be structured
                tweets.append(tweet)
            if len(tweets) >= timeline_limit: # some users have a large timeline
                print("[search] UPDATE for each user, retrieve {l} tweets maximally".format(l = timeline_limit))
                break
            try:
                new_tweets = api.user_timeline(user_id = uid, count = 200, max_id = maxid)
                new_tweets = toJson(new_tweets)
            except:
                print("[search] UPDATE Error occurs in the progress at tid, {t} of uid,{u}".format(t = maxid, u = uid))
                return False # move to next token
        else:
            for tweet in new_tweets:
                tweet = tweet_2_dict(tweet, city) # convert tweet to be structured
                tweets.append(tweet)
            break

    retries = 0
    while retries < 5:
        try:
            tweetres = couch.bulk_save('tweets', tweets)
            if tweetres.status_code in [200, 201, 202]: # ensure save into couchdb
                user['update_timestamp'] = couch.now() # update timestamp
                userres = couch.put(f'users/{uid}', user)
                if userres.status_code in [200, 201, 202]: 
                    print('[search] UPDATE the length of the timeline is {l}'.format(l = len(tweets)))
                    print(f'[search] UPDATE done at the {retries} retries.')
                    return True
                else:
                    print(f'[search] UPDATE Retries {retries}, {userres.status_code} at userres.')
            else:
                print(f'[search] UPDATE Retries {retries}, {tweetres.status_code} at tweetres.')
        except Exception as e: # connection error
            print(f'[search] UPDATE Retries {retries}, tweets saving progress: {str(e)}')
            time.sleep(10)
        retries += 1
    print("[search] UPDATE search tweet failed at connection error at the last.")
    return False

def get_api(tokens, i): 
    consumer_key = tokens[i]['consumer_key']
    consumer_secret = tokens[i]['consumer_secret']
    access_token_key = tokens[i]['access_token_key']
    access_token_secret = tokens[i]['access_token_secret']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token_key, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api

def assign_users():
    # get ulist of all users
    users = []
    try:
        for row in couch.get('users/_all_docs?include_docs=true').json()['rows']:
            users.append(row['doc'])
    except Exception as e:
        print(f'[search] UPDATE Unable to get ulist due to {e}.')
        print('[search] UPDATE the machine will wait for another 10 mins, then try again.')
        time.sleep(200) # wait for data compaction
        for row in couch.get('users/_all_docs?include_docs=true').json()['rows']:
            users.append(row['doc'])
        print('[search] UPDATE Success to get ulist after waiting 10 mins.')

    # Get node index
    index = -1
    rows = couch.get('nodes/_all_docs').json()['rows']
    print(f'[search] Nodes: {rows}')
    if rows is None:
        index = 0
    else: 
        for i in range(len(rows)): 
            row = rows[i]
            print(f'[search] {row["id"]} == {settings.DJANGO_NODENAME}')
            if row['id'] == settings.DJANGO_NODENAME:
                index = i
    workers = len(rows) if rows is not None else 1

    # assign node to corresponding block 
    interval = len(users)//(workers)
    assign_list = []
    for i in range(workers):
        assign_list.append(i * interval)
    assign_list.append(len(users))

    start = assign_list[index] # closed at left, open at the right
    end = assign_list[index + 1] - 1 

    print(f'[search] UPDATE update start from user {start} ends at user {end}.')

    users = users[start:end]

    return users, index

def run_update():
    query = dict(selector = {"type": "search"}, fields = ["consumer_key", "consumer_secret", "access_token_key","access_token_secret"]) 
    res = couch.post(f'tokens/_find', body = query)
    tokens = res.json()['docs']
    tokens = tokens * 10
    random.shuffle(tokens)

    users, index = assign_users()

    print(f'[search] {len(users)}:{index}')

    # for timelines of users
    t0 = time.time()
    count = 0
    for user in users:
        t1 = time.time()
        count += 1
        for i in range(len(tokens)):
            api = get_api(tokens, i) 
            # find the users
            previous_timestamp = user.get('update_timestamp', None)
            if previous_timestamp == None:
                job = search_tweet(user, api, 3000)
            else:
                previous_timestamp = datetime.datetime.strptime(previous_timestamp, '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=datetime.timezone.utc) 
                now_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)
                time_diff = now_timestamp - previous_timestamp
                if datetime.timedelta(days = 5) < time_diff <= datetime.timedelta(days = 7):
                    job = search_tweet(user, api, 400) # for each user, retrieve 200 tweets maximally for each 7 days
                elif datetime.timedelta(days = 7) < time_diff <= datetime.timedelta(days = 14):
                    job = search_tweet(user, api, 800) # for each user, retrieve 800 tweets maximally for each 14 days
                elif time_diff > datetime.timedelta(days = 14):
                    job = search_tweet(user, api, 3000)
                else: 
                    break
            if job == True:
                t2 = time.time()
                print('[search] UPDATE {u} in {c} is done.'.format(u = user["_id"], c = user['city']))
                print('[search] UPDATE success to update {c}/{t} users into CouchDB'.format(c = count, t = len(users)))
                print('[search] UPDATE Cost {t:.3f} seconds for this user; average cost time {s:.3f} seconds for each user'.format(t = t2-t1, s = (t2-t0)/count))
                print('[search] UPDATE Total cost time is {t:.3f} mins.'.format(t = (t2 - t0)/60))
                print('[search] UPDATE Estimated time to complete {t:.3f} mins at instance {i}.'.format(t = (len(users)-count)*(t2-t0)/count/60, i = index))
                print('[search] UPDATE \n')
                break # next user
            else:
                print('[search] UPDATE move to next token and continue to search {u} in {c}.'.format(u = user["_id"], c = user['city']))