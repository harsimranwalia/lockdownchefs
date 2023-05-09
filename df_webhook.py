import datetime
from dialogflow.input import main
from dialogflow.output import build_telegram_response
from telegram_bot.bot_interface import TelegramBot
from helpers.timezone import get_timezone_offset
from config import TELEGRAM, BREAKFAST_TIME, ASK_PREFERENCE_DAYS_AFTER
from df_intent_handlers import *
from mailchimp import get_new_subscribers
from email_service.ses import send_email
from msg_content import email_content

telegram_bot = TelegramBot(token=TELEGRAM['token'], messages_mode="webhook")


def lambda_handler(event, context):
    if "devtest" in event:
        users = get_tz_users(tz="", all_users=True)
        for user in users:
            if user['source_id'] == "307705210":
                break
        user_subscribed_since = (datetime.datetime.utcnow() - user['_id'].generation_time.replace(tzinfo=None)).days
        print(user_subscribed_since)
        if "cuisines" not in user:
            cuisine_msg = ask_cuisine_personalisation()
            telegram_bot.send_message(user['source_id'], cuisine_msg['msg'], cuisine_msg['inline_buttons_markup'])

        food = get_food_option(cuisines=user.get('cuisines', None))
        print(food)

    # Scheduled cloudwatch event every 30 min
    elif "detail-type" in event and event['detail-type'] == "Scheduled Event":
        # Mailchimp get new subscribers added in last 35 min (30min lambda frequency+5min buffer)
        subscribers = get_new_subscribers(timedelta_mins=35)
        for subscriber in subscribers:
            print(subscriber)
            mailchimp_user_subscribe(subscriber)

        # get the timezone offset of current utc time from the notification scheduled time
        utc_now = datetime.datetime.utcnow()
        date_today = str(datetime.date.today())
        notif_time = datetime.datetime.strptime(date_today+" "+BREAKFAST_TIME, "%Y-%m-%d %H:%M")
        tz_offset = get_timezone_offset(utc_now, notif_time)

        # Get the users in the timezone where the time now is notification sending time
        users = get_tz_users(tz=tz_offset, all_users=False)
        for user in users:
            # Get the food option
            user_cuisines = user.get('cuisines', None)
            if user_cuisines is not None and len(user_cuisines) == 0:
                user_cuisines = None
            food = get_food_option(cuisines=user_cuisines)
            
            for app in user['connected_apps']:
                if app == "telegram":
                    try:
                        telegram_bot.send_message(user['source_id'], food['msg'], food['inline_buttons_markup'])
                        
                        # Ask for cuisine preferences if not already set
                        user_subscribed_since = (datetime.datetime.utcnow() - user['_id'].generation_time.replace(tzinfo=None)).days
                        if "cuisines" not in user and user_subscribed_since > ASK_PREFERENCE_DAYS_AFTER:
                            cuisine_msg = ask_cuisine_personalisation()
                            telegram_bot.send_message(user['source_id'], cuisine_msg['msg'], cuisine_msg['inline_buttons_markup'])
                    except:
                        pass
                    
                elif app == "email":
                    subject = email_content['food_option']['subject']
                    subject = subject.format(food['option']['name'])

                    body_html = email_content['food_option']['body_html']
                    body_html = body_html.format(food['option']['name'], 
                                            food['option']['image_url'], 
                                            food['option']['recipe_url'])
                    send_email(user['email'], subject, body_html=body_html)


    # Dialogflow webhook call
    elif "queryResult" in event:
        print(event)
        df_data = main(event)
        intent = df_data['intent']
        update_inline = False
        # print(df_data)
        
        if intent in ["location_personalisation", "user_timezone"]:
            resp = update_user_pref(df_data)
        elif intent == "cuisine_personalisation":
            resp = update_user_pref(df_data)
            update_inline = True
            update_inline_message = "Cuisine preferences updated"
        elif intent == "breakfast_option" or intent == "option_today":
            resp = fetch_food_option(df_data, meal="breakfast")
        elif intent == "Next food option":
            resp = fetch_food_option(df_data)
        elif intent == "command_cuisine":
            resp = ask_cuisine_personalisation(df_data=df_data)

        # Assuming the dialogflow is only connected to telegram for now
        if update_inline:
            telegram_bot.update_inline_keyboard(df_data['user']['source_id'], 
                                df_data['user']['msg_id'], resp['inline_buttons_markup'])
            resp = build_telegram_response(output=update_inline_message)
        else:
            resp = build_telegram_response(output=resp['msg'],
                    inline_buttons=resp['inline_buttons_markup'])

        return resp


    '''
    # Mailchimp subscriber addition webhook call
    else:
        print(event)
        event = mailchimp_callback_data_to_json(event)
        resp = mailchimp_user_subscribe(event)
        return resp
    '''