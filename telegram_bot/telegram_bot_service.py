from config import TELEGRAM
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from helpers.telegram_bot import TelegramBot
from telegram_handlers import *

'''
- This module can be used to run the bot as a service.
- It will continuously poll telegram to get the new message updates.
- The updates (i.e messages) are handled by the handlers defined while creating the bot object
'''

# Initiate telegram bot with the handlers
telegram_bot = TelegramBot(
    token=TELEGRAM['token'], 
    start_handler=start_handler, 
    msg_handler=message_handler,
)

print(telegram_bot.get_webhook())

# Job queue
# jq = telegram_bot.updater.job_queue
# jq.run_once(send_food_option, 1)
# jq.run_repeating(send_food_option, interval=86400, first=0)

# Start the bot
telegram_bot.updater.start_polling()

# Wait till ctrl+c command is given or the program is interuppted to end the bot
telegram_bot.updater.idle()


# chat_id = "307705210"
# chat_id = "771963109"
# # send_food_option(chat_id)
# import datetime
# print(datetime.datetime.today().weekday())