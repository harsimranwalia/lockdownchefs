from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext


def format_message(app, msg):
    return msg.format( **{
        "bold_open": "<b>",
        "bold_close": "</b>",
        "newline": "<pre>\n</pre>"
    })
    

def start_handler(update, context):
    '''
    This function gets called when user starts communication with the bot
    which is /start command
    '''
    start_msg = "Hi, are you always thinking about what to cook?{newline}{newline}Think no more, automatically get food options delivered to you at the right time."
    msg = format_message("telegram", start_msg)
    # context.bot.send_message(chat_id=update.effective_chat.id, text=start_msg)
    update.message.reply_html(msg)


def message_handler(update, context):
    '''
    This function gets called when user sends a message to the bot
    '''
    msg = update.message.text



