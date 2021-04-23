# author Zihao Hu
# time 4/23/2021
import tweepy
import couchdb
import configparser
import json
import time
from shapely.geometry import Point, Polygon

# load json file
def json_load(url):
    with open(url, 'r') as f:
        data = json.load(f)
        return data

# read melbourne shape json
areas = json_load("melbourne.json")["features"]

# read SA4 list
SA4_list = []
for i in areas:
    SA4_list.append(i["attributes"]["SA4_NAME16"])


def area_match(longitude, latitude, area):
    # if the point is in a polygon returns True
    point = Point(longitude, latitude)
    polygon = Polygon(area["geometry"]["rings"][0])
    return point.within(polygon)


def coor_area(longitude, latitude, areas):
    # matching the tweet's coordinate to city
    SA4_NAME = "out"
    for area in areas:
        if area_match(longitude, latitude, area):
            SA4_NAME = area["attributes"]["SA4_NAME16"]
            break
    return SA4_NAME

def check_add2db(tweet):
    t_id = tweet["_id"]
    record = None
    if tweet["SA4_name"] != "out" and tweet["SA4_name"] != None:
        # tweet should be in the target area
        for rec in cdb.view('_all_docs', key=t_id):
            record = rec
        if record != None:
            print("already exist")
        else:
            print("got a new tweet")
            cdb.save(tweet)

def stream_tweet_norm(tweetJson):
    # convert tweet json to normalized data
    try:
        tweet = {}
        tweet["_id"] = tweetJson["id_str"]
        if tweetJson.get('user'):
            tweet["user_id"] = tweetJson["user"]["id_str"]
        tweet["SA4_name"] = "out"
        tweet["text"] = tweetJson["text"]
        tweet["language"] = tweetJson["lang"]
        tweet['hashtags'] = None
        if tweetJson['entities']:
            if tweetJson['entities']['hashtags']:
                tweet['hashtags']=tweetJson['entities']['hashtags'][0]['text']
        if tweetJson['timestamp_ms']:
            tweet['timestamp'] = tweetJson['timestamp_ms']
        # locate the tweet to the SA4 region
        if tweetJson['coordinates']:
            # coordinates to city
            longitude = tweetJson['coordinates']['coordinates'][0]
            latitude = tweetJson['coordinates']['coordinates'][1]
            tweet["SA4_name"] = coor_area(longitude, latitude, areas)
            print("coord from 1")
#             SA4_name = coor_area(longitude, latitude, tweetJson)
#             if SA4_name in SA4_list:
#                 tweet["SA4_name"] = SA4_name
        elif tweetJson["place"] and tweetJson["place"]['bounding_box']:
            # bounding box to city
                box_coor = tweetJson['place']['bounding_box']['coordinates'][0]
                longitude = (box_coor[0][0] + box_coor[2][0]) / 2
                latitude = (box_coor[0][1] + box_coor[2][1]) / 2
                tweet["SA4_name"] = coor_area(longitude, latitude, areas)
                print("coord from 2")
        else:
            print("do not get coord")
        # later version tweet will add to database directly
        check_add2db(tweet)

    except Exception as e:
        print(e)
        print("something wrong in stream_tweet_norm")
        time.sleep(10)


class MyStreamListener(tweepy.StreamListener):

    def on_data(self, data):
        tweetJson = json.loads(data)
        stream_tweet_norm(tweetJson)

    def on_error(self, status_code):
        print(status_code)

if __name__ == '__main__':

    # Generate Authentication
    config = configparser.ConfigParser()
    try:
        config.read("tokensimon.conf")
    except:
        print("token Configuration not found")
    consumer_key = config.get('Token', 'Consumer Key')
    consumer_secret = config.get('Token', 'Consumer Secret')
    access_token = config.get('Token', 'Access Token')
    access_token_secret = config.get('Token', 'Access Token Secret')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)


    # Create CouchDB dataset
    server = couchdb.Server("http://admin:Aa123456789@localhost:5984")
    if 'twitterdb' in server:
        cdb = server['twitterdb']
    else:
        cdb = server.create('twitterdb')

    # Loop to save the tweets that meet the requirements in CouchDB
    while True:
        try:
            myStream = tweepy.Stream(auth=api.auth, listener=MyStreamListener())
            myStream.filter(locations=[144.3120, -38.506, 145.894, -37.16])

        except Exception as e:
            print(e)
            print("something wrong")
