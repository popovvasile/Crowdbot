# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler, Updater)
import logging
from database import users_messages_to_admin_table
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1


class SendScamReport(object):  # TODO
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_report")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def start_answering(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         "Please describe your problem and we will try to solve this issue")
        return MESSAGE

    @run_async
    def received_message(self, bot, update, user_data):
        bot.send_message(update.message.chat_id,
                         "Thank you! We will review your this chatbot asap")
        users_messages_to_admin_table.insert({"user_full_name": update.message.full_name,
                                              "chat_id": update.message.chat_id,
                                              "user_id": update.message.user_id,
                                              "message": update.message.text,
                                              "timestamp": datetime.datetime.now(),
                                              "bot_id": bot.id})
        return ConversationHandler.END

    @run_async
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(bot, update)

        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        callback=  get_help(bot, update)
        return ConversationHandler.END


REPORT_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('start', SendScamReport().start_answering)],

    states={
        MESSAGE: [MessageHandler(Filters.all,
                                 SendScamReport().received_message,
                                 pass_user_data=True)],
    },
    fallbacks=[CallbackQueryHandler(callback=SendScamReport().back, pattern=r"cancel_report"),
               CommandHandler('cancel', SendScamReport().back, pass_user_data=True),
               MessageHandler(filters=Filters.command, callback=SendScamReport().error)]
)


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("797824166:AAFyNk3Bh-OIvCDkKeaYPockxZG-fx2NDtI")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(REPORT_HANDLER)
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
