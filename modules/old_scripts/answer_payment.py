#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import LabeledPrice
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler, RegexHandler)
import logging
import datetime
# Enable logging
from telegram.ext.dispatcher import run_async
from database import payments_requests_table, payments_table
from modules.helper_funcs.auth import initiate_chat_id
from telegram.ext import ConversationHandler, CommandHandler
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
__mod_name__ = "My payments"

__admin_help__ = """

 - /create_payment - create a payment
 - /my_payments - to check and pay a specific payment
 - /change_payment_token - change the payment token
 - /cancel to cancel a command
"""

__user_help__ = """
 - /my_payments - to check or pay a specific payment
 - /cancel to cancel a command
"""
__admin_keyboard__ = [["/create_payment"], ["/my_payments"], ["/change_payment_token"]]

__user_keyboard__ = [["/payments"]]


CHOOSING_PAYMENT, HANDLE_PRECHECKOUT, HANDLE_SUCCES = range(3)

class PaymentBot(object):
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)
    # @if_admin
    @staticmethod
    @run_async
    def payments_list(bot, update):  # TODO make this with buttons as well
        chat_id, txt = initiate_chat_id(update)
        chat = chats_table.find_one({"chat_id": chat_id})
        payment_requests = payments_table.find({"bot_id": bot.id})
        text_to_send_answer = ''
        for payment_request in payment_requests:
            if chat['tag'] in payment_request['tags']:
                text_to_send_answer += str("Title:{} \nDescription: {} \nStatus:{}\n".format(
                    payment_request["title"],
                    payment_request['description'],
                    payment_request['paid_status']
                )) + '\n\n'
        bot.send_message(chat_id, "To make a payment, click /execute_payment")
    @run_async
    def start_payment(self, bot, update, user_data):
        text_to_send_answer = ''
        for payment_request in payment_requests:
            if chat['tag'] in payment_request['tags']:
                text_to_send_answer += str("Title:{} \nDescription: {} \nStatus:{}\n".format(
                    payment_request["title"],
                    payment_request['description'],
                    payment_request['paid_status']
                )) + '\n\n'

        bot.send_message(chat_id, "To make a payment, click /execute_payment")
        command_list = [
            payment['title'] for payment in payments_table.find({"bot_id": bot.id,
            "user_id": update.message.from_user.id}) if payment['title']==False]
        if len(command_list) >0:
            reply_keyboard = [list(set(command_list))]
            update.message.reply_text(
                "Please choose one of your payment requests",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return CHOOSING_PAYMENT
        else:
            return ConversationHandler.END

    def execute_payment(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        payment_request = payments_table.find_one({"bot_id": bot.id,
                                                   "title": txt,
                                                   "user_id": update.message.from_user.id})
        if payment_request:
            if payment_request['status'] == False:
                title = payment_request['title']
                description = payment_request['description']
                payload = payment_request['type']
                provider_token = payment_request['token']
                start_parameter = "test-payment"  # TODO change in production
                currency = payment_request['currency']
                price = payment_request['amount']
                prices = [LabeledPrice(title, price * 100)]
                bot.sendInvoice(chat_id, title, description, payload,
                                provider_token, start_parameter, currency, prices)
                user_data = payment_request
                return HANDLE_PRECHECKOUT
            else:
                update.message.reply_text("You already paid for this)")
                return ConversationHandler.END
        else:
            update.message.reply_text("There is no payment request for you with such title")
            return ConversationHandler.END




    # after (optional) shipping, it's the pre-checkout
    def precheckout_callback(self, bot, update, user_data):
        query = update.pre_checkout_query
        # # check the payload, is this from your bot?
        # if query.invoice_payload != 'Custom-Payload':
        #     # answer False pre_checkout_query
        #     bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False,
        #                                   error_message="Something went wrong...")
        # else:
        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
        return HANDLE_SUCCES

    # finally, after contacting to the payment provider...
    def successful_payment_callback(self, bot, update, user_data):
        # do something after successful receive of payment?
        user_data["status"] = "Paid"
        user_data['timestamp_paid'] = datetime.datetime.now()
        payment_request = payments_table.update_one({"bot_id": bot.id,
                                                     "title": txt.split("_")[2],
                                                     "user_id": update.message.from_user.id},
                                                    user_data)
        update.message.reply_text("Thank you for your payment!")
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text("Command is finished. Until next time!")
        return ConversationHandler.END


EXECUTE_PAYMENT_HANDLER = ConversationHandler(
    entry_points=[
        CommandHandler('my_payments',
                     PaymentBot().start_payment,
                     pass_user_data=True),
    ],
    states={
        CHOOSING_PAYMENT:[MessageHandler(Filters.text,
                     PaymentBot().execute_payment,
                     pass_user_data=True),],
        HANDLE_PRECHECKOUT: [PreCheckoutQueryHandler(PaymentBot().precheckout_callback,
                                                   pass_user_data=True),
                           CommandHandler('cancel', PaymentBot().cancel),
                             MessageHandler(Filters.successful_payment,
                                            PaymentBot().successful_payment_callback,
                                            pass_user_data=True)
                             ],
        HANDLE_SUCCES: [MessageHandler(Filters.successful_payment,
                                     PaymentBot().successful_payment_callback,
                                     pass_user_data=True),]
    },
    fallbacks=[ MessageHandler(Filters.successful_payment,
                                     PaymentBot().successful_payment_callback,
                                     pass_user_data=True),
                MessageHandler(filters=Filters.command, callback=PaymentBot().cancel)
                ])


