#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from random import randint

from telegram.error import BadRequest
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler, CallbackQueryHandler)

from database import products_table, chatbots_table, orders_table, \
    shop_customers_contacts_table, carts_table, \
    users_table
from helper_funcs.misc import delete_messages
from logs import logger
from modules.shop.components.order import UserOrder, AdminOrder
from modules.shop.user_side.cart import Cart


class OnlinePayment(object):
    def send_invoice(self, update, context, order, shop=None, reply_markup=None, description=None):
        context.user_data["paid_order"] = order
        if not shop:
            shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]

        if not description:
            description = "\n".join([
                "{}\nx{} {} {}\n".format(
                    item["product"]["name"],
                    item["quantity"],
                    item["product"]["price"],
                    order.currency) for item in order.items_json])

        # The first button must be a Pay button
        if reply_markup:
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(text=context.bot.lang_dict["pay_button"],
                                       pay=True)]]
                + reply_markup)

        title = context.bot.lang_dict["order_id"].format(str(order.article))
        payload = "Purchase"
        start_parameter = "shop-payment"  # TODO change in production
        prices = [LabeledPrice(title, int(float(order.total_price) * 100))]
        try:
            context.user_data["to_delete"].append(
                context.bot.sendInvoice(chat_id=update.effective_chat.id,
                                        title=title,
                                        description=description,
                                        payload=payload,
                                        provider_token=shop["payment_token"],
                                        start_parameter=start_parameter,
                                        currency=order.currency,
                                        prices=prices,
                                        reply_markup=reply_markup))
        except BadRequest as exception:
            logger.info(f"Sending invoice excseption -> {exception}. "
                        f"User {update.effective_user.full_name} on bot {context.bot.username}")
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    context.bot.lang_dict["payment_not_available"],
                    parse_mode=ParseMode.HTML))
        logger.info("User {} on bot {} requested a purchase".format(
            update.effective_user.first_name, context.bot.first_name))

    def precheckout_callback(self, update, context):
        # query = update.callback_query
        # if query:
        #     if query.data == "help_back":
        #         return ConversationHandler.END
        # TODO - back problem coz there are now callback_query
        # if not context.user_data.get("paid_order"):
        #     return Cart().back_to_cart(update, context)
        query = update.pre_checkout_query
        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
        return ConversationHandler.END

    @staticmethod
    def successful_payment_callback(update, context):
        delete_messages(update, context, True)
        orders_table.update_one({"_id": context.user_data["paid_order"].id_},
                                {"$set": {"paid": True}})
        context.user_data["to_delete"].append(
            context.bot.send_message(
                update.effective_chat.id,
                context.bot.lang_dict["thank_you"],
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="back_to_user_orders")]
                ])))
        return ConversationHandler.END


HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(OnlinePayment().precheckout_callback)

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               OnlinePayment().successful_payment_callback)