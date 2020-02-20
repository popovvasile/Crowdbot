#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime

from bson import ObjectId
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler, CallbackQueryHandler)

from database import products_table, chatbots_table, orders_table


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class PurchaseBot(object):

    def start_purchase(self, update, context):
        button_callback_data = update.callback_query.data

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id, )
        product_id = ObjectId(button_callback_data.replace(
            "online_buy/", ""))
        purchase_request = products_table.find_one({"_id": product_id})

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        # TODO when creating products, double check if payment token has been added
        context.bot.send_message(update.callback_query.message.chat.id, "Pay:{} {}".format(
            str(purchase_request["price"]), str(shop["currency"])))
        title = purchase_request['name']
        description = purchase_request['description']
        payload = "Purchase"
        start_parameter = "shop-payment"  # TODO change in production
        currency = shop['currency']
        prices = [LabeledPrice(title, int(float(purchase_request["price"]) * 100))]
        context.bot.sendInvoice(update.callback_query.message.chat_id, title, description, payload,
                                shop["payment_token"], start_parameter, currency, prices,
                                need_name=True, need_phone_number=True,
                                need_email=True, need_shipping_address=True,
                                is_flexible=True
                                )
        context.bot.send_message(update.callback_query.message.chat.id,
                                 text=context.bot.lang_dict["back_text"],
                                 reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                            callback_data="help_back")]]))
        logger.info("User {} on bot {} requested a purchase".format(
            update.effective_user.first_name, context.bot.first_name))

        return ConversationHandler.END

    def precheckout_callback(self, update, context):
        # query = update.callback_query
        # if query:
        #     if query.data == "help_back":
        #         return ConversationHandler.END
        query = update.pre_checkout_query

        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
        return ConversationHandler.END

    # finally, after contacting to the purchase provider...
    def successful_payment_callback(self, update, context):
        # TODO add counting of purchases and prepare for callback_query
        # do something after successful receive of purchase?
        buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="help_back")]]
        # TODO add a back function with deleting of old message
        markup = InlineKeyboardMarkup(buttons)
        context.user_data = dict()
        context.user_data["status"] = "Paid"
        context.user_data['timestamp_paid'] = datetime.datetime.now()
        context.user_data["amount"] = update.message.successful_payment.total_amount
        # context.user_data["currency"]
        context.user_data["chat_id"] = update.message.chat_id
        context.user_data["bot_id"] = context.bot.id
        # order_info
        orders_table.insert_one(context.user_data)
        update.message.reply_text(context.bot.lang_dict["thank_purchase"], markup=markup)
        context.user_data.clear()
        return ConversationHandler.END


ONLINE_PURCHASE_HANDLER = CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                               pattern=r'online_buy')

HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(
    PurchaseBot().precheckout_callback)  # TODO make different for donations and shop

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               PurchaseBot().successful_payment_callback)
