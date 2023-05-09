from telegram import ParseMode, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, Defaults, Dispatcher


class TelegramBot:

    def __init__(self, token, messages_mode="polling", parse_mode=ParseMode.HTML, start_handler=None, msg_handler=None, CallbackQueryHandler=None):
        # set default values
        self.parse_mode = parse_mode
        defaults = Defaults(parse_mode=parse_mode)
        
        if messages_mode == "polling":
            self.updater = Updater(token=token, use_context=True, defaults=defaults)
            self.dispatcher = self.updater.dispatcher
        elif messages_mode == "webhook":
            self.bot = Bot(token)
            self.dispatcher = Dispatcher(self.bot, None, workers=0, use_context=True)
        
        # /start command handler
        start_handler = CommandHandler('start', start_handler)
        self.dispatcher.add_handler(start_handler)
        
        # Regular messages handler
        echo_handler = MessageHandler(Filters.text & (~Filters.command), msg_handler)
        self.dispatcher.add_handler(echo_handler)

        # Handling unknown commands
        unknown_handler = MessageHandler(Filters.command, self.unknown)
        self.dispatcher.add_handler(unknown_handler)

    def unknown(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

    def get_webhook(self):
        return self.dispatcher.bot.get_webhook_info()

    def send_message(self, chat_id, msg, reply_markup):
        self.bot.send_message(chat_id, msg, reply_markup=reply_markup, parse_mode=self.parse_mode)

    def update_inline_keyboard(self, chat_id, msg_id, reply_markup):
        self.bot.edit_message_reply_markup(chat_id=chat_id, message_id=msg_id, reply_markup=reply_markup, parse_mode=self.parse_mode)
