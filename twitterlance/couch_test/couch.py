import requests, uuid, json, time

class Couch:
    def __init__(self):
        self.base_url = 'http://admin:password@localhost:5984'

    def new_id(self):
        return uuid.uuid4().hex

    def get(self, database, document_id):
        assert database is not None
        if document_id is None: 
            document_id = ''
        return requests.get(self.base_url + '/' + database + '/' + document_id)

    def create_db(self, database):
        return requests.put(self.base_url + '/' + database)

    # param document: records list of dict 
    def bulk_insert(self, database, records):
        assert database is not None
        assert records is not None

        for record in records: 
            if record["_id"] is None: 
                raise Exception('"_id" is missing')

        documents = {
            "docs": records
        }
        print(json.dumps(documents))
        return requests.post(self.base_url + '/' + database + '/_bulk_docs', json=documents)
        
    # param document: python dict with _id
    def insert(self, database, document):
        assert database is not None
        if document['_id'] is None: 
            raise Exception('"_id" is missing')
        return requests.put(self.base_url + '/' + database + '/' + document['_id'], json=document)

    def test(self):
        error = 0
        seconds = time.time()
        docs = []
        for i in range(0, 100):
            data = {"_id": self.new_id()}
            docs.append(data)
        res = self.bulk_insert('testok', docs)
        print(res.json())
        print("Seconds since epoch =", seconds - time.time())	
        return error
