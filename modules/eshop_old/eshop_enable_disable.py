# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import requests
import json

from telegram import LabeledPrice
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
import logging
from database import chatbots_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.helper import get_help
from helper_funcs.lang_strings.strings import string_dict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TYPING_TOKEN, TYPING_TITLE, TYPING_DESCRIPTION, SHOP_FINISH = range(4)


def check_provider_token(provider_token, update, context):
    bot_token = chatbots_table.find_one({"bot_id": context.bot.id})["token"]
    prices = [LabeledPrice(string_dict(context)["create_shop_str_1"], 10000)]
    data = requests.get("https://api.telegram.org/bot{}/sendInvoice".format(bot_token),
                        params=dict(title="TEST",
                                    description="A testing payment invoice to check the token",
                                    payload="test",
                                    provider_token=provider_token,
                                    currency="USD",
                                    start_parameter="test",
                                    prices=json.dumps([p.to_dict() for p in prices]),
                                    chat_id=update.effective_chat.id))
    if "description" in json.loads(data.content):
        if json.loads(data.content)["description"] == "Bad Request: CURRENCY_INVALID":
            data = requests.get("https://api.telegram.org/bot{}/sendInvoice".format(bot_token),
                                params=dict(title="TEST",
                                            description="A testing payment invoice to check the token",
                                            payload="test",
                                            provider_token=provider_token,
                                            currency="RUB",
                                            start_parameter="test",
                                            prices=json.dumps([p.to_dict() for p in prices]),
                                            chat_id=update.effective_chat.id))
    return json.loads(data.content)["ok"]


class CreateShopHandler(object):
    @staticmethod
    def facts_to_str(context):
        facts = list()

        for key, value in context.user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    def start_create_shop(self, update, context):
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=string_dict(context)["back_button"],
                                  callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        chatbot = chatbots_table.find_one({"bot_id": context.bot.id}) or {}
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        if "shop" in chatbot:
            if "payment_token" in chatbot["shop"]:
                context.bot.send_message(update.callback_query.message.chat.id,
                                         string_dict(context)["create_shop_str_2"], reply_markup=reply_markup)
                return TYPING_TITLE
            else:
                context.bot.send_message(update.callback_query.message.chat.id,
                                         string_dict(context)["create_shop_str_3"],
                                         reply_markup=reply_markup)
                return TYPING_TOKEN
        else:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     string_dict(context)["create_shop_str_3"],
                                     reply_markup=reply_markup)
            return TYPING_TOKEN

    def handle_token(self, update, context):
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=string_dict(context)["back_button"],
                                  callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        chat_id, txt = initiate_chat_id(update)
        if check_provider_token(provider_token=txt, update=update, context=context):

            context.user_data['payment_token'] = txt

            update.message.reply_text(string_dict(context)["create_shop_str_4"], reply_markup=reply_markup)

            return TYPING_TITLE
        else:
            update.message.reply_text(
                string_dict(context)["create_shop_str_5"],
                reply_markup=reply_markup)

        return TYPING_TOKEN

    def handle_title(self, update, context):
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=string_dict(context)["back_button"],
                                  callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        chat_id, txt = initiate_chat_id(update)
        context.user_data['title'] = txt

        update.message.reply_text(string_dict(context)["create_shop_str_6"],
                                  reply_markup=reply_markup)

        return TYPING_DESCRIPTION

    def handle_description(self, update, context):
        chat_id, txt = initiate_chat_id(update)
        context.user_data["description"] = txt
        currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
        update.message.reply_text(string_dict(context)["create_shop_str_7"],
                                  reply_markup=ReplyKeyboardMarkup(currency_keyboard, one_time_keyboard=True))

        return SHOP_FINISH

    def handle_shop_finish(self, update, context):

        create_buttons = [
            [InlineKeyboardButton(text=string_dict(context)["back_button"],
                                  callback_data="help_module(shop)")]]
        create_markup = InlineKeyboardMarkup(
            create_buttons)

        chat_id, txt = initiate_chat_id(update)
        currency = txt
        context.user_data["currency"] = currency

        context.bot.send_message(chat_id,
                                 string_dict(context)["create_shop_str_8"],
                                 reply_markup=create_markup)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id}) or {}

        context.user_data.pop("to_delete", None)
        if 'payment_token' not in context.user_data:
            # chatbot["shop"]["payment_token"] = user_data['payment_token']
            context.user_data["payment_token"] = chatbot["shop"]["payment_token"]
        chatbot["shop"] = context.user_data
        chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot}, upsert=True)

        logger.info("Admin {} on bot {}:{} added a shop config:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, context.user_data["title"]))
        context.user_data.clear()
        return ConversationHandler.END

    @staticmethod
    def error(update, context, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def cancel(self, update, context):

        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(update, context)
        return ConversationHandler.END

    def back(self, update, context):

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id, )
        get_help(update, context)
        return ConversationHandler.END


# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY'

CREATE_SHOP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=CreateShopHandler().start_create_shop,
                                       pass_user_data=True,
                                       pattern=r'allow_shop'),
                  ],
    # TYPING_TOKEN, TYPING_TITLE,  TYPING_DESCRIPTION, TYPING_AMOUNT, TYPING_CURRENCY,\
    # TYPING_TAGS, TYPING_TAGS_FINISH, TYPING_TYPE, TYPING_DEADLINE, TYPING_REPEAT
    states={
        TYPING_TOKEN: [MessageHandler(Filters.text,
                                      CreateShopHandler().handle_token,
                                      pass_user_data=True)],
        TYPING_TITLE: [MessageHandler(Filters.text,
                                      CreateShopHandler().handle_title,
                                      pass_user_data=True)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.text,
                                            CreateShopHandler().handle_description,
                                            pass_user_data=True)],
        SHOP_FINISH: [MessageHandler(Filters.text,
                                     CreateShopHandler().handle_shop_finish,
                                     pass_user_data=True)],
    },

    fallbacks=[CallbackQueryHandler(callback=CreateShopHandler().back, pattern=r"help_back"),
               CallbackQueryHandler(callback=CreateShopHandler().back, pattern=r"help_module"),
               MessageHandler(filters=Filters.command, callback=CreateShopHandler().back),
               ]
)
