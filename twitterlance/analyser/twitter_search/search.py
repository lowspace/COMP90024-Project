import json
import tweepy
from tweepy import OAuthHandler

def toJson(tweets):
    twitter = []
    for i in tweets:
        twitter.append(i._json)
    return twitter

def tweet_search(keyword, geocode, api):
    user = []
    store = []
    first = toJson(api.search(q = keyword, geocode= geocode, count=1))
    if len(first) == 0:
        return None
    maxid = str(first[0]['id']-1)
    count = 0
    while True:
        twitter = toJson(api.search(q = keyword, geocode= geocode, count = 100, max_id = maxid))
        if len(twitter) !=0:
            maxid = str(twitter[-1]['id']-1)
            for i in twitter:
                if i['user']['id_str'] not in user:
                    count += 1
                    store.append(i['user']['id_str'])
                    user.append(i['user']['id_str'])
                    if len(store) == 100:
                        print(store)
                        store = []
                    if count == 10000:
                        if len(store) != 0:
                            print(store)
                        break
                       
        else:
            break
    return user

def user_search(id, api):
    new_tweets = toJson(api.user_timeline(user_id =id,count=200))
    while True:
        if len(new_tweets)==0:
            break
        if len(new_tweets)==200:
            maxid=str(new_tweets[-1]['id']-1)
            for tweet in new_tweets:
                print(tweet['place'])
                if tweet['place']!=None:
                    print(tweet['place']['name'])
            new_tweets = api.user_timeline(user_id =id,count=200, max_id=maxid)
            new_tweets=toJson(new_tweets)
        else:
            for tweet in new_tweets:
                print(tweet['place'])
                if tweet['place']!=None:
                    print(tweet['place']['name'])
            break
    return None

class SearchAPI():
    Geocode  = dict(
        melbourne = ["-37.8142385,144.9622775,40km", 'Rkupsy9IRz1LZFn5BnW41HieR', 'AJGztH99Xj8Ch3ueleBd95nUHS2L30tmmvRjiVEpri1qZyAlc4', '1383751844057391107-Tw0FTLNESkWFgq5OB9BkvjvlOjETot', '847AbkKGOcEp1SeiR3wNu5xvBgDaUS0EHd9iIeMx6nv50'],
        sydney = ["-33.8559799094,151.20666584,50km", 'Rkupsy9IRz1LZFn5BnW41HieR', 'AJGztH99Xj8Ch3ueleBd95nUHS2L30tmmvRjiVEpri1qZyAlc4', '1383751844057391107-Tw0FTLNESkWFgq5OB9BkvjvlOjETot', '847AbkKGOcEp1SeiR3wNu5xvBgDaUS0EHd9iIeMx6nv50'],
        perth = ["-32.0391738,115.6813561,40km", 'Rkupsy9IRz1LZFn5BnW41HieR', 'AJGztH99Xj8Ch3ueleBd95nUHS2L30tmmvRjiVEpri1qZyAlc4', '1383751844057391107-Tw0FTLNESkWFgq5OB9BkvjvlOjETot', '847AbkKGOcEp1SeiR3wNu5xvBgDaUS0EHd9iIeMx6nv50'],
        canberra = ["-35.2812958,149.124822,40km", 'Rkupsy9IRz1LZFn5BnW41HieR', 'AJGztH99Xj8Ch3ueleBd95nUHS2L30tmmvRjiVEpri1qZyAlc4', '1383751844057391107-Tw0FTLNESkWFgq5OB9BkvjvlOjETot', '847AbkKGOcEp1SeiR3wNu5xvBgDaUS0EHd9iIeMx6nv50'],
        brisbane = ["-27.3812533,152.713015,40km", 'Rkupsy9IRz1LZFn5BnW41HieR', 'AJGztH99Xj8Ch3ueleBd95nUHS2L30tmmvRjiVEpri1qZyAlc4', '1383751844057391107-Tw0FTLNESkWFgq5OB9BkvjvlOjETot', '847AbkKGOcEp1SeiR3wNu5xvBgDaUS0EHd9iIeMx6nv50'],
        hobart = ["-42.8823389,147.3110468,40km", 'Rkupsy9IRz1LZFn5BnW41HieR', 'AJGztH99Xj8Ch3ueleBd95nUHS2L30tmmvRjiVEpri1qZyAlc4', '1383751844057391107-Tw0FTLNESkWFgq5OB9BkvjvlOjETot', '847AbkKGOcEp1SeiR3wNu5xvBgDaUS0EHd9iIeMx6nv50'],
        adelaide  = ["-34.9998826,138.3309816,40km",'Rkupsy9IRz1LZFn5BnW41HieR', 'AJGztH99Xj8Ch3ueleBd95nUHS2L30tmmvRjiVEpri1qZyAlc4', '1383751844057391107-Tw0FTLNESkWFgq5OB9BkvjvlOjETot', '847AbkKGOcEp1SeiR3wNu5xvBgDaUS0EHd9iIeMx6nv50']
    )

    for city in Geocode.keys():
        auth = tweepy.OAuthHandler(Geocode[city][1], Geocode[city][2])
        auth.set_access_token(Geocode[city][3], Geocode[city][4])
        api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        result = tweet_search(" ",Geocode[city][0], api)
        if result !=None:
            users = result[1]
            for user in users:
                user_search(user, api)