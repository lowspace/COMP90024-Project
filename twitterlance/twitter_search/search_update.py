import time, datetime
import couchdb.couch as couch
from .search_new import search_tweet, get_api

def assign_users():
    # get ulist of all users
    users = []
    try:
        for row in couch.get('users/_all_docs?include_docs=true').json()['rows']:
            users.append(row['doc'])
    except Exception as e:
        print(f'UPDATE Unable to get ulist due to {e}.')
        print('UPDATE the machine will wait for another 10 mins, then try again.')
        time.sleep(600) # wait for data compaction
        for row in couch.get('users/_all_docs?include_docs=true').json()['rows']:
            users.append(row['doc'])
        print('UPDATE Success to get ulist after waiting 10 mins.')

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
    end = assign_list[index + 1] - 1 

    print(f'UPDATE search start from user {start} ends at user {end}.')

    users = users[start:end]

    return users, index

def run_update():
    query = dict(selector = {"type": "search"}, fields = ["consumer_key", "consumer_secret", "access_token_key","access_token_secret"]) 
    res = couch.post(f'tokens/_find', body = query)
    tokens = res.json()['docs']
    tokens = tokens * 10

    users, index = assign_users()

    # for timelines of users
    t0 = time.time()
    for user in users:
        t1 = time.time()
        count = 0
        for i in range(len(tokens)):
            api = get_api(tokens, i) 
            # find the users
            time_diff = couch.now() - user['update_timestamp']
            if datetime.timedelta(days = 5) < time_diff <= datetime.timedelta(days = 7):
                job = search_tweet(user, api, 400) # for each user, retrieve 200 tweets maximally for each 7 days
            elif datetime.timedelta(days = 7) < time_diff <= datetime.timedelta(days = 14):
                job = search_tweet(user, api, 800) # for each user, retrieve 800 tweets maximally for each 14 days
            else:
                job = search_tweet(user, api, 3000)
            if job == True:
                t2 = time.time()
                print('UPDATE {u} in {c} is done.'.format(u = user["_id"], c = user['city']))
                print('UPDATE success to update {c}/{t} users into CouchDB'.format(c = count, t = len(users)))
                print('UPDATE Cost {t:.3f} seconds for this user; average cost time {s:.3f} seconds for each user'.format(t = t2-t1, s = (t2-t1)/count))
                print('UPDATE Total cost time is {t:.3f} mins.'.format(t = (t2 - t0)/60))
                print('UPDATE Estimated time to complete {t:.3f} mins at instance {i}.'.format(t = (len(users)-count)*(t2-t1)/count/60, i = index))
                print('UPDATE \n')
                break # next user
            else:
                print('UPDATE move to next token and continue to search {u} in {c}.'.format(u = user["_id"], c = user['city']))