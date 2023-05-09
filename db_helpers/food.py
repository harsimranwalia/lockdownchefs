from bson.objectid import ObjectId
from .dbconfig import db_conn
from .airtable_db import get_data


class Food:
    collection = db_conn['foods']
    source = "airtable"
    airtable_tables = { #table/sheet name
        "food": "food",
        "cuisine": "cuisines"
    }

    # def __init__(self)
        

    def get_food(self, id=None, meal="breakfast", cuisines=None):
        if self.source == "mongodb":
            if id is not None:
                return self.collection.find({"_id": ObjectId(id)})

            return self.collection.find({"meal": meal})
        
        elif self.source == "airtable":
            return get_data(self.airtable_tables['food'], cuisines=cuisines)


    def get_cuisines(self):
        cuisines = [{'id': 5, 'name': 'American', 'code': 'american'}, {'id': 2, 'name': 'South Indian', 'code': 'south_indian'}, {'id': 6, 'name': 'Parantha', 'code': 'parantha'}, {'id': 1, 'name': 'Indian', 'code': 'indian'}]
        return cuisines

        # if self.source == "airtable":
        #     return get_data(self.airtable_tables['cuisine'])


    def save_food(self, obj):
        return self.collection.insert_one(obj)


if __name__ == '__main__':
    food = Food()
    print(get_data("cuisines"))
    # print(food.get_food(cuisines=["american","parantha"]))
    # import json
    # with open('db_helpers/data_files/food.json') as f:
    #     foods = json.loads(f.read())
    #     f.close()

    # for food in foods:
    #     print(save_food(food).inserted_id)
    # foods = get_food(id="5eb7d4e960cf04186be364fb")
    # foods = collection.delete_many({'name': 'Grilled Cheese Sandwich'})
    # for x in foods:
    #     print(x)