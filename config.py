import os

class Config:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI") # set environment variable - mongodb://127.0.0.1:27017

    def get_mongo_uri(self):
        return self.mongo_uri

obj = Config()
MONGO_URI = obj.get_mongo_uri()