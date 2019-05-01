# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler)
from database import users_messages_to_admin_table, chats_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1
MESSAGE_TO_USERS = 1


class SendMessageToAdmin(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_message")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def send_message(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         "What do you want to tell us?", reply_markup=self.reply_markup)
        return MESSAGE

    @run_async
    def received_message(self, bot, update):
        bot.send_message(update.message.chat_id,
                         "Thank you! Your message has been sent to the chatbot owner!")
        users_messages_to_admin_table.insert({"user_full_name": update.message.from_user.full_name,
                                              "chat_id": update.message.chat_id,
                                              "user_id": update.message.from_user.id,
                                              "message": update.message.text,
                                              "timestamp": datetime.datetime.now(),
                                              "bot_id": bot.id})
        get_help(bot, update)
        return ConversationHandler.END

    @run_async
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )

        get_help(bot, update)
        return ConversationHandler.END


class SendMessageToUsers(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_message")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def send_message(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         "What do you want to tell your users?\n"
                                                 "We will forward your message to all your users."
                                                 "p.s. Your name will be displayed as well",
                         reply_markup=self.reply_markup)
        return MESSAGE_TO_USERS

    @run_async
    def received_message(self, bot, update):
        chat_id, txt = initiate_chat_id(update)

        chats = chats_table.find({"bot_id": bot.id})
        for chat in chats:
            bot.forward_message(chat_id=chat["chat_id"],  # TODO make it anonymous
                                from_chat_id=chat_id,
                                message_id=update.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_message")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.message.chat_id,
                         "Thank you! We've sent your message to your users!", reply_markup=final_reply_markup)

        return ConversationHandler.END

    @run_async
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )

        get_help(bot, update)
        return ConversationHandler.END


class SeeMessageToAdmin(object):
    @run_async
    def see_messages(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        messages = users_messages_to_admin_table.find({"bot_id": bot.id})
        if messages:
            for message in messages:
                if message["timestamp"] + datetime.timedelta(days=14) > datetime.datetime.now():
                    bot.send_message(update.callback_query.message.chat.id,
                                     "User's name: {}, \n\n"
                                      "Message: {}".format(message["user_full_name"],
                                      message["message"]))

        else:
            bot.send_message(update.callback_query.message.chat.id,
                             "You have no incoming messages yet")
        get_help(update=update, bot=bot)


SEND_MESSAGE_TO_ADMIN_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_admin", callback=SendMessageToAdmin().send_message),
                  CallbackQueryHandler(callback=SendMessageToUsers().back, pattern=r"cancel_send_message")],

    states={
        MESSAGE: [MessageHandler(Filters.all, SendMessageToAdmin().received_message),
                  CallbackQueryHandler(callback=SendMessageToUsers().back, pattern=r"cancel_send_message")],

    },

    fallbacks=[CallbackQueryHandler(callback=SendMessageToUsers().back, pattern=r"cancel_send_message"),
               CommandHandler('cancel', SendMessageToAdmin().error),
               MessageHandler(filters=Filters.command, callback=SendMessageToAdmin().error)]
)

SEND_MESSAGE_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_users", callback=SendMessageToUsers().send_message),
                  CallbackQueryHandler(callback=SendMessageToUsers().back, pattern=r"cancel_send_message")],

    states={
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendMessageToUsers().received_message),
                           CallbackQueryHandler(callback=SendMessageToUsers().back, pattern=r"cancel_send_message")],

    },

    fallbacks=[CallbackQueryHandler(callback=SendMessageToUsers().back, pattern=r"cancel_send_message"),
               CommandHandler('cancel', SendMessageToUsers().error),
               MessageHandler(filters=Filters.command, callback=SendMessageToUsers().error)]
)

SEE_MESSAGES_HANDLER = CallbackQueryHandler(pattern="inbox_message", callback=SeeMessageToAdmin().see_messages)


__mod_name__ = "Send a message"
__visitor_help__ = """
Here you can send a message to the chatbot owner

"""


__visitor_keyboard__ = [InlineKeyboardButton(text="Send message", callback_data="send_message_to_admin")]


__admin_help__ = """
Messages sent by the users to you
"""


__admin_keyboard__ = [
    InlineKeyboardButton(text="Send message", callback_data="send_message_to_users"),
    InlineKeyboardButton(text="Inbox messages", callback_data="inbox_message"),
]