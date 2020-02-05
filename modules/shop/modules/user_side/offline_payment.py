#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bson import ObjectId
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
import logging
import datetime
# Enable logging
from database import products_table, chatbots_table, orders_table
from helper_funcs.helper import get_help
from helper_funcs.misc import delete_messages
from modules.shop.modules.user_side.products import Cart


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)
ORDER_DESCRIPTION, ORDER_CONTACTS, ORDER_ADDRESS, ORDER_FINISH = range(4)


class PurchaseBot(object):
    @staticmethod
    def start_purchase(update, context):
        delete_messages(update, context, True)
        if not context.user_data.get("order"):
            return Cart().back_to_cart(update, context)
        # button_callback_data = update.callback_query.data
        # context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
        #                            message_id=update.callback_query.message.message_id, )
        # product_id = ObjectId(button_callback_data.replace("offline_buy/", ""))

        # product = products_table.find_one({"_id": product_id})
        # context.user_data["product"] = product
        # shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat.id,
                text="Pay:{} {}".format(
                    str(context.user_data["order"]["total_price"]),
                    str(context.user_data["order"]["currency"]))))
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat.id,
                text="Add some details to your order",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="back_to_cart")]])))
        return ORDER_CONTACTS

    @staticmethod
    def ask_contacts(update, context):
        delete_messages(update, context, True)
        if not context.user_data.get("order"):
            return Cart().back_to_cart(update, context)
        context.user_data["order"]["description"] = update.message.text
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.message.chat.id,
                text="Tell us your email or phone number",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="back_to_cart")]])))
        # TODO !!
        # if context.user_data["product"]["physical"]:
        #     return ORDER_ADDRESS
        # else:
        #     return ORDER_FINISH
        return ORDER_ADDRESS

    @staticmethod
    def ask_address(update, context):
        delete_messages(update, context, True)
        if not context.user_data.get("order"):
            return Cart().back_to_cart(update, context)
        
        context.user_data["order"]["contacts"] = update.message.text
        context.user_data["customers contacts"]
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.message.chat.id,
                text="Tell us your full address",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="back_to_cart")]])))
        return ORDER_FINISH

    @staticmethod
    def order_finish(update, context):
        delete_messages(update, context, True)
        if "contacts" not in context.user_data:
            context.user_data["order"]["contacts"] = update.message.text
        else:
            context.user_data["order"]["address"] = update.message.text

        orders_table.insert_one({"status": "Pending",  # TODO ask about the status
                                 "bot_id": context.bot.id,
                                 "user_id": update.effective_user.id,
                                 "timestamp": datetime.datetime.now(),
                                 "name": update.effective_user.name,
                                 "in_trash": False,
                                 # "product_id": context.user_data.get("product_id"),
                                 # "description": context.user_data.get("description"),
                                 # "contacts": context.user_data.get("contacts"),
                                 # "address": context.user_data.get("address"),
                                 })
        context.bot.send_message(
            chat_id=update.message.chat.id,
            text="Thank you!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["back_button"],
                    callback_data="back_to_cart")]]))
        return ConversationHandler.END


OFFLINE_PURCHASE_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                       pattern=r'offline_buy')],
    states={
        ORDER_ADDRESS: [MessageHandler(Filters.text,
                                       callback=PurchaseBot().ask_address)],
        ORDER_CONTACTS: [MessageHandler(Filters.text,
                                        callback=PurchaseBot().ask_contacts)],
        ORDER_FINISH: [MessageHandler(Filters.text,
                                      callback=PurchaseBot().order_finish)],


    },
    fallbacks=[CallbackQueryHandler(Cart().back_to_cart,
                                    pattern="back_to_cart")]
)
