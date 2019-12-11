# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from database import (users_table, donations_table, chatbots_table,
                      channels_table)
from helper_funcs.helper import get_help
from helper_funcs.pagination import Pagination, set_page_key
from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.misc import (delete_messages, back_button, back_reply,
                               lang_timestamp, get_obj)
from bson.objectid import ObjectId
from datetime import datetime, timedelta, time
from modules.donations.donation_statistic import DonationStatistic


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def users_menu(update, context):
    string_d_str = string_dict(context.bot)
    delete_messages(update, context, True)
    users_menu_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=string_d_str["statistic_btn_str"],
                              callback_data="users_statistic"),
         InlineKeyboardButton(text=string_d_str["users_list_btn_str"],
                              callback_data="users_layout")],
        [back_button(context, "help_module(users)")]
    ])
    context.bot.send_message(update.callback_query.message.chat.id,
                             string_dict(context.bot)["users_menu_str"],
                             reply_markup=users_menu_keyboard)
    return ConversationHandler.END


def back_to_users_menu(update, context):
    delete_messages(update, context, True)
    context.user_data.clear()
    return users_menu(update, context)


def time_statistic():
    pass


# todo last seen for users
class User(object):
    def __init__(self, context, obj: (ObjectId, dict, str)):
        self.context = context
        user_obj = get_obj(users_table, obj)
        self.user_id = user_obj["user_id"]
        self.mention_markdown = user_obj["mention_markdown"]
        self.timestamp = lang_timestamp(context, user_obj["timestamp"])

    def send_template(self, update):
        self.context.user_data["to_delete"].append(
            self.context.bot.send_message(update.effective_chat.id,
                                          f"{self.template}"
                                          f"\n{self.donates_to_string}",
                                          parse_mode=ParseMode.MARKDOWN))

    @property
    def template(self):
        return string_dict(self.context)["user_temp"].format(
            self.mention_markdown, self.timestamp)

    @property
    def donates(self):
        return donations_table.find({"bot_id": self.context.bot.id,
                                     "user_id": self.user_id})

    @property
    def donates_to_string(self):
        donates = self.donates
        return string_dict(self.context)["donations_count_str"].format(
            DonationStatistic().create_amount(donates)) if donates.count() else ""

    @staticmethod
    def statistic(context):
        bot_lang = chatbots_table.find_one({"bot_id": context.bot.id})["lang"]
        today_date = datetime.combine(datetime.today(), time.min)
        week_ago_date = today_date - timedelta(days=7)
        month_ago_date = today_date - timedelta(days=30)

        # https://www.w3resource.com/python-exercises/date-time-exercise/python-date-time-exercise-8.php
        all_users = users_table.find({"bot_id": context.bot.id,
                                      "is_admin": False}).sort([["_id", -1]])
        all_users_count = all_users.count()
        daily_users = users_table.find({"bot_id": context.bot.id,
                                        "is_admin": False,
                                        "timestamp": {"$gt": today_date}})
        week_users = users_table.find({"bot_id": context.bot.id,
                                       "is_admin": False,
                                       "timestamp": {"$gt": week_ago_date}})
        month_users = users_table.find({"bot_id": context.bot.id,
                                        "is_admin": False,
                                        "timestamp": {"$gt": month_ago_date}})

        today_str = lang_timestamp(bot_lang, today_date, "d MMM yyyy")
        return {
            "quantity": {
                "day": {"time_strings": today_str,
                        "count": daily_users.count()},

                "week": {"time_strings":
                         (lang_timestamp(bot_lang, week_ago_date, "d MMM yyyy"),
                          today_str),
                         "count": week_users.count()},

                "month": {"time_strings":
                          (lang_timestamp(bot_lang, month_ago_date, "d MMM yyyy"),
                           today_str),
                          "count": month_users.count()},

                "all": {"time_strings":
                        (lang_timestamp(bot_lang, all_users[all_users_count-1]['timestamp']),
                         lang_timestamp(bot_lang, all_users[0]['timestamp']))
                        if all_users_count else (0, 0),
                        "count": all_users_count}}}


class UsersHandler(object):
    def users(self, update, context):
        delete_messages(update, context, True)
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
                User(context, user).send_template(update)
            pagination.send_keyboard(
                update, [[back_button(context, "back_to_users_menu")]])


class UsersStatistic(object):
    def show_statistic(self, update, context):
        context.bot.delete_message(update.callback_query.message.chat_id,
                                   update.callback_query.message.message_id)
        user_statistic = User.statistic(context)
        context.bot.send_message(
            update.effective_chat.id,
            string_dict(context)["users_statistic_template"].format(
                user_statistic["quantity"]["day"]["time_strings"],
                user_statistic["quantity"]["day"]["count"],

                user_statistic["quantity"]["week"]["time_strings"][0],
                user_statistic["quantity"]["week"]["time_strings"][1],
                user_statistic["quantity"]["week"]["count"],

                user_statistic["quantity"]["month"]["time_strings"][0],
                user_statistic["quantity"]["month"]["time_strings"][1],
                user_statistic["quantity"]["month"]["count"],

                user_statistic["quantity"]["all"]["time_strings"][0],
                user_statistic["quantity"]["all"]["time_strings"][1],
                user_statistic["quantity"]["all"]["count"]),
            reply_markup=back_reply(context, "help_module(users)"),
            parse_mode=ParseMode.MARKDOWN),
        # CHANNELS STATISTIC
        if channels_table.find({"bot_id": context.bot.id}):
            pass
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
