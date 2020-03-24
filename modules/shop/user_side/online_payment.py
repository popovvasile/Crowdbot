#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import datetime
from random import randint

from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler, CallbackQueryHandler)

from database import products_table, chatbots_table, orders_table, \
    shop_customers_contacts_table, carts_table, \
    users_table
from helper_funcs.misc import delete_messages
from modules.shop.components.order import UserOrder, AdminOrder
from modules.shop.user_side.cart import Cart

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
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat.id,
                text=context.bot.lang_dict["to_pay"].format(
                    str(context.user_data["order"]["total_price"]),
                    str(context.user_data["order"]["currency"]))))

        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat.id,
                text=context.bot.lang_dict["add_order_comment"],
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                    text=context.bot.lang_dict["shop_admin_continue_btn"],
                    callback_data="pass_order_comment")],
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="back_to_cart")]
                ])))
        return ORDER_CONTACTS

    @staticmethod
    def ask_contacts(update, context):
        delete_messages(update, context, True)
        # TODO DESCRIPTION LENGTH VALIDATION
        if update.callback_query:
            context.user_data["order"]["user_comment"] = ""
        else:
            context.user_data["order"]["user_comment"] = update.message.text

        context.user_data["used_contacts"] = (
                shop_customers_contacts_table.find_one(
                    {"bot_id": context.bot.id,
                     "user_id": update.effective_user.id}) or {})
        # TODO SHARE PHONE NUMBER
        if (context.user_data["used_contacts"]
                and len(context.user_data["used_contacts"]["phone_numbers"])):
            text = context.bot.lang_dict["tell_phone_number"]
            buttons = [
                [InlineKeyboardButton(text=x,
                                      callback_data=f"phone_number/{x}")]
                for x in context.user_data["used_contacts"]["phone_numbers"]]
        else:
            text = context.bot.lang_dict["tell_phone_number_short"]
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
        # TODO PHONE NUMBER VALIDATION
        if update.callback_query:
            context.user_data["order"]["phone_number"] = (
                update.callback_query.data.split("/")[1])
        else:
            context.user_data["order"]["phone_number"] = update.message.text
            # set it to check in the next step if there are no shipping
            update.message.text = "phone"

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        # TODO SHARE GEO POSITION
        if shop["shipping"]:
            if (context.user_data["used_contacts"]
                    and len(context.user_data["used_contacts"]["addresses"])):
                text = context.bot.lang_dict["tell_address"]
                buttons = [
                    [InlineKeyboardButton(text=x,
                                          callback_data=f"address/{x}")]
                    for x in context.user_data["used_contacts"]["addresses"]]
            else:
                text = context.bot.lang_dict["tell_address_short"]
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
            return PurchaseBot.order_finish(update, context)

    @staticmethod
    def order_finish(update, context):
        delete_messages(update, context, True)
        order = UserOrder(context, context.user_data["order"])
        # Check products availability
        for item in order.items:
            if not item.item_exist:
                update.callback_query.answer(
                    context.bot.lang_dict["cart_changed_notification"],
                    show_alert=True)
                return Cart().back_to_cart(update, context)

        # Save contacts
        all_addresses = context.user_data["used_contacts"].get(
            "addresses", list())
        all_numbers = context.user_data["used_contacts"].get(
            "phone_numbers", list())
        address = context.user_data["order"].get("address")
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

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        order = UserOrder(context, context.user_data["order"])
        title = order.items_json[0]["product"]['name']
        description = order.items_json[0]["product"]['description']
        payload = "Purchase"
        start_parameter = "shop-payment"  # TODO change in production
        prices = [LabeledPrice(title, int(float(order.total_price) * 100))]
        context.bot.sendInvoice(update.callback_query.message.chat_id, title, description, payload,
                                shop["payment_token"], start_parameter, order.currency, prices
                                )
        context.bot.send_message(update.callback_query.message.chat.id,
                                 text=context.bot.lang_dict["back_text"],
                                 reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton(
                                         text=context.bot.lang_dict["back_button"],
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

    @staticmethod
    def successful_payment_callback(update, context):
        print(update.pre_checkout_query)
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
        inserted_id = orders_table.update_one(
            {**context.user_data["order"],
             **{"article": randint(10000, 99999),
                "status": False,
                "bot_id": context.bot.id,
                "user_id": update.effective_user.id,
                "creation_timestamp": datetime.datetime.now(),
                # "name": update.effective_user.name,
                "in_trash": False,
                "paid": True
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


ONLINE_PURCHASE_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                       pattern=r'online_buy')],
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
            CallbackQueryHandler(pattern="address",
                                 callback=PurchaseBot().order_finish)
        ]


    },
    fallbacks=[CallbackQueryHandler(Cart().back_to_cart,
                                    pattern="back_to_cart")]
)

HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(
    PurchaseBot().precheckout_callback)

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               PurchaseBot().successful_payment_callback)
