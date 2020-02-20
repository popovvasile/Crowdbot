#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
from pprint import pprint
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from database import (orders_table, chatbots_table,
                      shop_customers_contacts_table)
from helper_funcs.misc import delete_messages
from modules.shop.modules.user_side.products import Cart


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


ORDER_DESCRIPTION, ORDER_CONTACTS, ORDER_ADDRESS, CONFIRM_ORDER, \
    ORDER_FINISH = range(5)


class PurchaseBot(object):
    @staticmethod
    def start_purchase(update, context):
        delete_messages(update, context, True)
        if not context.user_data.get("order"):
            return Cart().back_to_cart(update, context)

        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat.id,
                text="Pay:{} {}".format(
                    str(context.user_data["order"]["total_price"]),
                    str(context.user_data["order"]["currency"]))))
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat.id,
                text="Add some details to your order or continue",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                         text=context.bot.lang_dict["back_button"],
                         callback_data="back_to_cart"),
                     InlineKeyboardButton(
                         text="Continue",
                         callback_data="pass_order_comment")]])))
        return ORDER_CONTACTS

    @staticmethod
    def ask_contacts(update, context):
        delete_messages(update, context, True)
        if not context.user_data.get("order"):
            return Cart().back_to_cart(update, context)
        if update.callback_query:
            context.user_data["order"]["description"] = ""
        else:
            context.user_data["order"]["description"] = update.message.text

        context.user_data["contacts"] = (
            shop_customers_contacts_table.find_one(
                {"bot_id": context.bot.id,
                 "user_id": update.effective_user.id}))

        if (context.user_data["contacts"]
                and len(context.user_data["contacts"]["phone_numbers"])):
            text = "Tell us your phone number or select one of with this:"
            buttons = [
                [InlineKeyboardButton(text=x,
                                      callback_data=f"phone_number/{x}")]
                for x in context.user_data["contacts"]["phone_numbers"]]
        else:
            text = "Tell us your phone number:"
            buttons = []

        buttons.append([InlineKeyboardButton(
                            text=context.bot.lang_dict["back_button"],
                            callback_data="back_to_cart")])
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons)))
        return ORDER_ADDRESS

    @staticmethod
    def ask_address(update, context):
        delete_messages(update, context, True)
        if not context.user_data.get("order"):
            return Cart().back_to_cart(update, context)
        if update.callback_query:
            context.user_data["order"]["phone_number"] = (
                update.callback_query.data.split("/")[1])
        else:
            context.user_data["order"]["phone_number"] = update.message.text
            # set it to check in the next step if there are no shipping
            update.message.text = "phone"

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        if shop["shipping"]:
            if (context.user_data["contacts"]
                    and len(context.user_data["contacts"]["addresses"])):
                text = "Tell us your full address or select one of with this:"
                buttons = [
                    [InlineKeyboardButton(text=x,
                                          callback_data=f"address/{x}")]
                    for x in context.user_data["contacts"]["addresses"]]
            else:
                text = "Tell us your full address"
                buttons = []

            buttons.append([InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="back_to_cart")])

            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=InlineKeyboardMarkup(buttons)))
            return ORDER_FINISH
        else:
            return PurchaseBot.confirm_order(update, context)

    @staticmethod
    def confirm_order(update, context):
        delete_messages(update, context, True)
        if update.callback_query and "address" in update.callbackquery.data:
            context.user_data["order"]["address"] = (
                update.callbackquery.data.split("/")[1])
        if update.message and update.message.text != "phone":
            context.user_data["order"]["address"] = update.message.text
        else:
            context.user_data["order"]["address"] = ""
        pprint(context.user_data["order"])

    @staticmethod
    def order_finish(update, context):
        delete_messages(update, context, True)
        # if "contacts" not in context.user_data:
        #     context.user_data["order"]["contacts"] = update.message.text
        # else:
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
        ORDER_ADDRESS: [
            CallbackQueryHandler(pattern=r"phone_number",
                                 callback=PurchaseBot().ask_address),
            MessageHandler(Filters.text,
                           callback=PurchaseBot().ask_address)],

        ORDER_CONTACTS: [
            CallbackQueryHandler(pattern="pass_order_comment",
                                 callback=PurchaseBot().ask_contacts),
            MessageHandler(Filters.text,
                           callback=PurchaseBot().ask_contacts)],
        ORDER_FINISH: [
            CallbackQueryHandler(pattern=r"address",
                                 callback=PurchaseBot().confirm_order),
            MessageHandler(Filters.text,
                           callback=PurchaseBot().confirm_order)],


    },
    fallbacks=[CallbackQueryHandler(Cart().back_to_cart,
                                    pattern="back_to_cart")]
)
