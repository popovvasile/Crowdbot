# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import uuid
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, run_async)
import logging
import datetime
from database import chats_table, chatbots_table
from modules.helper_funcs.auth import initiate_chat_id

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TYPING_TOKEN, TYPING_TITLE, TYPING_DESCRIPTION, DONATION_FINISH = range(4)


class CreateDonationHandler(object):
    @staticmethod
    def facts_to_str(user_data):
        facts = list()

        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @run_async
    def start_create_donation(self, bot, update, user_data):
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        if "payment_token" in chatbot:
            update.message.reply_text("Please enter a title for your donation.\n"
                                      "If you want to change your donation provider token, "
                                      "please click /change_donation_token")
            return TYPING_TITLE
        else:
            update.message.reply_text("Please enter your donation provider token"
                                      "In order to get it,"
                                      "please visit https://core.telegram.org/bots/donations#getting-a-token")
            return TYPING_TOKEN

    @run_async
    def handle_token(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        # chatbot = chatbots_table.find_one({"bot_id": bot.id})
        # if not "payment_token" in chatbot:
        user_data['payment_token'] = txt
        update.message.reply_text("Please enter a title for your donation")
        return TYPING_TITLE

    @run_async
    def handle_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['title'] = txt
        update.message.reply_text("Please write a short text for your donation- what your users have to pay for?")
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
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        chatbot["donation"] = user_data
        chatbot["payment_token"] = user_data['payment_token']
        chatbots_table.replace_one({"bot_id": bot.id}, chatbot)
        user_data.clear()
        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def cancel(self, bot, update):
        update.message.reply_text("Command is finished. Until next time!")
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
        MessageHandler(filters=Filters.command, callback=CreateDonationHandler().cancel)]
)
