import requests, uuid, json

class Couch:
    def __init__(self):
        self.base_url = 'http://admin:password@localhost:5984'

    def new_id(self):
        return uuid.uuid4().hex

    def get(self, database, document_id):
        if document_id is None: 
            document_id = ''
        return requests.get(self.base_url + '/' + database + '/' + document_id)

    def put(self, database, json_document):
        if json_document is None: 
            return requests.put(self.base_url + '/' + database)
        else: 
            return requests.put(self.base_url + '/' + database + '/' + self.new_id(), json=json_document)