from datetime import datetime, timedelta, timezone
from .config import api_key, audience_list
from mailchimp3 import MailChimp

client = MailChimp(mc_api=api_key)

# returns all the audience lists (only name and id)
# audiences = client.lists.all(get_all=True, fields="lists.name,lists.id")
# print(audiences)
# {'lists': [{'id': 'b6e44d7c5f', 'name': 'Startup Experiments'}], 'total_items': 1}

# returns all members inside list 'b6e44d7c5f'
# members = client.lists.members.all('b6e44d7c5f', get_all=True, fields="members.email_address,members.merge_fields,members.ip_signup,members.ip_opt")
# print(members)

def get_new_subscribers(timedelta_mins=30):
    # get the ISOformat needed by mailchimp
    since_dt = datetime.utcnow().replace(microsecond=0).replace(tzinfo=timezone.utc) - timedelta(minutes=timedelta_mins)
    since_dt = since_dt.isoformat()

    member_fields = "members.id,members.list_id,members.email_address,members.merge_fields,members.ip_opt"
    members = client.lists.members.all(audience_list, status="subscribed", since_last_changed=since_dt, fields=member_fields)
    members = members['members']

    for i in range(len(members)):
        members[i]['email'] = members[i]['email_address']
        del members[i]['email_address']
    
    return members


def mailchimp_callback_data_to_json(data_in):
    data_out = {}
    data_in = dict(data_in)

    for key in data_in.keys():
        user_key = key.split('[')
        if len(user_key) == 1:
            key = user_key[0]
            data_out[key] = data_in[key]
        elif len(user_key) > 1:
            key1 = user_key[0]
            key2 = user_key[1][:-1]

            if key1 not in data_out:
                data_out[key1] = {}

            if len(user_key) == 2:
                data_out[key1][key2] = data_in[key]

            elif len(user_key) == 3:
                key3 = user_key[2][:-1]
                if key2 not in data_out[key1]:
                    data_out[key1][key2] = {}

                data_out[key1][key2][key3] = data_in[key]

    return data_out

# print(get_new_subscribers())