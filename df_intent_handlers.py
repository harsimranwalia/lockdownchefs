import _thread
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from helpers.notification import format_message
from db_helpers import User, Timezone, Food
from bson.objectid import ObjectId

user_obj = User()
tz_obj = Timezone()
food_obj = Food()

def mailchimp_user_subscribe(subscriber_data):
    df_data = {"intent": "location_personalisation"}

    # subscriber_data = subscriber_data['data']  <-- this is needed in case of mailchimp webhook
    subscriber_data['source'] = "mailchimp"
    
    user_data = {}
    user_data['source'] = "email"
    user_data['source_id'] = subscriber_data['id']
    user_data['email'] = subscriber_data['email']
    user_data['first_name'] = subscriber_data['merge_fields']['FNAME']
    user_data['last_name'] = subscriber_data['merge_fields']['LNAME']
    user_data['language_code'] = 'en'
    # Save the user access points from multiple apps
    user_data['email_data'] = subscriber_data
    user_data['connected_apps'] = "email"
    df_data['user'] = user_data

    entities = {"geo-country": subscriber_data['merge_fields']['TIMEZONE']}
    has_tz = False
    if "(UTC" in entities['geo-country']:
        has_tz = True
        entities['geo-country'] = entities['geo-country'].split(" (UTC")[0]
    df_data['entities'] = entities
    # Save the user details
    resp = update_user_pref(df_data)

    # Update the user timezone if his country contained the timezone information
    if has_tz:
        df_data['intent'] = "user_timezone"
        tz_info = entities['geo-country'].split(" (")
        entities['timezone_info'] = "(" + tz_info[1] + "_" + tz_info[1][3:9]
        
        del entities['geo-country']
        resp = update_user_pref(df_data)

    return resp


def ask_cuisine_personalisation(df_data=None, liked=[]):
    if df_data is not None:
        db_user = user_obj.get_users({"source": df_data['user']['source'], "source_id": df_data['user']['source_id']})[0]
        liked = db_user.get('cuisines',[])

    cuisines = food_obj.get_cuisines()
    keyboard = []
    for cuisine in cuisines:
        selected = "✅ " if cuisine['code'] in liked else ""
        keyboard.append([InlineKeyboardButton(selected+cuisine['name'], callback_data="cuisine-"+cuisine['code'])])
    reply_markup = InlineKeyboardMarkup(keyboard)
    return_resp = {"msg":"Choose your favourite cuisines to personalise recommendations", "inline_buttons_markup": reply_markup}
    return return_resp


def upd_user_in_db(params, update):
    user_obj.update_user(params, update)


def update_user_pref(df_data):
    intent = df_data['intent']
    user = df_data['user'].copy()
    entities = df_data['entities']

    if intent == "cuisine_personalisation":
        cuisine = entities['cuisine']
        db_user = user_obj.get_users({"source": user['source'], "source_id": user['source_id']})[0]
        user_cuisines = db_user.get('cuisines',[])

        # User has either selected / unselected the option
        try:
            # If the cuisine already exists, that means user has unselected the option
            user_cuisines.remove(cuisine)
        except:
            # Removal failed, hence add the cuisine as the user has newly selected the option
            user_cuisines.append(cuisine)

        _thread.start_new_thread( upd_user_in_db,
                ({"source": user['source'], "source_id": user['source_id']}, {"cuisines": user_cuisines}) )
        return ask_cuisine_personalisation(liked=user_cuisines)
    
    elif intent == "user_timezone":
        timezone_info = entities['timezone_info'].split('_')
        timezone_info = {"timezone": timezone_info[0], "utc_delta": timezone_info[1]}
        user_obj.update_user({"source": user['source'], "source_id": user['source_id']}, timezone_info)
        return {"msg": "Great! You are all set now. Wait for tomorrow to get your breakfast surprise.", "inline_buttons_markup": None}
    
    elif intent == "location_personalisation":
        user['country'] = entities['geo-country']
        if "geo-city" in entities and entities['geo-city'] != "":
            user['city'] = entities['geo-city']
         
        # Get user timezone to send notifications at the right time
        tz_record = tz_obj.get_timezone(user['country'])
        if tz_record is not None:
            timezones = tz_record['TimezoneData']
            if len(timezones) == 1:
                user['utc_delta'] = timezones[0]['UtcDelta']
                user['timezone'] = timezones[0]['Name']
                return_resp = {"msg": "Great! You are all set now. Wait for tomorrow to get your breakfast surprise.", "inline_buttons_markup": None}    
            else:
                keyboard = []
                for tz in timezones:
                    keyboard.append([InlineKeyboardButton(tz['Name'], callback_data="user_timezone "+tz['Name']+"_"+tz['UtcDelta'])])
                reply_markup = InlineKeyboardMarkup(keyboard)
                return_resp = {"msg":"Kindly help me identify your timezone by clicking on the appropriate button", "inline_buttons_markup": reply_markup}
            
        # Help choose the right country as I cant match the country name to my database
        else:
            print(entities)
            return_resp = {}
        
        # Save the apps list that user has connected
        if "connected_apps" not in user: user['connected_apps'] = user['source'] 
        # Push app data for use later
        source_data_key = user['source'] + "_data"
        if source_data_key not in user: user[source_data_key] = df_data['user']
        
        push_data = {"connected_apps": user['connected_apps']} #, "apps_data": user['apps_data']}
        del user['connected_apps']
        try: user.remove('msg_id')
        except: pass
        
        db_return = user_obj.update_user({"source": user['source'], "source_id": user['source_id']}, user, add_to_list=push_data, upsert=True)
        print(db_return.acknowledged)
        return return_resp


