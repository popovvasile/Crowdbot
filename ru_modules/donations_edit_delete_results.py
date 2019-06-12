# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, run_async,
                          CallbackQueryHandler)
import logging
import requests  # TODO
import json

from telegram import LabeledPrice
# Enable logging
from database import chatbots_table
from ru_modules.helper_funcs.auth import initiate_chat_id
from ru_modules.helper_funcs.helper import get_help
from ru_modules.helper_funcs.strings import donations_edit_str_1, back_button, menu_button, donations_edit_str_2, \
    allow_donations_button, allow_donation_text, delete_donation_button, edit_button, donations_edit_str_4, \
    donations_edit_str_3, donations_edit_str_5, title_button, description_button, currency_button, donations_edit_str_6, \
    great_text, donations_edit_str_7, donations_edit_str_8, donations_edit_str_9, donations_edit_str_10, \
    donations_edit_str_11, donations_edit_str_12, donations_edit_str_13, donations_edit_str_14

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START, CHOOSING_ACTION, FINISH_ACTION, EDIT_PAYMENT, CHOOSING_EDIT_ACTION, \
TYPING_TITLE, TYPING_DESCRIPTION, TYPING_CURRENCY, \
TYPING_TOKEN, TYPING_TOKEN_FINISH, EDIT_FINISH, DOUBLE_CHECK_DELETE, DELETE_FINISH = range(13)


