# import sys
# import os
# sys.path.append(os.path.join(os.path.dirname(os.getcwd()),"couchdb"))

import couch as couch
import json
import datetime
import sys
import search_new

def test():
    print(couch.put('testdb').json())
    print(couch.save('testdb', {'_id': '1'}).json())
    print(couch.bulk_save('testdb', [{'_id': '1'}, {'_id': '2'}]).json())


# # query = dict(selector = {"city": 'Melbourne', 'update_timestamp': None}, fields = ["_id", "city"], limit = 10) 
# for city in ["Melbourne", "Sydney", "Canberra", "Adelaide"]:
#     query = dict(selector = {"city": city}, fields = ["_id", "city", 'update_timestamp', '_rev'],  limit = 10000) 
#     response = couch.post(path = 'userdb/_find', body = query) # get users list of dict
#     response = response.json()['docs']
#     for i in response:
#         if 'update_timestamp' not in i.keys():
#             i['update_timestamp'] = None
#             couch.put(f'userdb/{ID}', i) 
#         if i['update_timestamp']:
#             print("sth", i['_id'], i)
#     print(f'{city} done\n\n')

# ID = '123'
# i = {'123':123}
# couch.put(f'userdb/{ID}', i) 

# search_new.run_search()