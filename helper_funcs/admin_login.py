#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, MessageHandler, Filters, RegexHandler, \
    CallbackQueryHandler

from database import users_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.helper import get_help
from datetime import datetime

TYPING_PASS = 1


class AdminAuthentication(object):
    def handle_email(self, update, context):
        print("Message: " + str(update.message))
        chat_id, txt = initiate_chat_id(update)
        used_email = txt

        user = users_table.find_one({'bot_id': context.bot.id, "email": used_email})
        if user:
            context.bot.send_message(chat_id, "Enter your password or click /cancel")
            context.user_data["email"] = used_email
            return TYPING_PASS
        else:
            context.bot.send_message(chat_id,
                                     "This email is not listed in the list of users.")
            return ConversationHandler.END

    def handle_password(self, update, context):
        print("Message: " + str(update.message))
        user_id = update.message.from_user.id
        chat_id, txt = initiate_chat_id(update)
        used_password = txt
        used_email = context.user_data["email"]
        user = users_table.find_one({'bot_id': context.bot.id, "email": used_email})
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(context)["back_button"],
                                             callback_data="help_back")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        # todo but superuser can't be in user variable- coz superuser don't have "email" key
        superuser = user.get("superuser") or False
        # if "superuser" in user:
        #     superuser = user["superuser"]
        # else:
        #     superuser = False
        if used_password == user["password"]:
            context.bot.send_message(chat_id, update.message.chat.first_name + string_dict(context)["you_have_been_reg"])
            users_table.replace_one({"user_id": user_id,
                                     "bot_id": context.bot.id},
                                    {'bot_id': context.bot.id,
                                     "chat_id": chat_id,
                                     "user_id": user_id,
                                     "email": used_email,
                                     "username": update.message.from_user.username,
                                     "full_name": update.message.from_user.full_name,
                                     "mention_markdown": update.effective_user.mention_markdown(),
                                     "mention_html": update.effective_user.mention_html(),
                                     "timestamp": datetime.now(),
                                     'registered': True,
                                     "is_admin": True,
                                     "superuser": superuser,
                                     "tags": ["#all", "#user", "#admin"]})
            get_help(update, context)
            return ConversationHandler.END

        elif used_password is None:
            context.bot.send_message(chat_id, string_dict(context)["no_pass_provided"],
                                     reply_markup=reply_markup)
            return TYPING_PASS

        else:
            context.bot.send_message(chat_id, string_dict(context)["wrong_pass_admin"],
                                     reply_markup=reply_markup)
            return TYPING_PASS

    def cancel(self, update, context):
        get_help(update, context)
        update.message.reply_text("Until next time!")
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        get_help(update, context)
        return ConversationHandler.END


ADMIN_AUTHENTICATION_HANDLER = ConversationHandler(
    entry_points=[
        MessageHandler(Filters.regex(r"^\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$"),
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
