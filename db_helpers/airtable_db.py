import json
from airtable import airtable

api_key = "key091MLeo2IGsbDh" # account api key
base_id = "appXbRWUGQurMQ88E" # db base (lockdownchefs)
at = airtable.Airtable(base_id, api_key)

def create_filter_formula(filters=None, logical="OR"):
    filter_str = logical + "("
    for key, value in filters.items():
        if type(value) == list:
            for f in value:
                filter_str += "{" + key + "}='" + f + "',"
        elif type(value) == str:
            filter_str += "{" + key + "}='" + value + "'"

        if filter_str[-1] == ",": filter_str = filter_str[:-1]
        filter_str += ")" 

    # print(filter_str)
    return filter_str


def get_data(table_name, cuisines=None):
    result = []
    filter_formula = None

    if cuisines is not None:
        filters = {"cuisine": cuisines}
        filter_formula = create_filter_formula(filters)

    items = at.get(table_name, filter_by_formula=filter_formula)
    items = json.loads(json.dumps(items))['records']
    for item in items:
        result.append(item['fields'])
    
    return result


    
