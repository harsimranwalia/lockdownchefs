from bson.objectid import ObjectId
from .dbconfig import db_conn


class User:
    def __init__(self):
        self.collection = db_conn['users']

    def get_users(self, params, columns=None, sort=None):
        if sort is None:
            if columns is None:
                return self.collection.find(params)
            else:
                return self.collection.find(params, projection=columns)
        else:
            if columns is None:
                return self.collection.find(params, sort=sort)
            else:
                return self.collection.find(params, projection=columns, sort=sort)

    def update_user(self, filter, update, add_to_list=None, remove_from_list=None, upsert=False):
        update_dict = {"$set":update}
        if add_to_list is not None: update_dict.update({"$addToSet":add_to_list})
        if remove_from_list is not None: update_dict.update({"$pull":add_to_list})
        
        return self.collection.update_one(filter, update_dict, upsert=upsert)

    def insert_user(self, user):
        return self.collection.insert_one(user)

    def delete_user(self, id=None):
        if id is None:
            return self.collection.delete_many({})
            
        return self.collection.delete_one({"_id": ObjectId(id)})
