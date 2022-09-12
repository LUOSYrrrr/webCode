from pymongo import *


class Mongo():
    def __init__(self,config):
        self.config=config
        self.client=MongoClient(self.config.mongo['host'],self.config.mongo['port'])
        self.db=self.client[self.config.mongo['db']]
        print('connect mongodb.....')

    # return json
    def select_one(self, collection, query=None, projection=None):
        if projection is None:
            projection = {'_id': 0}
        try:
            collection=self.db[collection]
        except Exception as e:
            print(e)
        return collection.find_one(filter=query,projection=projection)


    # return list
    def select_all(self, collection, query=None, projection=None):
        if projection is None:
            projection = {'_id': 0}
        try:
            collection=self.db[collection]
        except Exception as e:
            print(e)
        return collection.find(filter=query,projection=projection)

    def getallid(self, collection):
        allid=[]
        for item in self.select_all(collection=collection,projection={'id':1,'_id':0}):
            allid.append(item['id'])
        return allid





