#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler, CommandHandler,
                          ConversationHandler, run_async, CallbackQueryHandler)
import logging
import datetime
# Enable logging
from database import donations_table, chatbots_table, user_mode_table
from modules.helper_funcs.auth import initiate_chat_id, if_admin
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


EXECUTE_DONATION = 1


class DonationBot(object):
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    @run_async
    def start_donation(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id,)
        donation_request = chatbots_table.find_one({"bot_id": bot.id})
        current_user_mode = user_mode_table.find_one({"bot_id": bot.id,
                                                      "user_id": update.effective_user.id}) or {"user_mode": False}
        if donation_request.get("donate") is not None and donation_request.get("donate") != {}:
            bot.send_message(update.callback_query.message.chat.id,
                             donation_request["donate"]["description"])
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["pay_donation_str_1"])
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["pay_donation_str_2"].format(
                                 donation_request["donate"]['currency']))
            bot.send_message(update.callback_query.message.chat.id,
                             text=string_dict(bot)["back_text"],
                             reply_markup=InlineKeyboardMarkup(
                                          [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                            callback_data="cancel_donation_payment")]]))
            return EXECUTE_DONATION

        else:
            try:
                if current_user_mode["user_mode"] is True:
                    admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                           callback_data="help_back")]
                    bot.send_message(update.callback_query.message.chat.id,
                                     string_dict(bot)["pay_donation_str_4"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
                elif if_admin(update, bot):
                    admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                                           callback_data="allow_donation"),
                                      InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                           callback_data="help_back")]
                    bot.send_message(update.callback_query.message.chat.id,
                                     string_dict(bot)["allow_donation_text"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
                else:
                    admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                           callback_data="help_back")]
                    bot.send_message(update.callback_query.message.chat.id,
                                     string_dict(bot)["pay_donation_str_4"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            except KeyError:
                admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                                       callback_data="allow_donation"),
                                  InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                       callback_data="help_back")]
                bot.send_message(update.callback_query.message.chat.id,
                                 string_dict(bot)["allow_donation_text"],
                                 reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    # @run_async
    # def donation_message(self, bot, update, user_data):
    #     chat_id, txt = initiate_chat_id(update)
    #     user_data["amount"] = txt
    #     update.message.reply_text("You can write a message about your crowdfunding campaign, "
    #                               "tell why you want to donate or click SKIP",
    #                               reply_markup=ReplyKeyboardMarkup([["SKIP"]], one_time_keyboard=True))
    #     return EXECUTE_DONATION

    @run_async
    def execute_donation(self, bot, update, user_data):
        query = update.callback_query
        if query:
            if query.data == "help_back":
                return ConversationHandler.END

        chat_id, txt = initiate_chat_id(update)
        # user_data["amount"] = txt
        try:
            amount = int(float(txt)*100)  # TODO add an exception if not int
        except ValueError:
            update.message.reply_text(text=string_dict(bot)["pay_donation_str_5"],
                                      reply_markup=InlineKeyboardMarkup(
                                          [[InlineKeyboardButton(text=string_dict(bot)["menu_button"],
                                            callback_data="cancel_donation_payment")]]))
            return EXECUTE_DONATION
        donation_request = chatbots_table.find_one({"bot_id": bot.id})["donate"]
        title = donation_request['title']
        description = donation_request['description']
        payload = "Donation"
        provider_token = donation_request['payment_token']
        start_parameter = "test-payment"  # TODO change in production
        currency = donation_request['currency']
        print(amount)
        prices = [LabeledPrice(title, amount)]
        bot.sendInvoice(chat_id, title, description, payload,
                        provider_token, start_parameter, currency, prices)
        update.message.reply_text(text=string_dict(bot)["back_text"],
                                  reply_markup=InlineKeyboardMarkup(
                                      [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                             callback_data="help_back")]]))
        logger.info("User {} on bot {} requested a donation".format(
            update.effective_user.first_name, bot.first_name))

        return ConversationHandler.END

    @run_async
    def precheckout_callback(self, bot, update):
        # query = update.callback_query
        # if query:
        #     if query.data == "help_back":
        #         return ConversationHandler.END
        query = update.pre_checkout_query

        bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
        return ConversationHandler.END

    @run_async
    # finally, after contacting to the donation provider...
    def successful_payment_callback(self, bot, update):
        # TODO add counting of donations and prepare for callback_query
        # do something after successful receive of donation?
        user_data = dict()
        user_data["status"] = "Paid"
        user_data['timestamp_paid'] = datetime.datetime.now()
        user_data["amount"] = update.message.successful_payment.total_amount
        donations_table.insert_one(user_data)
        update.message.reply_text("Thank you for your donation!")
        user_data.clear()
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(bot, update)

        return ConversationHandler.END

    def back(self, bot, update, user_data):
        print("TEST")
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
        return ConversationHandler.END


DONATE_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=DonationBot().start_donation,
                             pattern=r'pay_donation'),
    ],
    states={
        # DONATION_MESSAGE: [MessageHandler(callback=DonationBot().donation_message,
        #                                   filters=Filters.text,
        #                                   pass_user_data=True),
        #                    CallbackQueryHandler(callback=DonationBot().back, pattern=r"cancel_donation_payment"),
        #                    CommandHandler('cancel', DonationBot().cancel)
        #                    ],
        EXECUTE_DONATION: [MessageHandler(callback=DonationBot().execute_donation,
                                          filters=Filters.text,
                                          pass_user_data=True),
                           CallbackQueryHandler(callback=DonationBot().back,
                                                pattern=r"cancel_donation_payment",
                                                pass_user_data=True),
                           CommandHandler('cancel', DonationBot().cancel)
                           ],

    },
    fallbacks=[CallbackQueryHandler(callback=DonationBot().back,
                                    pattern=r"cancel_donation_payment", pass_user_data=True),
               MessageHandler(Filters.successful_payment,
                              DonationBot().successful_payment_callback,
                              pass_user_data=True),

               MessageHandler(filters=Filters.command, callback=DonationBot().back, pass_user_data=True),

               CommandHandler('cancel', DonationBot().cancel)
               ])


HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(DonationBot().precheckout_callback)

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               DonationBot().successful_payment_callback)
