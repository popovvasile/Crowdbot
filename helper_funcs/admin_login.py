#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, MessageHandler, Filters, RegexHandler, \
    CallbackQueryHandler

from database import users_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.helper import get_help

TYPING_PASS = 1


class AdminAuthentication(object):

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

    def handle_password(self, bot, update, user_data):
        print("Message: " + str(update.message))
        user_id = update.message.from_user.id
        chat_id, txt = initiate_chat_id(update)
        used_password = txt
        used_email = user_data["email"]
        user = users_table.find_one({'bot_id': bot.id, "email": used_email})
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_back")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        if "superuser" in user:
            superuser = user["superuser"]
        else:
            superuser = False
        if used_password == user["password"]:
            bot.send_message(chat_id, update.message.chat.first_name + string_dict(bot)["you_have_been_reg"])
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
            get_help(bot, update)

            return ConversationHandler.END
        elif used_password is None:

            bot.send_message(chat_id, string_dict(bot)["no_pass_provided"],
                             reply_markup=reply_markup)
            return TYPING_PASS

        else:
            bot.send_message(chat_id, string_dict(bot)["wrong_pass_admin"],
                             reply_markup=reply_markup)
            return TYPING_PASS

    def cancel(self, bot, update):
        get_help(bot, update)
        update.message.reply_text("Until next time!")
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END


ADMIN_AUTHENTICATION_HANDLER = ConversationHandler(
    entry_points=[
        RegexHandler(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$",
                     AdminAuthentication().handle_email, pass_user_data=True),
    ],

    states={
        TYPING_PASS: [MessageHandler(Filters.text,
                                     AdminAuthentication().handle_password,
                                     pass_user_data=True)],
    },

    fallbacks=[
        CallbackQueryHandler(callback=AdminAuthentication().back, pattern=r"help_back"),
    ]
)
