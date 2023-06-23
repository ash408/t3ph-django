
import pymongo

from pymongo import MongoClient


class DB():

    def __init__(self, system, game, data_types):
        self.client = MongoClient(serverSelectionTimeoutMS = 2000)
        
        if type(data_types) is str:
            self.data_types = {data_types}
        else:
            self.data_types = set(data_types)
        
        self.system = system
        self.game = game
        self.db_name = system + ':' + game

        self.set_game(self.db_name, self.data_types)

    def list_databases():
        client = MongoClient(serverSelectionTimeoutMS = 2000)
        databases = client.list_database_names()
        returned_dbs = []

        for database in databases:
            if ':' in database:
                returned_dbs.append(database)

        return returned_dbs

    def set_game(self, db_name, data_types):
        self.db = self.client[db_name]
        
        if data_types:
            data_types = set(data_types)

            for data_type in data_types:
                self.db[data_type].create_index([('uid', pymongo.ASCENDING)], unique = True)

    def make(self, obj_dict, data_type):
        obj_dict = obj_dict.copy()

        self.db[data_type].insert_one(obj_dict)

    def save(self, obj_dict, data_type):
        obj_dict = obj_dict.copy()
        uid = obj_dict['uid']
        current_dict = self.load(uid, data_type)

        for key in current_dict.keys():
            if key not in obj_dict.keys():
                self.db[data_type].update_one({'uid': uid}, {'$unset': {key : ''}})

        self.db[data_type].update_one({'uid' : uid}, {'$set' : obj_dict})

    def load(self, uid, data_type=None):
        obj_dict = self.db[data_type].find_one({'uid' : uid})

        if obj_dict:
            del obj_dict['_id']
       
        return obj_dict

    def find(self, data_type, search = None):
        if search:
            objs = self.db[data_type].find(search)
        else:
            objs = self.db[data_type].find()

        return objs

    def remove(self, uid,  data_type):
        self.db[data_type].delete_one({'uid' : uid})
    

    def delete_game(system, game):
        databases = DB.list_databases()
        db_name = system + ':' + game

        client = MongoClient()

        if db_name in databases:
            client.drop_database(db_name)
            return True
        else:
            return False

