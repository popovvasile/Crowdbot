#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from random import randint
import html

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from database import (orders_table, chatbots_table, carts_table, shop_customers_contacts_table,
                      products_table, users_table)
from helper_funcs.misc import delete_messages
from helper_funcs.constants import MIN_ADDRESS_LENGTH, MAX_ADDRESS_LENGTH
from modules.shop.user_side.cart import Cart
from modules.shop.user_side.online_payment import OnlinePayment
from modules.shop.components.order import UserOrder, Product, AdminOrder


ORDER_DESCRIPTION, ORDER_CONTACTS, ORDER_ADDRESS, CONFIRM_ORDER, \
    ORDER_FINISH = range(5)


class PurchaseBot(object):
    @staticmethod
    def send_address_markup(update, context, invalid_address_txt=False):
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

        if invalid_address_txt:
            text = invalid_address_txt + text

        buttons.append([InlineKeyboardButton(
            text=context.bot.lang_dict["back_button"],
            callback_data="back_to_cart")])

        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=text,
                reply_markup=InlineKeyboardMarkup(buttons)))

    @staticmethod
    def send_number_markup(update, context, invalid_number=False):
        if (context.user_data["used_contacts"]
                and len(context.user_data["used_contacts"]["phone_numbers"])):
            text = context.bot.lang_dict["tell_phone_number"]
            buttons = [[InlineKeyboardButton(text=x, callback_data=f"phone_number/{x}")]
                       for x in context.user_data["used_contacts"]["phone_numbers"]]
        else:
            text = context.bot.lang_dict["tell_phone_number_short"]
            buttons = []

        if invalid_number:
            text = context.bot.lang_dict["invalid_number"] + text

        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="back_to_cart")])
        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text,
                                     reply_markup=InlineKeyboardMarkup(buttons)))

    @staticmethod
    def validate_number(number):
        if not 5 < len(number) < 25:
            return False
        number.replace(
            "-", "").replace(
            "(", "").replace(
            ")", "").replace(
            " ", "").replace(
            "*", "")
        if number.isdigit():
            return True
        else:
            return False

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
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                         text=context.bot.lang_dict["shop_admin_continue_btn"],
                         callback_data="pass_order_comment")],
                    [InlineKeyboardButton(
                         text=context.bot.lang_dict["back_button"],
                         callback_data="back_to_cart")]
                     ])))
        return ORDER_CONTACTS

    def ask_contacts(self, update, context):
        delete_messages(update, context, True)
        if update.callback_query:
            context.user_data["order"]["user_comment"] = ""
        elif len(update.message.text) > 445:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    context.bot.lang_dict["order_comment_too_long"],
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                             text=context.bot.lang_dict["shop_admin_continue_btn"],
                             callback_data="pass_order_comment")],
                        [InlineKeyboardButton(
                             text=context.bot.lang_dict["back_button"],
                             callback_data="back_to_cart")]
                         ])))
            return ORDER_CONTACTS
        else:
            context.user_data["order"]["user_comment"] = update.message.text

        context.user_data["used_contacts"] = (
            shop_customers_contacts_table.find_one(
                {"bot_id": context.bot.id,
                 "user_id": update.effective_user.id}) or {})
        self.send_number_markup(update, context)
        return ORDER_ADDRESS

    def ask_address(self, update, context):
        delete_messages(update, context, True)
        if update.callback_query:
            context.user_data["order"]["phone_number"] = (
                update.callback_query.data.split("/")[1])
        else:
            if self.validate_number(update.message.text):
                context.user_data["order"]["phone_number"] = update.message.text
                # set it to check in the next step if there are no shipping
                update.message.text = "phone"
            else:
                self.send_number_markup(update, context, True)
                return ORDER_ADDRESS

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]

        if shop["shipping"]:
            self.send_address_markup(update, context)
            return CONFIRM_ORDER
        else:
            return self.confirm_order(update, context)

    def confirm_order(self, update, context):
        delete_messages(update, context, True)
        if update.callback_query and "address" in update.callback_query.data:
            context.user_data["order"]["address"] = (update.callback_query.data.split("/")[1])
        elif update.message and update.message.text != "phone":
            if len(update.message.text) < MIN_ADDRESS_LENGTH:
                self.send_address_markup(update, context, context.bot.lang_dict["short_address"])
                return CONFIRM_ORDER
            elif len(update.message.text) > MAX_ADDRESS_LENGTH:
                self.send_address_markup(update, context, context.bot.lang_dict["long_address"])
                return CONFIRM_ORDER
            else:
                context.user_data["order"]["address"] = update.message.text
        else:
            context.user_data["order"]["address"] = ""

        context.user_data["order_data"] = Cart().order_data(update, context)
        if not context.user_data["order_data"]["order"]["items"]:
            return Cart().back_to_cart(update, context)

        # shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        context.user_data["order"] = {**context.user_data["order"],
                                      **context.user_data["order_data"]["order"]}
        context.user_data["order"]["shipping"] = (
            context.user_data["order_data"]["shop"]["shipping"])

        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=context.user_data["order_data"]["template"],
                                     parse_mode=ParseMode.HTML))
        # Creating confirm order text
        confirm_text = context.bot.lang_dict["confirm_order_text"].format(
            context.user_data['order']['phone_number'])
        if context.user_data["order"]["shipping"]:
            confirm_text += context.bot.lang_dict["delivery_to"].format(
                html.escape(context.user_data["order"]['address'], quote=False))
        else:
            confirm_text += context.bot.lang_dict["pick_up_from"].format(
                html.escape(context.user_data["order_data"]["shop"]["address"], quote=False))
        if context.user_data["order"]["user_comment"]:
            confirm_text += context.bot.lang_dict["comment_field"].format(
                html.escape(context.user_data['order']['user_comment'], quote=False))

        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["finish_order_btn"],
                                             callback_data=f"finish_order")])
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="back_to_cart")])

        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=confirm_text,
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(buttons)))
        return ORDER_FINISH

    @staticmethod
    def order_finish(update, context):
        delete_messages(update, context, True)
        order = UserOrder(context, context.user_data["order"])
        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        # Check products availability
        for item in order.items:
            if not item.item_exist:
                update.callback_query.answer(
                    context.bot.lang_dict["cart_changed_notification"],
                    show_alert=True)
                return Cart().back_to_cart(update, context)
        # Create order
        inserted_id = orders_table.insert_one(
            {**context.user_data["order"],
             **{"status": False,
                "bot_id": context.bot.id,
                "user_id": update.effective_user.id,
                "creation_timestamp": datetime.datetime.now(),
                "in_trash": False,
                "paid": False}}).inserted_id
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
        all_addresses = context.user_data["used_contacts"].get("addresses", list())
        all_numbers = context.user_data["used_contacts"].get("phone_numbers", list())
        address = context.user_data["order"]["address"]
        number = context.user_data["order"]["phone_number"]
        if address and address not in all_addresses:
            if len(all_addresses) > 4:
                all_addresses.insert(0, address)
                del all_addresses[-1]
            else:
                all_addresses.append(address)
        if number not in all_numbers:
            if len(all_numbers) > 4:
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
        # Send notification about new order to all admins
        order = AdminOrder(context, inserted_id)
        for admin in users_table.find({"bot_id": context.bot.id, "is_admin": True}):
            if admin["order_notification"]:
                # Create notification text and send it.
                text = context.bot.lang_dict["new_order_notification"].format(
                    order.article, order.user_mention)
                try:
                    context.bot.send_message(chat_id=admin["chat_id"],
                                             text=text,
                                             reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                                 text=context.bot.lang_dict["notification_close_btn"],
                                                 callback_data="dismiss"
                                             )]]),
                                             parse_mode=ParseMode.HTML)
                except:
                    continue
        final_text = context.bot.lang_dict["order_success"]
        if shop["shop_type"] == "online":
            final_text += context.bot.lang_dict["order_success_online"]
            OnlinePayment().send_invoice(update, context, order, shop)
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=final_text,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="back_to_user_orders")]])))
        return ConversationHandler.END


OFFLINE_PURCHASE_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                       pattern=r'create_order')],
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
        CONFIRM_ORDER: [
            CallbackQueryHandler(pattern=r"address",
                                 callback=PurchaseBot().confirm_order),
            MessageHandler(Filters.text,
                           callback=PurchaseBot().confirm_order)],

        ORDER_FINISH: [
            CallbackQueryHandler(pattern="finish_order",
                                 callback=PurchaseBot().order_finish)]
    },
    fallbacks=[CallbackQueryHandler(Cart().back_to_cart,
                                    pattern="back_to_cart")]
)
