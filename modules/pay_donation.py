#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler, RegexHandler, CommandHandler,
                          ConversationHandler, run_async, CallbackQueryHandler)
import logging
import datetime
# Enable logging
from database import donations_table, chatbots_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
__mod_name__ = "Donation"

__admin_help__ = """
 Click:
  - Donate - to make a donation for this organization
  - Allow donations - to allow the users of this bot to donate for your organization 
  - Configure - to edit the current donation settings

"""

__visitor_help__ = """
 Click:
  - Donate to make a donation for this organization
"""

__admin_keyboard__ = [InlineKeyboardButton(text="Donate", callback_data="donate"),
                      InlineKeyboardButton(text="Allow donations", callback_data="allow_donation"),
                      InlineKeyboardButton(text="Configure", callback_data="configure_donation")]
__visitor_keyboard__ = [InlineKeyboardButton(text="Donate", callback_data="donate")]


DONATION_MESSAGE, EXECUTE_DONATION, HANDLE_PRECHECKOUT, HANDLE_SUCCES = range(4)


class DonationBot(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_donation_payment")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    @run_async
    def start_donation(self, bot, update, user_data):
        donation_request = chatbots_table.find_one({"bot_id": bot.id})

        if donation_request:

            if "donation" in donation_request:
                bot.send_message(update.callback_query.message.chat.id,
                                 "Great! We very glad that you want to donate for our cause!")
                bot.send_message(update.callback_query.message.chat.id,
                                 "First, tell us how much do you want to donate. Enter a floating point number")
                bot.send_message(update.callback_query.message.chat.id,
                                 "Remember, we use {} as our primary currency".format(
                    donation_request["donation"]['currency'])
                )
                bot.send_message(update.callback_query.message.chat.id,
                                 text="To return to main menu, click 'Back' ",
                                          reply_markup=InlineKeyboardMarkup(  # TODO modify this shit
                                              [[InlineKeyboardButton(text="Back",
                                                                     callback_data="cancel_donation_payment")]]))
                return DONATION_MESSAGE
            else:
                bot.send_message(update.callback_query.message.chat.id,
                                 "Sorry, no option for donation yet")
                return ConversationHandler.END

        else:
            bot.send_message(update.callback_query.message.chat.id,
                             "Sorry, no option for donation yet")
            return ConversationHandler.END

    @run_async
    def donation_message(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["amount"] = txt
        update.message.reply_text("You can write a message about your donation, "
                                  "tell why you want to donate or click SKIP",
                                  reply_markup=ReplyKeyboardMarkup([["SKIP"]], one_time_keyboard=True))
        return EXECUTE_DONATION

    @run_async
    def execute_donation(self, bot, update, user_data):
        query = update.callback_query
        if query:
            if query.data == "help_back":
                return ConversationHandler.END

        chat_id, txt = initiate_chat_id(update)
        user_data["donation_message"] = txt
        donation_request = chatbots_table.find_one({"bot_id": bot.id})["donation"]
        title = donation_request['title']
        description = donation_request['description']
        payload = "Donation"
        provider_token = donation_request['payment_token']
        start_parameter = "test-payment"  # TODO change in production
        currency = donation_request['currency']
        amount = int(user_data["amount"])
        prices = [LabeledPrice(title, amount * 100)]
        bot.sendInvoice(chat_id, title, description, payload,
                        provider_token, start_parameter, currency, prices)
        update.message.reply_text(text="To return to main menu, click 'Back' ",
                                  reply_markup=InlineKeyboardMarkup(
                                      [[InlineKeyboardButton(text="Back",
                                                             callback_data="help_back")]]))
        user_data = donation_request

        return HANDLE_PRECHECKOUT

    @run_async
    def precheckout_callback(self, bot, update, user_data):
        query = update.callback_query
        if query:
            if query.data == "help_back":
                return ConversationHandler.END
        query = update.pre_checkout_query

        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
        return HANDLE_SUCCES

    @run_async
    # finally, after contacting to the donation provider...
    def successful_payment_callback(self, bot, update, user_data):
        # do something after successful receive of donation?
        user_data["status"] = "Paid"
        user_data['timestamp_paid'] = datetime.datetime.now()
        donations_table.update_one({"bot_id": bot.id,
                                    "title": user_data['title'],
                                    "user_id": update.message.from_user.id},
                                   user_data)
        update.message.reply_text("Thank you for your donation!")
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(bot, update)

        return ConversationHandler.END

    def back(self, bot, update):

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END


DONATE_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=DonationBot().start_donation,
                             pass_user_data=True,
                             pattern=r'donate'),
    ],
    states={
        DONATION_MESSAGE: [MessageHandler(callback=DonationBot().donation_message,
                                          filters=Filters.text,
                                          pass_user_data=True),
                           CallbackQueryHandler(callback=DonationBot().back, pattern=r"cancel_donation_payment"),
                           CommandHandler('cancel', DonationBot().cancel)
                           ],
        EXECUTE_DONATION: [MessageHandler(callback=DonationBot().execute_donation,
                                          filters=Filters.text,
                                          pass_user_data=True),
                           CallbackQueryHandler(callback=DonationBot().back, pattern=r"cancel_donation_payment"),
                           CommandHandler('cancel', DonationBot().cancel)
                           ],
        HANDLE_PRECHECKOUT: [PreCheckoutQueryHandler(DonationBot().precheckout_callback,
                                                     pass_user_data=True),
                             CallbackQueryHandler(callback=DonationBot().back, pattern=r"cancel_donation_payment"),
                             CommandHandler('cancel', DonationBot().cancel),
                             MessageHandler(Filters.successful_payment,
                                            DonationBot().successful_payment_callback,
                                            pass_user_data=True)
                             ],
        HANDLE_SUCCES: [MessageHandler(Filters.successful_payment,
                                       DonationBot().successful_payment_callback,
                                       pass_user_data=True),
                        CallbackQueryHandler(callback=DonationBot().back, pattern=r"cancel_donation_payment")]
    },
    fallbacks=[CallbackQueryHandler(callback=DonationBot().back, pattern=r"cancel_donation_payment"),
               MessageHandler(Filters.successful_payment,
                              DonationBot().successful_payment_callback,
                              pass_user_data=True),

               MessageHandler(filters=Filters.command, callback=DonationBot().back),

               CommandHandler('cancel', DonationBot().cancel)
               ])
