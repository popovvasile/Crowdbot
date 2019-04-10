# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, run_async,
                          CallbackQueryHandler)
import logging
import requests  # TODO
import json

from telegram import LabeledPrice
# Enable logging
from database import chatbots_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START, CHOOSING_ACTION, FINISH_ACTION, EDIT_PAYMENT, CHOOSING_EDIT_ACTION, \
TYPING_TITLE, TYPING_DESCRIPTION, TYPING_CURRENCY, \
TYPING_TOKEN, TYPING_TOKEN_FINISH, EDIT_FINISH, DOUBLE_CHECK_DELETE, DELETE_FINISH = range(13)


def check_provider_token(provider_token, bot_id):
    bot_token = chatbots_table.find_one({"bot_id": bot_id})["token"]
    prices = [LabeledPrice("Test payment, Please ignore this message", 10000)]
    data = requests.get("https://api.telegram.org/bot{}/sendInvoice".format(bot_token),

                        params=dict(title="test",
                                    description="test",
                                    payload="test",
                                    provider_token=provider_token,
                                    currency="USD",
                                    start_parameter="test",
                                    prices=json.dumps([p.to_dict() for p in prices]),
                                    chat_id=244356086))
    return json.loads(data.content)["ok"]


class EditPaymentHandler(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_donation_edit")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @staticmethod
    def facts_to_str(user_data):
        facts = list()
        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @run_async
    def start_donation(self, bot, update, user_data):

        reply_keyboard = [["Delete this donation"], ["Edit"]]
        update.message.reply_text(
            "What do you want to do with this donation?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return FINISH_ACTION

    def handle_action_finish(self, bot, update, user_data):  # TODO add if leifs for every action
        chat_id, txt = initiate_chat_id(update)
        if txt == "Delete this donation":
            user_data['action'] = txt
            return DOUBLE_CHECK_DELETE
        elif txt == "Edit":
            user_data['action'] = txt
            return EDIT_PAYMENT

    @run_async
    def handle_edit_action(self, bot, update, user_data):
        keyboard_markup = [["Title", "Description"],
                           ["Currency"]]
        chat_id, txt = initiate_chat_id(update)
        bot.send_message(chat_id, "Please choose what exactly do you want to edit",
                         reply_markup=ReplyKeyboardMarkup(keyboard_markup))
        return CHOOSING_EDIT_ACTION

    def handle_edit_action_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['edit_action'] = txt
        if txt == "Title":
            bot.send_message(chat_id,
                             "Please write a new title for this donation", reply_markup=self.reply_markup)
            return TYPING_TITLE
        elif txt == "Description":
            update.message.reply_text(
                "Please write a short text for your donation- what your users have to pay for?",
                reply_markup=self.reply_markup)
            return TYPING_DESCRIPTION
        elif txt == "Currency":
            currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
            update.message.reply_text("Please choose the currency of your donation",
                                      reply_markup=ReplyKeyboardMarkup(currency_keyboard, one_time_keyboard=True))
            return TYPING_CURRENCY

    @run_async
    def handle_currency(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        currency = txt
        user_data["currency"] = currency

        return EDIT_FINISH

    @run_async
    def handle_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['title'] = txt
        return EDIT_FINISH

    @run_async
    def handle_description(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["description"] = txt

        return EDIT_FINISH

    @run_async
    def handle_edit_finish(self, bot, update, user_data):  # TODO double check
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        chatbot["donation"] = user_data
        chatbots_table.replace_one({"bot_id": bot.id}, chatbot)
        update.message.reply_text("Your donation has been updated", reply_markup=self.reply_markup)

        user_data.clear()
        return ConversationHandler.END

    @run_async
    def handle_delete_double_check(self, bot, update, user_data):
        reply_keyboard = [["Yes, I am sure"], ["No, let's get back"]]
        update.message.reply_text(
            "Are you sure that you want to delete this donation?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return DELETE_FINISH

    @run_async
    def handle_finish_delete(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if txt == "Yes, I am sure":
            user_data['action'] = "delete"
            return ConversationHandler.END
        elif txt == "No, let's get back":
            return CHOOSING_ACTION

    @run_async
    def change_donation_token(self, bot, update):

        update.message.reply_text(
            "Please enter your new donation provider token", reply_markup=self.reply_markup
        )
        return TYPING_TOKEN

    @run_async
    def change_donation_token_finish(self, bot, update):

        chat_id, txt = initiate_chat_id(update)
        if check_provider_token(provider_token=txt, bot_id=bot.id):
            chatbot = chatbots_table.find_one({"bot_id": bot.id})
            chatbots_table.update_one(chatbot, chatbot.update({"donation_token": txt}))
            update.message.reply_text("Thank you! Your provider_token was changed successfully !",
                                      reply_markup=self.reply_markup)
            return ConversationHandler.END
        else:
            update.message.reply_text(
                "Your provider token is wrong. Please check your provider token and send it again",
                reply_markup=self.reply_markup)

            return TYPING_TOKEN

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

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


EDIT_DONATION_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('edit_donation', EditPaymentHandler().start_donation, pass_user_data=True)],

    states={
        TYPING_TOKEN: [MessageHandler(Filters.text,
                                      EditPaymentHandler().change_donation_token,
                                      pass_user_data=True),
                       CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_TOKEN_FINISH: [MessageHandler(Filters.text,
                                             EditPaymentHandler().change_donation_token_finish,
                                             pass_user_data=True),
                              CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_TITLE: [MessageHandler(Filters.text,
                                      EditPaymentHandler().handle_title,
                                      pass_user_data=True),
                       CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.text,
                                            EditPaymentHandler().handle_description,
                                            pass_user_data=True),
                             CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_CURRENCY: [MessageHandler(Filters.text,
                                         EditPaymentHandler().handle_currency,
                                         pass_user_data=True),
                          CommandHandler('cancel', EditPaymentHandler().cancel)],

        DOUBLE_CHECK_DELETE: [MessageHandler(Filters.text,
                                             EditPaymentHandler().handle_delete_double_check,
                                             pass_user_data=True),
                              CommandHandler('cancel', EditPaymentHandler().cancel)],
    },

    fallbacks=[
        CommandHandler('cancel', EditPaymentHandler().cancel),
        CallbackQueryHandler(callback=EditPaymentHandler().back, pattern=r"cancel_donation_edit"),
        MessageHandler(filters=Filters.command, callback=EditPaymentHandler().back)]
)