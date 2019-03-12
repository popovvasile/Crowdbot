# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler)
from database import users_messages_to_admin_table, chats_table
from modules.helper_funcs.auth import initiate_chat_id

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1
MESSAGE_TO_USERS = 1


class SendMessageToAdmin(object):
    @run_async
    def start_answering(self, bot, update):
        bot.send_message(update.message.chat_id, "What do you want to tell us?")
        return MESSAGE

    @run_async
    def received_message(self, bot, update):
        bot.send_message(update.message.chat_id,
                         "Thank you! Your message has been sent to the chatbot owner!")
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


class SendMessageToUsers(object):
    @run_async
    def start_answering(self, bot, update):
        bot.send_message(update.message.chat_id, "What do you want to tell your users?\n"
                                                 "We will forward your message to all your users."
                                                 "p.s. You name will be displayed as well")
        return MESSAGE_TO_USERS

    @run_async
    def received_message(self, bot, update):
        chat_id, txt = initiate_chat_id(update)

        chats = chats_table.find()
        for chat in chats:
            bot.forward_message(chat_id=chat["chat_id"], from_chat_id=chat_id, message_id=update.message.id)
        bot.send_message(update.message.chat_id,
                         "Thank you! We've sent your message to your users!")

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
        print("TEST")
        messages = users_messages_to_admin_table.find({"bot_id": bot.id})
        if messages:
            for message in messages:
                if message["timestamp"] + datetime.timedelta(days=14) > datetime.datetime.now():
                    bot.send_message(update.message.chat_id, "User's fullname:{}, \n"
                                                             "Message:{}".format(message["full_name"],
                                                                                 message["message"]))

        else:
            bot.send_message(update.message.chat_id, "You have no incoming messages yet")


SEND_MESSAGE_TO_ADMIN_HANDLER = ConversationHandler(
    entry_points=[CommandHandler("Send_message", SendMessageToAdmin().start_answering)],

    states={
        MESSAGE: [MessageHandler(Filters.all,
                                 SendMessageToAdmin().received_message)],

    },

    fallbacks=[
               CommandHandler('cancel', SendMessageToAdmin().error),
               MessageHandler(filters=Filters.command, callback=SendMessageToAdmin().error)]
)

SEND_MESSAGE_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler("Send_message_to_users", SendMessageToUsers().start_answering)],

    states={
        MESSAGE_TO_USERS: [MessageHandler(Filters.all,
                                 SendMessageToUsers().received_message)],

    },

    fallbacks=[
               CommandHandler('cancel', SendMessageToUsers().error),
               MessageHandler(filters=Filters.command, callback=SendMessageToUsers().error)]
)

SEE_MESSAGES_HANDLER = CommandHandler("See_Inbox_Messages", SeeMessageToAdmin().see_messages)


__mod_name__ = "Send a message"
__visitor_help__ = """
Here you can send a message to the chatbot owner

"""


__visitor_keyboard__ = [["/Send_message"]]


__admin_help__ = """
Messages sent by the users to you
"""


__admin_keyboard__ = [["/See_Inbox_Messages", "/Send_message_to_users"]]
