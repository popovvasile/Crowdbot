#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
from database import chatbots_table
from helper_funcs.helper import get_help


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1
MESSAGE_TO_USERS = 1


class ChangeBotLanguage(object):

    def send_message(self, update, context):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(settings)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        context.bot.send_message(update.callback_query.message.chat.id,
                         context.bot.lang_dict["edit_button_str_1"], reply_markup=reply_markup)  # TODO
        return MESSAGE

    def received_message(self, update, context):
        context.bot.send_message(update.message.chat_id,
                         context.bot.lang_dict["edit_button_str_2"])

        old_bot = chatbots_table.find_one({"bot_id": context.bot.id})
        old_bot['lang'] = update.message.text
        chatbots_table.update_one({"bot_id": context.bot.id}, {"$set": old_bot})
        get_help(update, context)
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(update, context)
        return ConversationHandler.END


class EditBotDescription(object):

    def send_message(self, update, context):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(settings)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        context.bot.send_message(update.callback_query.message.chat.id,
                         context.bot.lang_dict["edit_button_str_1"], reply_markup=reply_markup)
        return MESSAGE

    def received_message(self, update, context):
        context.bot.send_message(update.message.chat_id,
                         context.bot.lang_dict["edit_button_str_2"])

        old_bot = chatbots_table.find_one({"bot_id": context.bot.id})
        old_bot['welcomeMessage'] = update.message.text
        chatbots_table.update_one({"bot_id": context.bot.id}, {"$set": old_bot})
        get_help(update, context)
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(update, context)
        return ConversationHandler.END


EDIT_BOT_DESCRIPTION_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="edit_bot_description",
                                       callback=EditBotDescription().send_message)],

    states={
        MESSAGE: [MessageHandler(Filters.all, EditBotDescription().received_message)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=EditBotDescription().back,
                             pattern=r"help_module"),
    ]
)

CHANGE_BOT_LANGUAGE_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="change_bot_language",
                                       callback=EditBotDescription().send_message)],

    states={
        MESSAGE: [MessageHandler(Filters.all, EditBotDescription().received_message)],
    },

    fallbacks=[
        CallbackQueryHandler(callback=EditBotDescription().back,
                             pattern=r"help_module"),
    ]
)