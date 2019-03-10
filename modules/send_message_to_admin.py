# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime

from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler)

import logging

from database import users_messages_to_admin_table

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1


class SendMessageToAdmin(object):
    @run_async
    def start_answering(self, bot, update, user_data):
        bot.send_message(update.message.chat_id, "What do you want to tell us?")
        return MESSAGE

    @run_async
    def received_message(self, bot, update, user_data):
        bot.send_message(update.message.chat_id,
                         "Thank you! Your message has bee registered")
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


class SeeMessageToAdmin(object):
    @run_async
    def see_messages(self, bot, update):
        for message in users_messages_to_admin_table.find({"bot_id": bot.id}):
            if message["timestamp"] + datetime.timedelta(days=30) > datetime.datetime.now():
                bot.send_message(update.message.chat_id, "User's fullname:{}, \n"
                                                         "Message:{}".format(message["full_name"],
                                                                             message["message"]))


SEND_MESSAGE_HANDLER = ConversationHandler(
    entry_points=[CommandHandler("send_message_to_admin", SendMessageToAdmin().start_answering)],

    states={
        MESSAGE: [MessageHandler(Filters.all,
                                 SendMessageToAdmin().received_message,
                                 pass_user_data=True)],

    },

    fallbacks=[
               CommandHandler('cancel', SendMessageToAdmin().error, pass_user_data=True),
               MessageHandler(filters=Filters.command, callback=SendMessageToAdmin().error)]
)

SEE_MESSAGES_HANDLER = CommandHandler("see_the_messages", SeeMessageToAdmin().see_messages)


__mod_name__ = "Send message to the chatbot owner"
__user_help__ = """
Send message to the chatbot owner

"""


__user_keyboard__ = [["/send_message_to_admin"]]


__admin_help__ = """
Messages sent by the users to you
"""


__admin_keyboard__ = [["/see_the_messages"]]
