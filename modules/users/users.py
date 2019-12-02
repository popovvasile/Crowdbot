# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
# import random
from haikunator import Haikunator
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from database import users_table, donations_table
from helper_funcs.helper import get_help
from helper_funcs.pagination import Pagination, set_page_key
from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.misc import delete_messages, back_button, back_reply
from bson.objectid import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timedelta, time


# May raise Exception and bson.errors.InvalidId
def get_obj(table, obj: (ObjectId, dict, str)):
    if type(obj) is dict:
        return obj
    elif type(obj) is ObjectId:
        return table.find_one({"_id": obj})
    elif type(obj) is str:
        return table.find_one({"_id": ObjectId(obj)})
    else:
        raise Exception


def users_menu(update, context):
    string_d_str = string_dict(context.bot)
    # bot.delete_message(chat_id=update.callback_query.message.chat_id,
    #                    message_id=update.callback_query.message.message_id)
    delete_messages(update, context)
    users_menu_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=string_d_str["statistic_btn_str"],
                              callback_data="users_statistic"),
         InlineKeyboardButton(text=string_d_str["users_list_btn_str"],
                              callback_data="users_layout")],
        [InlineKeyboardButton(text=string_d_str["admins_btn_str"],
                              callback_data="admins"),
         InlineKeyboardButton(text=string_d_str["add_admin_btn_str"],
                              callback_data="start_add_admins")],
        [back_button(context, "help_module(users)")]
    ])
    context.bot.send_message(update.callback_query.message.chat.id,
                             string_dict(context.bot)["users_menu_str"],
                             reply_markup=users_menu_keyboard)
    return ConversationHandler.END


def back_to_users_menu(update, context):
    delete_messages(update, context)
    context.user_data.clear()
    return users_menu(update, context)


# список донатов
# todo last seen for users
class User(object):
    def __init__(self, obj: (ObjectId, dict, str)):
        obj = get_obj(users_table, obj)
        self.mention_markdown = obj["mention_markdown"]
        # https://dateparser.readthedocs.io/en/latest/
        self.timestamp = obj["timestamp"].strftime("%d, %b %Y, %H:%M")

    def template(self, bot):
        return string_dict(bot)["user_temp"].format(
            self.mention_markdown, self.timestamp)

    def send_template(self, update, context):
        context.user_data["to_delete"].append(
            context.bot.send_message(update.effective_chat.id,
                                     self.template(context.bot),
                                     parse_mode=ParseMode.MARKDOWN))

    def donates(self):
        return

    def donates_to_string(self):
        pass


class UsersHandler(object):
    def users(self, update, context):
        delete_messages(update, context)
        set_page_key(update, context, "users_layout")
        self.send_users_layout(update, context)
        return USERS

    def send_users_layout(self, update, context):
        all_users = users_table.find({"bot_id": context.bot.id,
                                      "is_admin": False}).sort([["_id", -1]])
        per_page = 5
        context.user_data['to_delete'].append(
            context.bot.send_message(
                update.callback_query.message.chat_id,
                string_dict(context.bot)["users_layout_title"].format(
                    all_users.count()),
                ParseMode.MARKDOWN))
        if all_users.count() == 0:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    string_dict(context.bot)["no_users_str"],
                    reply_markup=back_reply(context, "back_to_users_menu")))
        else:
            pagination = Pagination(context, per_page, all_users)
            for user in pagination.page_content():
                User(user).send_template(update, context)
            pagination.send_keyboard(
                update, [[back_button(context, "back_to_users_menu")]])


class UsersStatistic(object):
    def show_statistic(self, update, context):
        context.bot.delete_message(update.callback_query.message.chat_id,
                                   update.callback_query.message.message_id)
        today = datetime.combine(datetime.today(), time.min)
        today_str = str(today).split(' ')[0]
        week_ago_date = today - timedelta(days=7)
        month_ago_date = today - timedelta(days=30)

        # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-8.php
        all_users = users_table.find({"bot_id": context.bot.id,
                                      "is_admin": False})
        daily_users = users_table.find({"bot_id": context.bot.id,
                                        "is_admin": False,
                                        "timestamp": {"$gt": today}})
        week_users = users_table.find({"bot_id": context.bot.id,
                                       "is_admin": False,
                                       "timestamp": {"$gt": week_ago_date}})
        month_users = users_table.find({"bot_id": context.bot.id,
                                        "is_admin": False,
                                        "timestamp": {"$gt": month_ago_date}})

        context.bot.send_message(
            update.effective_chat.id,
            string_dict(context)["users_statistic_template"].format(
                today_str,
                daily_users.count(),
                f"`{str(week_ago_date).split(' ')[0]}:{today_str}`",
                week_users.count(),
                f"`{str(month_ago_date).split(' ')[0]}:{today_str}`",
                month_users.count(),
                all_users.count()),
            reply_markup=back_reply(context, "help_module(users)"),
            parse_mode=ParseMode.MARKDOWN)
        # return USERS_STATISTIC
        return ConversationHandler.END


USERS = range(1)
# USERS_STATISTIC = range(1)


USERS_MENU = CallbackQueryHandler(pattern="users_list",
                                  callback=users_menu)


USERS_LIST_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="users_layout",
                                       callback=UsersHandler().users)],

    states={
        USERS: [CallbackQueryHandler(pattern="^[0-9]+$",
                                     callback=UsersHandler().users)]
    },

    fallbacks=[
        CallbackQueryHandler(pattern=r"back_to_users_menu",
                             callback=back_to_users_menu),
        # CallbackQueryHandler(pattern=r"help_back",
        #                      callback=UsersHandler(),
        #                      pass_user_data=True),
    ]
)

USERS_STATISTIC_HANDLER = \
    CallbackQueryHandler(pattern=r"users_statistic",
                         callback=UsersStatistic().show_statistic)
