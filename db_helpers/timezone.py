from bson.objectid import ObjectId
from .dbconfig import db_conn

class Timezone:
    def __init__(self):
        self.collection = db_conn['timezones']

    def get_timezone(self,country):
        return self.collection.find_one({"CountryName": country.title()}, ['TimezoneData'])

    def get_all_timezones(self):
        return self.collection.find({}, ['TimezoneData','CountryName'])


if __name__ == '__main__':
    import json
    import os
    tz_obj = Timezone()

    for tz in tz_obj.get_all_timezones():
        print(tz['CountryName'])
        for t in tz['TimezoneData']:
            print(t['Name'])


    def insert_timezones():
        with open(os.getcwd()+'/db_helpers/data_files/timezones.json') as f:
            timezones = json.loads(f.read())
            f.close()

        
        tz_obj.collection.delete_many({})
        for tz in timezones:
            if len(tz["WindowsTimeZones"]) == 0:
                print("0 timezones")
                print(tz)
                continue
            elif len(tz["WindowsTimeZones"]) == 1:
                tz['Multiple'] = False
                utc_delta = tz['WindowsTimeZones'][0]['Name'].split(' ')[0]
                tz['TimezoneData'] = [{
                    "Name":utc_delta+" "+tz['WindowsTimeZones'][0]['Id'].replace(' Standard ',' '),
                    "UtcDelta":utc_delta.split('UTC')[1][:-1]
                }]
            else:
                tz['Multiple'] = True
                tz['TimezoneData'] = []
                for wtz in tz['WindowsTimeZones']:
                    utc_delta = wtz['Name'].split(' ')[0]
                    tz['TimezoneData'].append({
                        "Name":utc_delta+" "+wtz['Id'].replace(' Standard ',' '),
                        "UtcDelta":utc_delta.split('UTC')[1][:-1]
                    })    
            # print(tz['TimezoneData'])
            tz_obj.collection.insert_one(tz)
    
        print(tz_obj.collection.count_documents())