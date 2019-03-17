# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler)
import logging
from database import users_messages_to_admin_table
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1


class SendScamReport(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_report")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def start_answering(self, bot, update, user_data):
        bot.send_message(update.message.chat_id, "Did you find out that this chatbot is a scam? \n"
                                                 "Please describe us the details and we will try to solve this issue")
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
        get_help(bot, update)

        return ConversationHandler.END


SEND_SCAM_REPORT_HANDLER = ConversationHandler(
    entry_points=[CommandHandler("send_scam_report", SendScamReport().start_answering)],

    states={
        MESSAGE: [MessageHandler(Filters.all,
                                 SendScamReport().received_message,
                                 pass_user_data=True)],
    },
    fallbacks=[CallbackQueryHandler(callback=SendScamReport().cancel, pattern=r"cancel_report"),
               CommandHandler('cancel', SendScamReport().error, pass_user_data=True),
               MessageHandler(filters=Filters.command, callback=SendScamReport().error)]
)


__mod_name__ = "Scam Report"

__visitor_help__ = """
Report a scam
"""


__visitor_keyboard__ = [["/send_scam_report"]]
