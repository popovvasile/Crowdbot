#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler, CallbackQueryHandler)
import logging
import datetime
# Enable logging
from database import purchases_table, products_table, chatbots_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


class PurchaseBot(object):
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def start_purchase(self, bot, update):
        query = update.callback_query
        button_callback_data = query.data

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id, )
        purchase_request = products_table.find_one({"bot_id": bot.id, "title_lower": button_callback_data.replace(
            "pay_product_", "")})

        provider_token = chatbots_table.find_one({"bot_id": bot.id})["donate"][
            "payment_token"]  # TODO when creating products, double check if payment token has been added
        bot.send_message(update.callback_query.message.chat.id, "Pay:{} {}".format(
            str(purchase_request["price"]), str(purchase_request["currency"])))
        title = purchase_request['title']
        description = purchase_request['title']
        payload = "Purchase"
        start_parameter = "test-payment"  # TODO change in production
        currency = purchase_request['currency']
        prices = [LabeledPrice(title, purchase_request["price"])]
        bot.sendInvoice(update.callback_query.message.chat_id, title, description, payload,
                        provider_token, start_parameter, currency, prices,
                        need_name=True, need_phone_number=True,
                        need_email=True, need_shipping_address=purchase_request["shipping"], is_flexible=True
                        )
        bot.send_message(update.callback_query.message.chat.id,
                         text=string_dict(bot)["back_text"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_back")]]))
        logger.info("User {} on bot {} requested a purchase".format(
            update.effective_user.first_name, bot.first_name))

        return ConversationHandler.END

    def precheckout_callback(self, bot, update):
        # query = update.callback_query
        # if query:
        #     if query.data == "help_back":
        #         return ConversationHandler.END
        query = update.pre_checkout_query

        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
        return ConversationHandler.END

    # finally, after contacting to the purchase provider...
    def successful_payment_callback(self, bot, update):
        # TODO add counting of purchases and prepare for callback_query
        # do something after successful receive of purchase?
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_back")]]
        markup = InlineKeyboardMarkup(buttons)
        user_data = dict()
        user_data["status"] = "Paid"
        user_data['timestamp_paid'] = datetime.datetime.now()
        user_data["amount"] = update.message.successful_payment.total_amount
        user_data["chat_id"] = update.message.chat_id
        user_data["bot_id"] = bot.id

        purchases_table.insert_one(user_data)
        update.message.reply_text(string_dict(bot)["thank_purchase"], markup=markup)
        user_data.clear()
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(bot, update)

        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
        return ConversationHandler.END


PURCHASE_HANDLER = CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                        pattern=r'pay_product')

HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(PurchaseBot().precheckout_callback)

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               PurchaseBot().successful_payment_callback)
