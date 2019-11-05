# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from database import user_categories_table, users_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict


USERS = 1
MESSAGE_TO_USERS = 2


class BlockUnblockUsers(object):

    def see_users(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(users)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["send_user_category_14"], reply_markup=reply_markup)

        return USERS

    def choose_user(self, bot, update):

        users_table.update({"category": update.message.text},
                                     {"$set": {"category": update.message.text}},
                                     upsert=True)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(users)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.message.chat.id,
                         string_dict(bot)["send_user_category_15"],
                         reply_markup=reply_markup)
        return ConversationHandler.END

    def block_user(self, bot, update):
        users_table.update({"category": update.message.text},
                           {"$set": {"category": update.message.text}},
                           upsert=True)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(users)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.message.chat.id,
                         string_dict(bot)["send_user_category_15"],
                         reply_markup=reply_markup)
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

#
# SEND_USER_QUESTION_HANDLER = CallbackQueryHandler(pattern="send_user_category_question",
#                                                   callback=SendQuestionToUsers().send_question)