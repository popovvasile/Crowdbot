#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler,  CallbackQueryHandler)
import logging
import datetime
# Enable logging
from database import donations_table, chatbots_table, user_mode_table
from helper_funcs.auth import initiate_chat_id, if_admin
from helper_funcs.helper import get_help


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

EXECUTE_DONATION = 1


class DonationBot(object):
    def error(self, update, context, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def start_donation(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id, )
        donation_request = chatbots_table.find_one({"bot_id": context.bot.id})
        current_user_mode = user_mode_table.find_one({"bot_id": context.bot.id,
                                                      "user_id": update.effective_user.id}) or {"user_mode": False}
        if donation_request.get("donate") is not None and donation_request.get("donate") != {}:
            context.bot.send_message(update.callback_query.message.chat.id,
                             donation_request["donate"]["description"])
            context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["pay_donation_str_1"])
            context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["pay_donation_str_2"].format(
                                 donation_request["donate"]['currency']))
            context.bot.send_message(update.callback_query.message.chat.id,
                             text=context.bot.lang_dict["back_text"],
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                        callback_data="help_back")]]))
            return EXECUTE_DONATION

        else:
            try:
                if current_user_mode["user_mode"] is True:
                    admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                           callback_data="help_back")]
                    context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["pay_donation_str_4"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
                elif if_admin(update, context):
                    admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["allow_donations_button"],
                                                           callback_data="allow_donation"),
                                      InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                           callback_data="help_back")]
                    context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["allow_donation_text"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
                else:
                    admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                           callback_data="help_back")]
                    context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["pay_donation_str_4"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            except KeyError:
                admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["allow_donations_button"],
                                                       callback_data="allow_donation"),
                                  InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                       callback_data="help_back")]
                context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["allow_donation_text"],
                                 reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    # 
    # def donation_message(self, update, context):
    #     chat_id, txt = initiate_chat_id(update)
    #     user_data["amount"] = txt
    #     update.message.reply_text("You can write a message about your crowdfunding campaign, "
    #                               "tell why you want to donate or click SKIP",
    #                               reply_markup=ReplyKeyboardMarkup([["SKIP"]], one_time_keyboard=True))
    #     return EXECUTE_DONATION

    def execute_donation(self, update, context):
        query = update.callback_query
        if query:
            if query.data == "help_back" or query.data == "help_back":
                return ConversationHandler.END

        chat_id, txt = initiate_chat_id(update)
        # user_data["amount"] = txt
        try:
            amount = int(float(txt) * 100)  # TODO add an exception if not int
        except ValueError:
            update.message.reply_text(text=context.bot.lang_dict["pay_donation_str_5"],
                                      reply_markup=InlineKeyboardMarkup(
                                          [[InlineKeyboardButton(text=context.bot.lang_dict["menu_button"],
                                                                 callback_data="help_back")]]))
            return EXECUTE_DONATION
        donation_request = chatbots_table.find_one({"bot_id": context.bot.id})["donate"]
        title = donation_request['title']
        description = donation_request['description']
        payload = "Donation"
        provider_token = donation_request['payment_token']
        start_parameter = "test-payment"  # TODO change in production
        currency = donation_request['currency']
        prices = [LabeledPrice(title, amount)]
        context.bot.sendInvoice(chat_id, title, description, payload,
                        provider_token, start_parameter, currency, prices)
        update.message.reply_text(text=context.bot.lang_dict["back_text"],
                                  reply_markup=InlineKeyboardMarkup(
                                      [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                             callback_data="help_back")]]))
        logger.info("User {} on bot {} requested a donation".format(
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

    # finally, after contacting to the donation provider...
    def successful_payment_callback(self, update, context):
        # TODO add counting of donations and prepare for callback_query
        # do something after successful receive of donation?
        buttons=[[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                       callback_data="help_back")]]
        markup = InlineKeyboardMarkup(buttons)
        # context.user_data = dict()
        context.user_data.clear()
        context.user_data["status"] = "Paid"
        context.user_data['timestamp_paid'] = datetime.datetime.now()
        context.user_data["amount"] = update.message.successful_payment.total_amount
        context.user_data["currency"] = update.message.successful_payment.currency
        context.user_data["chat_id"] = update.message.chat_id
        context.user_data["bot_id"] = context.bot.id
        context.user_data["user_id"] = update.effective_user.id
        context.user_data["mention_markdown"] = update.effective_user.mention_markdown()

        donations_table.insert_one(context.user_data)
        update.message.reply_text(context.bot.lang_dict["thank_donation"], markup=markup)
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


DONATE_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=DonationBot().start_donation,
                             pattern=r'pay_donation'),
    ],
    states={
        # DONATION_MESSAGE: [MessageHandler(callback=DonationBot().donation_message,
        #                                   filters=Filters.text,
        #                                   pass_user_data=True),
        #                    CallbackQueryHandler(callback=DonationBot().back, pattern=r"help_back"),
        #                    CommandHandler('cancel', DonationBot().cancel)
        #                    ],
        EXECUTE_DONATION: [MessageHandler(callback=DonationBot().execute_donation,
                                          filters=Filters.text,
                                          pass_user_data=True)
                           ],

    },
    fallbacks=[CallbackQueryHandler(callback=DonationBot().back,
                                    pattern=r"help_back", pass_user_data=True),
               CallbackQueryHandler(callback=DonationBot().back,
                                    pattern=r"help_module", pass_user_data=True),
               MessageHandler(Filters.successful_payment,
                              DonationBot().successful_payment_callback,
                              pass_user_data=True),
               MessageHandler(filters=Filters.command, callback=DonationBot().back, pass_user_data=True),

               ])

HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(DonationBot().precheckout_callback)

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               DonationBot().successful_payment_callback)
