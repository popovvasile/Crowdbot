# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import requests  # TODO
import json

from telegram import LabeledPrice
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler,
                          run_async, CallbackQueryHandler)
import logging
from database import chats_table, chatbots_table
from modules.helper_funcs.auth import initiate_chat_id

# Enable logging
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TYPING_TOKEN, TYPING_TITLE, TYPING_DESCRIPTION, DONATION_FINISH = range(4)


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
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        if "donate" in chatbot:
            if "payment_token" in chatbot["donate"]:
                bot.send_message(update.callback_query.message.chat.id,
                                 "Please enter a title for your donation", reply_markup=self.reply_markup)
                return TYPING_TITLE
            else:
                bot.send_message(update.callback_query.message.chat.id,
                                 "Please enter your donation provider token\n"
                                 """
"1st Step: Go to @botfather and enter /mybots. Choose your bot and press “Payments”. Choose a provider. \n" +
        "We advise to use „Stripe“ because of low Acquiring comisson for European card. \n" +
        "2nd Step: Authorize yourself in the chatbot of the chosen provider. Just follow instructions then you will get a token-access, that you should copy.\n" +
        "3nd Step :Go back to your bot and create /newdonate. Paste your token, choose the currency, and minimal donation. \n" +

[Telegram's tutorial](https://core.telegram.org/bots/payments#getting-a-token)""",
                                 parse_mode='Markdown', reply_markup=self.reply_markup)
                return TYPING_TOKEN
        else:
            bot.send_message(update.callback_query.message.chat.id,
                             "Please enter your donation provider token\n"
                             "1st Step: Go to @botfather and enter /mybots. Choose your bot and press “Payments”. Choose a provider. \n" +
                             "We advise to use „Stripe“ because of low Acquiring comisson for European card. \n" +
                             "2nd Step: Authorize yourself in the chatbot of the chosen provider. Just follow instructions then you will get a token-access, that you should copy.\n" +
                             "3nd Step :Go back to your bot and create /newdonate. Paste your token, choose the currency, and minimal donation. \n"
                             """
 +
       
[Telegram's tutorial](https://core.telegram.org/bots/payments#getting-a-token)""", parse_mode='Markdown',
                             reply_markup=self.reply_markup)
            return TYPING_TOKEN

    @run_async
    def handle_token(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if check_provider_token(provider_token=txt, bot_id=bot.id):

            user_data['payment_token'] = txt

            update.message.reply_text("Enter a title for your donation", reply_markup=self.reply_markup)

            return TYPING_TITLE
        else:
            update.message.reply_text(
                "Your provider token is wrong. Please check your provider token and send it again",
                reply_markup=self.reply_markup)

        return TYPING_TOKEN

    @run_async
    def handle_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['title'] = txt

        update.message.reply_text("Write a short text for your donation campaign- what your users are donating for?",
                                  reply_markup=self.reply_markup)

        return TYPING_DESCRIPTION

    @run_async
    def handle_description(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["description"] = txt
        currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
        update.message.reply_text("Now, Choose the currency of your payment",
                                  reply_markup=ReplyKeyboardMarkup(currency_keyboard, one_time_keyboard=True))

        return DONATION_FINISH

    @run_async
    def handle_donation_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        currency = txt
        user_data["currency"] = currency
        bot.send_message(chat_id,
                         "Congratulation! You can get payments from your audience.\n"
                         "Do not forget to remind them of this.")  # TODO add button send donation request and back
        chatbot = chatbots_table.find_one({"bot_id": bot.id}) or {}

        print(user_data)
        if 'payment_token' not in user_data:
            # chatbot["donate"]["payment_token"] = user_data['payment_token']
            user_data["payment_token"] = chatbot["donate"]["payment_token"]
        chatbot["donate"] = user_data
        chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)

        logger.info("Admin {} on bot {}:{} added a donation config:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["title"]))
        user_data.clear()
        get_help(bot, update)
        return ConversationHandler.END

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
                           message_id=update.callback_query.message.message_id, )
        get_help(bot, update)
        return ConversationHandler.END


# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY'


CREATE_DONATION_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=CreateDonationHandler().start_create_donation,
                                       pass_user_data=True,
                                       pattern=r'allow_donation'),
                  ],
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

    fallbacks=[CallbackQueryHandler(callback=CreateDonationHandler().back, pattern=r"cancel_donation_create"),
               MessageHandler(filters=Filters.command, callback=CreateDonationHandler().back),
               ]
)
