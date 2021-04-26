from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from ...couch import Couch
import json

class Command(BaseCommand):
    help = 'Initialise the databses required by this app'
    
    def get_design_geo(self):
        f = open(f'{settings.BASE_DIR}/analyser/design_docs/geo/indexes/box/index.js')
        geo = {
            "_id": "geo",
            "indexes": {
                "box": {
                    "analyzer": "standard",
                    "index": f.read()
                }
            }

        }
        assert geo["indexes"]["box"]["index"] not in [None, '']
        f.close()
        return geo

    def handle(self, *args, **options):
        couch = Couch()

        # Create twitter database
        res = couch.head(f'/twitter')
        if res.status_code == 404:
            res = couch.put(f'/twitter')
            assert res.status_code in [200, 201], 'database "twitter" cannot be created: ' + res.text
        elif res.status_code != 200: 
            raise Exception('error code ' + res.status_code)
        
        # Create design documents
        res = couch.head(f'/twitter/_design/geo/')
        if res.status_code == 404:
            res = couch.put(f'/twitter/_design/geo/', body=self.get_design_geo())
            assert res.status_code in [200, 201], 'design document "geo" cannot be created: ' + res.text
        elif res.status_code != 200: 
            raise Exception(res.status_code)

        self.stdout.write(self.style.SUCCESS('Successfully initilised design documents'))