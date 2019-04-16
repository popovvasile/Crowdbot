#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters, RegexHandler
from telegram.ext.dispatcher import run_async

from database import users_table
from modules.helper_funcs.auth import initiate_chat_id

TYPING_PASS = 1


class AdminAuthentication(object):
    @run_async
    def handle_email(self, bot, update, user_data):
        print("Message: " + str(update.message))
        chat_id, txt = initiate_chat_id(update)
        used_email = txt
        user = users_table.find_one({'bot_id': bot.id, "email": used_email})
        if user:
            bot.send_message(chat_id, "Enter your password or click /cancel")
            user_data["email"] = used_email
            return TYPING_PASS
        else:
            bot.send_message(chat_id,
                             "This email is not listed in the list of users.")
            return ConversationHandler.END

    @run_async
    def handle_password(self, bot, update, user_data):
        print("Message: " + str(update.message))
        user_id = update.message.from_user.id
        chat_id, txt = initiate_chat_id(update)
        used_password = txt
        used_email = user_data["email"]
        user = users_table.find_one({'bot_id': bot.id, "email": used_email})
        if "superuser" in user:
            superuser = user["superuser"]
        else:
            superuser = False
        if used_password == user["password"]:
            if user["is_admin"]:
                bot.send_message(chat_id, update.message.chat.first_name + ", you have been registered " +
                                 "as an authorized user of this bot.")
                users_table.replace_one({"user_id": user_id},
                                        {'bot_id': bot.id,
                                         "chat_id": chat_id,
                                         "user_id": user_id,
                                         "username": update.message.from_user.username,
                                         "full_name": update.message.from_user.full_name,
                                         'registered': True,
                                         "is_admin": True,
                                         "superuser": superuser,
                                         "tags": ["#all", "#user", "#admin"]
                                         })
            else:
                bot.send_message(chat_id, update.message.chat.first_name + ", you have been registered " +
                                 "as an authorized user of this bot.")
                users_table.replace_one({"user_id": user_id},
                                        {'bot_id': bot.id,
                                         "chat_id": chat_id,
                                         "user_id": user_id,
                                         "username": update.message.from_user.username,
                                         "full_name": update.message.from_user.full_name,
                                         'registered': True,
                                         "is_admin": False,
                                         "superuser": superuser,
                                         "tags": ["#all", "#user"]
                                         })
            return ConversationHandler.END
        elif used_password is None:
            bot.send_message(chat_id, "No password provided. Please send a  valid password or click /cancel")
            return TYPING_PASS

        else:
            bot.send_message(chat_id, "Wrong password. Please send a  valid password or click /cancel")
            return TYPING_PASS

    @run_async
    def cancel(self, bot, update):
        update.message.reply_text("Until next time!")
        return ConversationHandler.END


ADMIN_AUTHENTICATION_HANDLER = ConversationHandler(
    entry_points=[RegexHandler(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$", AdminAuthentication().handle_email, pass_user_data=True)],

    states={
        TYPING_PASS: [MessageHandler(Filters.text,
                                     AdminAuthentication().handle_password,
                                     pass_user_data=True)],
    },

    fallbacks=[CommandHandler('cancel', AdminAuthentication().cancel),
               MessageHandler(filters=Filters.command, callback=AdminAuthentication().cancel)]
)