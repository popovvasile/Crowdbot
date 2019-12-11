#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler, CallbackQueryHandler)
import logging
import datetime
# Enable logging
from database import purchases_table, products_table, chatbots_table
from helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class PurchaseBot(object):
    def error(self, update, context, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def start_purchase(self, update, context):
        query = update.callback_query
        button_callback_data = query.data

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id, )
        purchase_request = products_table.find_one({"bot_id": context.bot.id, "title_lower": button_callback_data.replace(
            "pay_product_", "")})

        provider_token = chatbots_table.find_one({"bot_id": context.bot.id})["donate"][
            "payment_token"]  # TODO when creating products, double check if payment token has been added
        context.bot.send_message(update.callback_query.message.chat.id, "Pay:{} {}".format(
            str(purchase_request["price"]), str(purchase_request["currency"])))
        title = purchase_request['title']
        description = purchase_request['title']
        payload = "Purchase"
        start_parameter = "shop-payment"  # TODO change in production
        currency = purchase_request['currency']
        prices = [LabeledPrice(title, purchase_request["price"])]
        context.bot.sendInvoice(update.callback_query.message.chat_id, title, description, payload,
                        provider_token, start_parameter, currency, prices,
                        need_name=True, need_phone_number=True,
                        need_email=True, need_shipping_address=purchase_request["shipping"], is_flexible=True
                        )
        context.bot.send_message(update.callback_query.message.chat.id,
                         text=string_dict(context)["back_text"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(context)["back_button"],
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
        buttons = [[InlineKeyboardButton(text=string_dict(context)["back_button"],
                                         callback_data="help_back")]]
        markup = InlineKeyboardMarkup(buttons)
        context.user_data = dict()
        context.user_data["status"] = "Paid"
        context.user_data['timestamp_paid'] = datetime.datetime.now()
        context.user_data["amount"] = update.message.successful_payment.total_amount
        context.user_data["chat_id"] = update.message.chat_id
        context.user_data["bot_id"] = context.bot.id

        purchases_table.insert_one(context.user_data)
        update.message.reply_text(string_dict(context)["thank_purchase"], markup=markup)
        context.user_data.clear()
        return ConversationHandler.END

    def cancel(self, update, context):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(update, context)

        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(update, context)
        context.user_data.clear()
        return ConversationHandler.END


PURCHASE_HANDLER = CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                        pattern=r'pay_product')

HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(PurchaseBot().precheckout_callback)

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               PurchaseBot().successful_payment_callback)
