# author Zihao Hu
# time 4/29/2021
import tweepy
import configparser
import json
import time
from shapely.geometry import Point, Polygon
from http.client import IncompleteRead as http_incompleteRead
from urllib3.exceptions import IncompleteRead as urllib3_incompleteRead
import couchdb.couch as couch

def test():
    return couch.new_id()

# load json file
def json_load(url):
    with open(url, 'r') as f:
        data = json.load(f)
        return data

Syd = [149.928, -34.345, 151.645, -32.976]
Can = [148.747, -35.926, 149.420, -35.106]
Mel = [144.312, -38.506, 145.894, -37.160]
Ade = [138.422, -35.355, 139.052, -34.493]
overall = [144.312, -38.506, 151.645, -32.976]

# read melbourne shape json
areas = json_load("TOP4city.json")["features"]

# read area list
area_list = []
for i in areas:
    area_list.append(i["attributes"]["GCC_NAME16"])

# generate authon

consumer_key = 'wku1JIpNi4pXukXp510Hzylj2'
consumer_secret = 'JZPuJKqMZu929iu8XxgTQAOw0up1LLJj6hKUjFDPE4aSNsp1KP'
access_token = '1382968455989583874-9DiykvjpUlnYtq2fJAgScghh9TMBs2'
access_token_secret = 'k6C6Yx8LNkNp5FtyG55d6WZ0lwePYbAYAmnkg5xOd65G6'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# connect CouchDB dataset
server = "http://admin:Aa123456789@localhost:5984"
couch.base_url = server

# get the userlist
users = []
response = couch.get(path = 'userdb/_all_docs', body='') # get users list of dict
json_data = response.json()['rows'] # load response as json
for i in json_data:  # get the user list
    users.append(i['id'])


def area_match(longitude, latitude, area):
    # if the point is in a polygon returns True
    within = False
    point = Point(longitude, latitude)
    for i in area["geometry"]["rings"]:
        polygon = Polygon(i)
        if point.within(polygon):
            within = True
    return within


def coor_area(longitude, latitude, areas):
    # matching the tweet's coordinate to city
    area_NAME = "out"
    for area in areas:
        if area_match(longitude, latitude, area):
            area_NAME = area["attributes"]["GCC_NAME16"]
            break
    return area_NAME


def new_user(tweetJson, area):
    # if new user then add to database
    user = {}
    user["_id"] = tweetJson["user"]["id_str"]
    user["city"] = area
    if user["_id"] in users:
        print('not a new user')
        return False # return ???
    else:
        print("got new user in", area)
        users.append(user["_id"])
        couch.save('userdb', user)
        return True


def new_tweet(tweetJson, area):
    # save new tweet to couchdb
    tweettemp = {}
    tweettemp["_id"] = area + ':' + tweetJson["id_str"]
    tweettemp["uid"] = tweetJson["user"]["id_str"]
    tweettemp["city"] = area
    tweettemp["value"] = tweetJson
    try: # save directly, no need to retrive all, since too slow?
        print('got new tweet')
        couch.save('tweetdb', tweettemp)
        return True
    except:
        print("error new tweet")
        return False


def new_timeline(tweetJson, area):
    # add user's tweet to database
    uid = tweetJson["user"]["id"]
    cursor = tweepy.Cursor(api.user_timeline, user_id=uid)
    tweets = [] # return object
    for tweet in cursor.items(200):
        tweettemp = {}
        tjson = tweet._json
        tweettemp["_id"] = area + ':' + tjson["id_str"]
        tweettemp["uid"] = tjson["user"]["id_str"]
        tweettemp["city"] = area
        tweettemp["value"] = tjson
        tweets.append(tweettemp)
    try:
        print("got new timeline")
        couch.bulk_save('tweetdb', tweets)
        return True
    except:
        print("error: new timeline")
        return False


def AddUserTweet2DB(tweetJson):
    # locate the tweet to the region
    if tweetJson['coordinates']:
        # coordinates to city
        longitude = tweetJson['coordinates']['coordinates'][0]
        latitude = tweetJson['coordinates']['coordinates'][1]
        t_area = coor_area(longitude, latitude, areas)
    elif tweetJson["place"] and tweetJson["place"]['bounding_box']:
        # bounding box to city
        box_coor = tweetJson['place']['bounding_box']['coordinates'][0]
        longitude = (box_coor[0][0] + box_coor[2][0]) / 2
        latitude = (box_coor[0][1] + box_coor[2][1]) / 2
        t_area = coor_area(longitude, latitude, areas)
    else:
        t_area = "out"
    if t_area != "out":
        if new_user(tweetJson, t_area):
            new_timeline(tweetJson, t_area)
        else:
            new_tweet(tweetJson, t_area)
    else:
        print('Not in target area')


class MyStreamListener(tweepy.StreamListener):
    def on_data(self, data):
        try:
            tweetJson = json.loads(data)
            AddUserTweet2DB(tweetJson)
            return True

        except BaseException as e:
            print(e)
            time.sleep(10)
            return True

        except http_incompleteRead as e:
            print(e)
            time.sleep(10)
            return True

        except urllib3_incompleteRead as e:
            print(e)
            time.sleep(10)
            return True

    def on_error(self, status_code):
        print(status_code)
        if status_code == 429:
            time.sleep(15 * 60 + 1)
        if status_code == 420:
            time.sleep(60)
        else:
            time.sleep(60)
        return True


if __name__ == '__main__':

    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")

    # Loop to save the tweets that meet the requirements in CouchDB
    while True:
        try:
            myStream = tweepy.Stream(auth=api.auth, listener=MyStreamListener())
            myStream.filter(locations=overall)

        except Exception as e:
            print(e)
