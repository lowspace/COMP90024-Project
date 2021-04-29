
import analyser.couch as couch

def test():
    print(couch.put('testdb').json())
    print(couch.save('testdb', {'_id': '1'}).json())
    print(couch.bulk_save('testdb', [{'_id': '1'}, {'_id': '2'}]).json())