#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bson import ObjectId
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler, CallbackQueryHandler)
import logging
import datetime
# Enable logging
from database import products_table, chatbots_table, orders_table

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
ORDER_DESCRIPTION = 1


class PurchaseBot(object):

    def start_purchase(self, update, context):
        button_callback_data = update.callback_query.data

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id, )
        product_id = ObjectId(button_callback_data.replace(
                                                        "buy/", ""))
        purchase_request = products_table.find_one({"_id": product_id})

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
             # TODO when creating products, double check if payment token has been added
        context.bot.send_message(update.callback_query.message.chat.id, "Pay:{} {}".format(
            str(purchase_request["price"]), str(shop["currency"])))
PURCHASE_HANDLER = CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                        pattern=r'buy')