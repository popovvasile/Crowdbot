# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from database import user_categories_table, users_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict

# TODO category question + send message for category

TOPIC = 1
MESSAGE_TO_USERS = 2


class AddUsersCategory(object):

    def add_category(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(users)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["send_user_category_14"], reply_markup=reply_markup)

        return TOPIC

    def add_category_finish(self, bot, update):
        # TODO make it continues- add more than one category +
        #  ask if he wants to send teh message to teh users about that
        user_categories_table.update({"category": update.message.text},
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


class UsersCategory(object):

    def show_category(self, bot, update):
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_module(users)"),
                    InlineKeyboardButton(text=string_dict(bot)["add_user_category"],
                                         callback_data="add_user_category"),
                    ]]
        reply_markup = InlineKeyboardMarkup(
            buttons)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        categories = user_categories_table.find()
        for category in categories:
            delete_buttons = [[InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                    callback_data="delete_user_category_{}"
                                                    .format(category["category"]))]]
            delete_markup = InlineKeyboardMarkup(
                delete_buttons)
            bot.send_message(update.callback_query.message.chat.id, category["category"],
                             reply_markup=delete_markup)
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["send_user_category_16"], reply_markup=reply_markup)
        return ConversationHandler.END


class DeleteUsersCategory(object):

    def delete_category(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_module(users)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        user_categories_table.delete_one({"category": update.callback_query.data.replace("delete_user_category_", "")})

        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["send_user_category_17"], reply_markup=reply_markup)

        return ConversationHandler.END


class UsersChooseCategory(object):

    def choose_category(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_module(users)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        new_category = update.callback_query.data.replace("user_chooses_category_", "").split("__")
        user_data = users_table.find_one({"user_id": update.callback_query.from_user.id})
        if "categories" not in user_data:
            user_data["categories"] = []
        if new_category not in user_data["categories"]:
            user_data["categories"].append(new_category)
        users_table.update_one(
            {"user_id": update.callback_query.from_user.id},
            {"$set": user_data}
        )

        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["user_chooses_category"], reply_markup=reply_markup)

        return ConversationHandler.END


class SendQuestionToUsers(object):

    def send_question(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        chats = users_table.find({"bot_id": bot.id})
        categories = user_categories_table.find()
        if categories.count() > 0:
            print(categories)
            buttons = list()
            for category in categories:
                buttons.append([InlineKeyboardButton(text=category["category"],
                                                     callback_data="user_chooses_category_{}".format(
                                                         category["category"],
                                                     )
                                                     )])
            choose_markup = InlineKeyboardMarkup(
                buttons)
            for chat in chats:
                print(chat["chat_id"])
                # if chat["chat_id"] != update.callback_query.message.chat.id:
                if update.callback_query.message.text:
                    bot.send_message(chat["chat_id"],
                                     string_dict(bot)["send_category_question_3"],
                                     reply_markup=choose_markup)
            buttons = list()
            buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                 callback_data="help_module(users)")])
            reply_markup = InlineKeyboardMarkup(buttons)
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["send_category_question_4"], reply_markup=reply_markup)
        else:
            buttons = list()
            buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                 callback_data="help_module(users)")])
            reply_markup = InlineKeyboardMarkup(buttons)
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["send_category_question_5"], reply_markup=reply_markup)
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END


USER_CATEGORY_HANDLER = CallbackQueryHandler(pattern="show_user_categories",
                                             callback=UsersCategory().show_category)
DELETE_USER_CATEGORY_HANDLER = CallbackQueryHandler(pattern="delete_user_category_",
                                                    callback=DeleteUsersCategory().delete_category)
USER_CHOOSES_CATEGORY_HANDLER = CallbackQueryHandler(pattern="user_chooses_category_",
                                                     callback=UsersChooseCategory().choose_category)
ADD_USER_CATEGORY_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="add_user_category",
                                       callback=AddUsersCategory().add_category)],

    states={
        TOPIC: [MessageHandler(Filters.all, AddUsersCategory().add_category_finish)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=AddUsersCategory().back,
                             pattern=r"help_module"),
    ]
)
SEND_USER_QUESTION_HANDLER = CallbackQueryHandler(pattern="send_user_category_question",
                                                  callback=SendQuestionToUsers().send_question)