def get_food_option(next_from=None, meal="breakfast", cuisines=None):
    food_options = food_obj.get_food(meal=meal, cuisines=cuisines)
    try:
        num_options = food_options.count()
    except:
        num_options = len(food_options)

    # If the user has requested next option on previously shown option
    if next_from is not None:
        curr_food_id = int(next_from[2:])
        next_option_id = (curr_food_id+1)%num_options
        if next_option_id == curr_food_id:
            next_option_id = (next_option_id+1)%num_options
        food = food_options[next_option_id]
    # Send a random food option
    else:
        import random
        # we used `num_options-1` because randint includes this number as array index, which in other case will make array go out of bound
        option_num = random.randint(0, num_options-1)
        food = food_options[option_num]
    
    msg = "Here is your breakfast option for today:"+ \
        "{newline}{newline}{bold_open}"+food['name']+"{bold_close}"+ \
        "{newline}<a href='"+food['image_url']+"'>&#8205;</a>"
    msg = format_message("telegram", msg)

    keyboard = [[InlineKeyboardButton("Recipe", url=food['recipe_url'])],
                [InlineKeyboardButton("Next Option",  callback_data="nextOption id"+str(food['id']))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    return {"msg": msg, "inline_buttons_markup": reply_markup, "option":food}


def fetch_food_option(df_data, meal="breakfast"):
    intent = df_data['intent']
    user = user_obj.get_users({"source": df_data['user']['source'], "source_id": df_data['user']['source_id']},{"cuisines"})
    cuisines = user[0].get('cuisines', None)

    if intent == "Next food option":
        food = get_food_option(next_from=df_data['entities']['source_food_id'], cuisines=cuisines)
    else:
        food = get_food_option(meal=meal, cuisines=cuisines)
    
    return {"msg": food['msg'], "inline_buttons_markup": food['inline_buttons_markup']}


def get_tz_users(tz=None, all_users=False):
    if all_users:
        users = user_obj.get_users({})
    else:
        users = user_obj.get_users({"utc_delta": tz})
    return users

if __name__ == '__main__':
    '''
    user_obj.delete_user(id="5ed91aa09215b0f122d362f4")
    # user_obj.insert_user({'source': 'telegram', 'source_id': '771963109', 'country': 'Netherlands', 'first_name': 'Kd', 'language_code': 'en', 'timezone': '(UTC+01:00) W. Europe Time', 'utc_delta': '+01:00'})
    # mailchimp_user_subscribe({'type': 'subscribe', 'fired_at': '2020-05-18 12:52:45', 'data': {'id': '883f57a2aa', 'email': 'harsimran007@gmail.com', 'email_type': 'html', 'ip_opt': '172.17.10.10', 'web_id': '204280544', 'merge_fields': {'EMAIL': 'harsimran007@gmail.com', 'FNAME': '', 'LNAME': '', 'ADDRESS': '', 'PHONE': '', 'BIRTHDAY': '', 'TIMEZONE': 'India'}, 'list_id': 'b6e44d7c5f'}})
    # user_obj.update_user({"_id":ObjectId("5ec294159215b0f122dc7efd")},{"$set":{"id":"9043246747501502d57c5bfab30e554e"}})
    '''
    print(fetch_food_option({"intent":"breakfast_option", "user":{"source":"telegram", "source_id":"307705210"}}))
    # user_obj.delete_user(id="5ed91aa09215b0f122d362f4")
    # user_obj.collection.update({}, {"$unset": {"cuisines":1}}, multi=True, upsert=False)
    # users = get_tz_users(tz="+05:30", all_users=True)
    # # print(list(users))
    # for x in users:
    #     # print(x)
    #     print(x['_id'].generation_time, x.get('cuisines',''))
    #     print(x['first_name'],x.get('email',''), x['connected_apps'])
