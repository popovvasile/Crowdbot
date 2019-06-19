#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, Filters
from telegram.ext.dispatcher import run_async

from database import users_table
from modules.helper_funcs.auth import initiate_chat_id

TYPING_EMAIL, TYPING_PASS = range(2)


class UserAuthentication(object):
    
    def handle_addme_user(self, bot, update):
        print("Message: " + str(update.message))
        chat_id, txt = initiate_chat_id(update)
        bot.send_message(chat_id, update.message.chat.first_name + " please enter your email")
        return TYPING_EMAIL

    
    def handle_email(self, bot, update, user_data):
        print("Message: " + str(update.message))
        chat_id, txt = initiate_chat_id(update)
        used_email = txt
        user = users_table.find_one({'bot_id': bot.id, "email": used_email})
        if user:  # TODO double check
            bot.send_message(chat_id, "Please enter your password")
            user_data["email"] = used_email
            return TYPING_PASS
        else:
            bot.send_message(chat_id,
                             "This email is not listed in the list of users."
                             " Please enter a valid email or click /cancel")
            return TYPING_EMAIL

    
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

    
    def handle_rmme(self, bot, update):
        user_id = update.message.from_user.id
        chat_id = update.message.chat_id
        user = users_table.find_one({'bot_id': bot.id, "chat_id": chat_id})

        if user:
            users_table.delete_one(
                {"bot_id": bot.id, "user_id": user_id}
            )
            bot.send_message(chat_id, "Your permission for using the bot was removed successfully.")
        else:
            bot.send_message(chat_id, "You didn't have the permission to use this bot")

    
    def show_users(self, bot, update):  # TODO why no full_name is save?
        chat_id = update.message.chat_id
        users = users_table.find({'bot_id': bot.id})

        text_to_return = ''
        for user in users:
            text_to_return += 'Name: {}, email: {} \n'.format(user["full_name"], user['email'])
        bot.send_message(chat_id, "This is the full list on the users of this bot: \n" + text_to_return)

    
    def cancel(self, bot, update):
        update.message.reply_text("Until next time!")
        return ConversationHandler.END


USER_AUTHENTICATION_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('addme', UserAuthentication().handle_addme_user)],

    states={
        TYPING_EMAIL: [MessageHandler(Filters.text,
                                      UserAuthentication().handle_email,
                                      pass_user_data=True)],
        TYPING_PASS: [MessageHandler(Filters.text,
                                     UserAuthentication().handle_password,
                                     pass_user_data=True)],
    },

    fallbacks=[CommandHandler('cancel', UserAuthentication().cancel),
               MessageHandler(filters=Filters.command, callback=UserAuthentication().cancel)]
)
USER_REMOVE_HANDLER = CommandHandler("rmme", UserAuthentication().handle_rmme)
SHOW_USERS_HANDLER = CommandHandler("show_users", UserAuthentication().show_users)

__mod_name__ = "Login"

__admin_help__ = """
  -  /addme - get the user permissions
  -  /rmme - removes the user permissions 
  -  /show_users - shows all the users of the chatbot
"""

__user_help__ = """
  -  /rmme - removes your user permissions 
"""

__visitor_help__ = """
  -  /addme - get your user permissions
"""
__admin_keyboard__ = [["/addme", "/rmme", "/show_users"]]
__user_keyboard__ = [["/addme"]]
__visitor_keyboard__ = [["/addme"]]
