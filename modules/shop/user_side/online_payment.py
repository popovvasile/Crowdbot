#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
from pprint import pprint
from random import randint
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler, CallbackQueryHandler)

from database import products_table, chatbots_table, orders_table, shop_customers_contacts_table, carts_table, \
    users_table
from helper_funcs.misc import delete_messages
from modules.shop.components.order import UserOrder, AdminOrder
from modules.shop.user_side.cart import Cart

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class PurchaseBot(object):

    def start_purchase(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id, )

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        order = UserOrder(context, context.user_data["order"])
        context.bot.send_message(update.callback_query.message.chat.id, "Pay:{} {}".format(
            str(order.total_price),
            str(order.currency)))
        title = order.items_json[0]["product"]['name']
        description = order.items_json[0]["product"]['description']
        payload = "Purchase"
        start_parameter = "shop-payment"  # TODO change in production
        prices = [LabeledPrice(title, int(float(order.total_price) * 100))]
        context.bot.sendInvoice(update.callback_query.message.chat_id, title, description, payload,
                                shop["payment_token"], start_parameter, order.currency, prices,
                                need_name=True, need_phone_number=True,
                                need_email=True, need_shipping_address=shop["shipping"],
                                is_flexible=True
                                )
        context.bot.send_message(update.callback_query.message.chat.id,
                                 text=context.bot.lang_dict["back_text"],
                                 reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                            callback_data="back_to_cart")]]))
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

    # def successful_payment_callback(self, update, context):
    #     buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
    #                                      callback_data="back_to_cart")]]
    #     markup = InlineKeyboardMarkup(buttons)
    #     context.user_data = dict()
    #     context.user_data["status"] = "Paid"
    #     context.user_data['timestamp_paid'] = datetime.datetime.now()
    #     context.user_data["amount"] = update.message.successful_payment.total_amount
    #     # context.user_data["currency"]
    #     context.user_data["chat_id"] = update.message.chat_id
    #     context.user_data["bot_id"] = context.bot.id
    #     # order_info
    #     orders_table.insert_one(context.user_data)
    #     update.message.reply_text(context.bot.lang_dict["thank_purchase"], markup=markup)
    #     context.user_data.clear()
    #     return ConversationHandler.END
    @staticmethod
    def successful_payment_callback(update, context):
        delete_messages(update, context, True)
        order = UserOrder(context, context.user_data["order"])
        # Check products availability
        for item in order.items:
            if not item.item_exist:
                update.callback_query.answer(
                    context.bot.lang_dict["shop_product_not_available"],
                    show_alert=True)
                return Cart().back_to_cart(update, context)
        # Create order
        inserted_id = orders_table.insert_one(
            {**context.user_data["order"],
             **{"article": randint(10000, 99999),
                "status": False,
                "bot_id": context.bot.id,
                "user_id": update.effective_user.id,
                "creation_timestamp": datetime.datetime.now(),
                # "name": update.effective_user.name,
                "in_trash": False,
                # "is_canceled": False
                }}).inserted_id
        # Remove products from shop
        for item in order.items_json:
            new_fields = dict()
            product = products_table.find_one({"_id": item["product_id"]})
            if not product["unlimited"]:
                new_fields["quantity"] = product["quantity"] - item["quantity"]
                # if new_fields["quantity"] == 0:
                #     new_fields["sold"] = True
            if new_fields:
                products_table.update_one({"_id": item["product_id"]},
                                          {"$set": new_fields})
        # Save contacts
        all_addresses = context.user_data["used_contacts"].get(
            "addresses", list())
        all_numbers = context.user_data["used_contacts"].get(
            "phone_numbers", list())
        address = context.user_data["order"]["address"]
        number = context.user_data["order"]["phone_number"]
        if address and address not in all_addresses:
            if len(all_addresses) > 5:
                all_addresses.insert(0, address)
                del all_addresses[-1]
            else:
                all_addresses.append(address)
        if number not in all_numbers:
            if len(all_numbers) > 5:
                all_numbers.insert(0, number)
                del all_numbers[-1]
            else:
                all_numbers.append(number)
        shop_customers_contacts_table.update_one(
            {"bot_id": context.bot.id,
             "user_id": update.effective_user.id},
            {"$set": {"phone_numbers": all_numbers,
                      "addresses": all_addresses}},
            upsert=True)
        # Clear cart
        carts_table.update_one({"bot_id": context.bot.id,
                                "user_id": update.effective_user.id},
                               {"$set": {"products": list()}})
        # Send notification
        # Send notification about new order to all admins
        order = AdminOrder(context, inserted_id)
        for admin in users_table.find({"bot_id": context.bot.id,
                                       "is_admin": True}):
            # Create notification text and send it.
            text = context.bot.lang_dict["shop_order_template"].format(
                order.article, order.user_mention)

            context.bot.send_message(chat_id=admin["chat_id"],
                                     text=text,
                                     parse_mode=ParseMode.HTML)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=context.bot.lang_dict["thank_you"],
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["back_button"],
                    callback_data="back_to_cart")]]))
        return ConversationHandler.END


ONLINE_PURCHASE_HANDLER = CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                               pattern=r'online_buy')

HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(
    PurchaseBot().precheckout_callback)  # TODO make different for donations and shop

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               PurchaseBot().successful_payment_callback)