def check_provider_token(provider_token, bot_id):
    bot_token = chatbots_table.find_one({"bot_id": bot_id})["token"]
    prices = [LabeledPrice(donations_edit_str_1, 10000)]
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
        buttons.append([InlineKeyboardButton(text=back_button, callback_data="cancel_donation_edit")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)
        finish_buttons = list()
        finish_buttons.append([InlineKeyboardButton(text=menu_button, callback_data="help_back")])
        self.finish_markup = InlineKeyboardMarkup(
            finish_buttons)

    @staticmethod
    def facts_to_str(user_data):
        facts = list()
        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @run_async
    def start_donation(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id, )
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        if chatbot.get("donate") != {} and "donate" in chatbot:
            reply_keyboard = [[delete_donation_button], [edit_button]]

            bot.send_message(update.callback_query.message.chat.id,
                             donations_edit_str_2,
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

            return FINISH_ACTION
        else:
            admin_keyboard = [InlineKeyboardButton(text=allow_donations_button, callback_data="allow_donation"),
                              InlineKeyboardButton(text=back_button, callback_data="help_back")]
            bot.send_message(update.callback_query.message.chat.id,
                             allow_donation_text,
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            user_data.clear()
            return ConversationHandler.END

    def handle_action_finish(self, bot, update, user_data):  # TODO add if leifs for every action

        chat_id, txt = initiate_chat_id(update)
        if txt == delete_donation_button:

            user_data['action'] = txt
            reply_keyboard = [[donations_edit_str_3], [donations_edit_str_4]]
            update.message.reply_text(
                donations_edit_str_5,
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return DELETE_FINISH

        elif txt == edit_button:
            keyboard_markup = [[title_button, description_button],
                               [currency_button]]
            chat_id, txt = initiate_chat_id(update)
            bot.send_message(chat_id, donations_edit_str_6,
                             reply_markup=ReplyKeyboardMarkup(keyboard_markup))
            return CHOOSING_EDIT_ACTION

    def handle_edit_action_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['edit_action'] = txt
        if txt == title_button:
            bot.send_message(chat_id, great_text, reply_markup=ReplyKeyboardRemove())
            bot.send_message(chat_id,
                             donations_edit_str_7,
                             reply_markup=self.reply_markup)
        elif txt == description_button:
            bot.send_message(chat_id, great_text, reply_markup=ReplyKeyboardRemove())

            update.message.reply_text(
                donations_edit_str_8,
                reply_markup=self.reply_markup)
        elif txt == currency_button:
            bot.send_message(chat_id, great_text, reply_markup=ReplyKeyboardRemove())

            currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
            update.message.reply_text(donations_edit_str_9,
                                      reply_markup=ReplyKeyboardMarkup(currency_keyboard,
                                                                       one_time_keyboard=True))
        user_data["action"] = txt
        return EDIT_FINISH

    @run_async
    def handle_edit_finish(self, bot, update, user_data):  # TODO double check
        chat_id, txt = initiate_chat_id(update)
        if user_data["action"] == title_button:
            user_data['title'] = txt

        if user_data["action"] == description_button:
            user_data["description"] = txt

        if user_data["action"] == currency_button:
            user_data["currency"] = txt
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        chatbot["donate"].update(user_data)
        chatbots_table.replace_one({"bot_id": bot.id}, chatbot)
        update.message.reply_text(donations_edit_str_10, reply_markup=self.finish_markup)

        logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
        user_data.clear()

        return ConversationHandler.END

    @run_async
    def handle_finish_delete(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if txt == donations_edit_str_3:
            chatbot = chatbots_table.find_one({"bot_id": bot.id})
            chatbot["donate"] = {}
            chatbots_table.replace_one({"bot_id": bot.id}, chatbot)
            update.message.reply_text(donations_edit_str_11)
            logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
                update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
            get_help(bot, update)
            user_data.clear()
            return ConversationHandler.END
        elif txt == donations_edit_str_4:
            chat_id, txt = initiate_chat_id(update)
            if txt == delete_donation_button:
                user_data['action'] = txt
                reply_keyboard = [[donations_edit_str_3], [donations_edit_str_4]]
                update.message.reply_text(
                    donations_edit_str_5,
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
                return DELETE_FINISH

            elif txt == edit_button:
                user_data['action'] = txt
                return EDIT_PAYMENT

    @run_async
    def change_donation_token(self, bot, update, user_data):
        update.message.reply_text(
            donations_edit_str_12, reply_markup=self.reply_markup
        )
        return TYPING_TOKEN

    @run_async
    def change_donation_token_finish(self, bot, update, user_data):

        chat_id, txt = initiate_chat_id(update)
        if check_provider_token(provider_token=txt, bot_id=bot.id):
            chatbot = chatbots_table.find_one({"bot_id": bot.id}) or {}

            chatbot["donate"]["payment_token"] = txt
            chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)
            update.message.reply_text(donations_edit_str_13,
                                      reply_markup=self.reply_markup)
            get_help(bot, update)
            logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
                update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
            return ConversationHandler.END
        else:
            update.message.reply_text(
                donations_edit_str_14,
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
    entry_points=[
        CallbackQueryHandler(callback=EditPaymentHandler().start_donation,
                             pass_user_data=True,
                             pattern=r'configure_donation')
    ],

    states={
        FINISH_ACTION: [MessageHandler(Filters.text,
                                       EditPaymentHandler().handle_action_finish,
                                       pass_user_data=True),
                        CommandHandler('cancel', EditPaymentHandler().cancel)],
        CHOOSING_EDIT_ACTION: [MessageHandler(Filters.text,
                                              EditPaymentHandler().handle_edit_action_finish,
                                              pass_user_data=True),
                               CommandHandler('cancel', EditPaymentHandler().cancel)],

        TYPING_TOKEN: [MessageHandler(Filters.text,
                                      EditPaymentHandler().change_donation_token,
                                      pass_user_data=True),
                       CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_TOKEN_FINISH: [MessageHandler(Filters.text,
                                             EditPaymentHandler().change_donation_token_finish,
                                             pass_user_data=True),
                              CommandHandler('cancel', EditPaymentHandler().cancel)],
        DELETE_FINISH: [MessageHandler(Filters.text,
                                       EditPaymentHandler().handle_finish_delete,
                                       pass_user_data=True),
                        CommandHandler('cancel', EditPaymentHandler().cancel)],
        EDIT_FINISH: [MessageHandler(Filters.text,
                                     EditPaymentHandler().handle_edit_finish,
                                     pass_user_data=True),
                      CommandHandler('cancel', EditPaymentHandler().cancel)],

    },

    fallbacks=[
        CommandHandler('cancel', EditPaymentHandler().cancel),
        CallbackQueryHandler(callback=EditPaymentHandler().back, pattern=r"cancel_donation_edit"),
        MessageHandler(filters=Filters.command, callback=EditPaymentHandler().back)]
)
