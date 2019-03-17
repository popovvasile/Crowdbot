# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import uuid
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, run_async, CallbackQueryHandler)
import logging
import datetime
from database import chats_table, chatbots_table
from modules.helper_funcs.auth import initiate_chat_id

# Enable logging
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TYPING_TOKEN, TYPING_TITLE, TYPING_DESCRIPTION, DONATION_FINISH = range(4)


class CreateDonationHandler(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_donation_create")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @staticmethod
    def facts_to_str(user_data):
        facts = list()

        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @run_async
    def start_create_donation(self, bot, update, user_data):
        chatbot = chatbots_table.find_one({"bot_id": bot.id}) or {}
        if "payment_token" in chatbot:
            update.message.reply_text("Please enter a title for your donation.\n"
                                      "If you want to change your donation provider token, "
                                      "please click /change_donation_token")

            update.message.reply_text("If you want to quit, click 'Back' ", reply_markup=self.reply_markup)
            return TYPING_TITLE
        else:
            update.message.reply_text("Please enter your donation provider token\n"
                                      "In order to get it,"
                                      "please visit https://core.telegram.org/bots/donations#getting-a-token")

            update.message.reply_text("If you want to quit, click 'Back' ", reply_markup=self.reply_markup)
            return TYPING_TOKEN

    @run_async
    def handle_token(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['payment_token'] = txt

        update.message.reply_text("Please enter a title for your donation", reply_markup=self.reply_markup)

        return TYPING_TITLE

    @run_async
    def handle_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['title'] = txt

        update.message.reply_text("Please write a short text for your donation- what your users have to pay for?",
                                  reply_markup=self.reply_markup)

        return TYPING_DESCRIPTION

    @run_async
    def handle_description(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["description"] = txt
        currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
        update.message.reply_text("Please choose the currency of your payment",
                                  reply_markup=ReplyKeyboardMarkup(currency_keyboard, one_time_keyboard=True))

        return DONATION_FINISH

    @run_async
    def handle_donation_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        currency = txt
        user_data["currency"] = currency
        bot.send_message(chat_id, "Your donation has been created!")
        chatbot = chatbots_table.find_one({"bot_id": bot.id}) or {}
        chatbot["donation"] = user_data
        chatbot["payment_token"] = user_data['payment_token']
        chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)
        user_data.clear()
        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def cancel(self, bot, update):
        get_help(bot, update)

        return ConversationHandler.END


# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY'


CREATE_DONATION_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('configure_donation', CreateDonationHandler().start_create_donation,
                                 pass_user_data=True)],
    # TYPING_TOKEN, TYPING_TITLE,  TYPING_DESCRIPTION, TYPING_AMOUNT, TYPING_CURRENCY,\
    # TYPING_TAGS, TYPING_TAGS_FINISH, TYPING_TYPE, TYPING_DEADLINE, TYPING_REPEAT
    states={
        TYPING_TOKEN: [MessageHandler(Filters.text,
                                      CreateDonationHandler().handle_token,
                                      pass_user_data=True),
                       CommandHandler('cancel', CreateDonationHandler().cancel)],
        TYPING_TITLE: [MessageHandler(Filters.text,
                                      CreateDonationHandler().handle_title,
                                      pass_user_data=True),
                       CommandHandler('cancel', CreateDonationHandler().cancel)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.text,
                                            CreateDonationHandler().handle_description,
                                            pass_user_data=True),
                             CommandHandler('cancel', CreateDonationHandler().cancel)],
        DONATION_FINISH: [MessageHandler(Filters.text,
                                         CreateDonationHandler().handle_donation_finish,
                                         pass_user_data=True),
                          CommandHandler('cancel', CreateDonationHandler().cancel)],
    },

    fallbacks=[
        MessageHandler(filters=Filters.command, callback=CreateDonationHandler().cancel),
        CallbackQueryHandler(callback=CreateDonationHandler().cancel, pattern=r"cancel_donation_create")]
)
