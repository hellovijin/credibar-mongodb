from django.conf import settings
from pymongo.mongo_client import MongoClient
from pymongo.errors import ConnectionFailure

import os

class connections:
    def __init__(self):
        self.dbusername = os.getenv("{}_USERNAME".format( settings.DB_PREFIX ), '')
        self.dbpassword = os.getenv("{}_PASSWORD".format( settings.DB_PREFIX), '')
        self.connection_uri = "mongodb+srv://{}:{}@credibar.nixkgbb.mongodb.net/"
    
    def connect(self):
        try:
            self.client = MongoClient( self.connection_uri.format( self.dbusername, self.dbpassword ) )
            self.client.admin.command('ismaster')
            return self.client[ os.getenv("{}_NAME".format( settings.DB_PREFIX ), '') ]
        except Exception as e:
            print( e )
            raise Exception("Database Server not available")
    
    def disconnect(self):
        self.client.close()