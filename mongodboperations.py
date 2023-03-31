import pymongo
import os,sys
from bson.objectid import ObjectId
from logger import logging
from exception import ScrapperException

class MongoOperations:
    def __init__(self,mongo_uri="mongodb://127.0.0.1:27017", db_name="youtube_data_db",
                 collection_name="youtube_data_collection_sentiment"):
        """
        Definition: __init__(mongo_uri="mongodb://127.0.0.1:27017", db_name="youtube_data_db",
                            collection_name="youtube_data_collection")
        :param mongo_uri: connection uri str
        :param db_name:database name str
        :param collection_name: collection name str
        """
        self.mongo_uri= mongo_uri
        self.__db_name = db_name
        self.__collection_name = collection_name
        self.logger = logging.getLogger()

    def get_mongo_client(self):
        """
        :return: pymongo.MongoClient
        """
        try:
            # client = pymongo.MongoClient(self.__host, self.__port)
            client = pymongo.MongoClient(self.mongo_uri)
            return client
        except Exception as e:
            raise ScrapperException(e,sys)
            

    def close_client_connection(self, client):
        try:
            client.close()
        except Exception as e:
            raise ScrapperException(e,sys)

    def check_db(self, db_name):
        """
        :param db_name: str
        :return: Boolean
        """
        client = self.get_mongo_client()
        databases = client.list_database_names()
        self.close_client_connection(client)
        if db_name in databases:
            return True
        else:
            return False

    def check_collection(self, db_name, collection_name):
        """

        :param db_name: str
        :param collection_name: str
        :return: boolean
        """
        client = self.get_mongo_client()
        db = client[db_name]
        collections = db.list_collections()
        self.close_client_connection(client)
        if collection_name in collections:
            return True
        else:
            return False

    def insert_document_into_collection(self, document):
        """
        :param document: dict
        :return: object
        """
        try:
            client = self.get_mongo_client()
            db = client[self.__db_name]
            collection = db[self.__collection_name]
            document_id = collection.insert_one(document, bypass_document_validation=True)
            document_id = document_id.inserted_id
            self.close_client_connection(client)
            return document_id
        except Exception as e:
            raise ScrapperException(e,sys)
            

    def insert_many_document_into_collection(self, documents):
        """
        :param documents: list(dict)
        :return: list
        """
        try:
            client = self.get_mongo_client()
            db = client[self.__db_name]
            collection = db[self.__collection_name]
            document_id_list = collection.insert_many(documents,  bypass_document_validation=True).inserted_ids
            self.close_client_connection(client)
            return str(document_id_list)
        except Exception as e:
            raise ScrapperException(e,sys)

    def search_record_from_collection(self, document_id):
        """
        :param document_id: str
        :return: dict
        """
        try:
            client = self.get_mongo_client()
            db = client[self.__db_name]
            collection = db[self.__collection_name]
            search = {"_id": ObjectId(document_id)}
            self.logger.info(str(search))
            result = collection.find_one(search)
            self.close_client_connection(client)
            return result
        except Exception as e:
           raise ScrapperException(e,sys)
            

    def delete_record_from_collection(self, document_id):
        """
        :param document_id: str
        :return: dict
        """
        try:
            client = self.get_mongo_client()
            db = client[self.__db_name]
            collection = db[self.__collection_name]
            collection.delete_one({"_id":document_id})
            self.close_client_connection(client)
            self.logger(f"Document {document_id} deleted.")
        except Exception as e:
            raise ScrapperException(e,sys)
            


    def delete_collection(self,collection_name):
        """

        :param collection_name: str
        :return: None
        """
        try:
            client = self.get_mongo_client()
            db = client[self.__db_name]
            db.drop_collection(collection_name)
            self.close_client_connection(client)
            self.logger(f"Collection {collection_name} deleted.")
        except Exception as e:
            raise ScrapperException(e,sys)
            


    def delete_database(self,db_name):
        """
        :param db_name: str
        :return: None
        """
        try:
            client = self.get_mongo_client()
            client.drop_database(db_name)
            self.close_client_connection(client)
            self.logger(f"Database {db_name} deleted.")
        except Exception as e:
            raise ScrapperException(e,sys)
            
if __name__ == "__main__":
    obj = MongoOperations("mongodb://127.0.0.1:27017")
    print(obj.search_record_from_collection("63153b88cbadbdd1420cd57f"))

