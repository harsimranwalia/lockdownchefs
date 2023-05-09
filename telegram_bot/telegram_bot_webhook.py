from telegram_handlers import *
from config import TELEGRAM
from telegram import Update
from helpers.telegram_bot import TelegramBot

'''
- This module can be used to deploy telegram webhook on AWS Lambda serverless.
- Everytime a new message update happens on bot in telegram this lambda function (webhook) is called.
- The updates (i.e messages) are handled by the handlers defined while creating the bot object
'''

def lambda_handler(event, context):
    # Initiate telegram bot with the handlers
    telegram_bot = TelegramBot(
        token=TELEGRAM['token'], 
        start_handler=start_handler, 
        msg_handler=message_handler,
        messages_mode="webhook"
    )

    bot = telegram_bot.bot
    dispatcher = telegram_bot.dispatcher

    # Upon receiving an update (i.e. message) from telegram, process it (i.e. call the right handler)
    dispatcher.process_update(
        Update.de_json(json.loads(event["body"]), bot)
    )

    return {"statusCode": 200}