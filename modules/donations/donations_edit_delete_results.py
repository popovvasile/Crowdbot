# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
import logging
import requests
import json

from telegram import LabeledPrice
# Enable logging
from database import chatbots_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.main_runnner_helper import get_help
from helper_funcs.lang_strings.strings import string_dict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START, CHOOSING_ACTION, FINISH_ACTION, EDIT_PAYMENT, CHOOSING_EDIT_ACTION, \
TYPING_TITLE, TYPING_DESCRIPTION, TYPING_CURRENCY, \
TYPING_TOKEN, TYPING_TOKEN_FINISH, EDIT_FINISH, DOUBLE_CHECK_DELETE, DELETE_FINISH = range(13)


def check_provider_token(provider_token, bot, update):
    bot_token = chatbots_table.find_one({"bot_id": bot.id})["token"]
    prices = [LabeledPrice(string_dict(bot)["create_donation_str_1"], 10000)]
    data = requests.get("https://api.telegram.org/bot{}/sendInvoice".format(bot_token),
                        params=dict(title="test",
                                    description="test",
                                    payload="test",
                                    provider_token=provider_token,
                                    currency="USD",
                                    start_parameter="test",
                                    prices=json.dumps([p.to_dict() for p in prices]),
                                    chat_id=update.effective_chat.id))
    return json.loads(data.content)["ok"]


class EditPaymentHandler(object):

    @staticmethod
    def facts_to_str(user_data):
        facts = list()
        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    def start_donation(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id, )
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        if chatbot.get("donate") != {} and "donate" in chatbot:
            reply_keyboard = [[string_dict(bot)["edit_donation"]], [string_dict(bot)["delete_donation_button"]]]

            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["donations_edit_str_2"],
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")]]
            create_markup = InlineKeyboardMarkup(create_buttons)
            bot.send_message(update.callback_query.message.chat.id, string_dict(bot)["back_text"],
                             reply_markup=create_markup)

            return FINISH_ACTION
        else:
            admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                                   callback_data="allow_donation"),
                              InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                   callback_data="help_module(shop)")]
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["allow_donation_text"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            user_data.clear()
            return ConversationHandler.END

    def handle_action_finish(self, bot, update, user_data):  # TODO add if elifs for every action
        chat_id, txt = initiate_chat_id(update)
        if txt == string_dict(bot)["delete_donation_button"]:

            user_data['action'] = txt
            reply_keyboard = [[string_dict(bot)["donations_edit_str_3"]], [string_dict(bot)["donations_edit_str_4"]]]
            update.message.reply_text(
                string_dict(bot)["donations_edit_str_5"],
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")]]
            create_markup = InlineKeyboardMarkup(create_buttons)
            bot.send_message(chat_id, string_dict(bot)["back_text"],
                             reply_markup=create_markup)

            return DELETE_FINISH

        elif txt == string_dict(bot)["edit_donation"]:
            keyboard_markup = [[string_dict(bot)["title_button"], string_dict(bot)["description_button"]],
                               [string_dict(bot)["currency_button"], string_dict(bot)["payment_token_button"]]]
            chat_id, txt = initiate_chat_id(update)
            bot.send_message(chat_id, string_dict(bot)["donations_edit_str_6"],
                             reply_markup=ReplyKeyboardMarkup(keyboard_markup))
            create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")]]
            create_markup = InlineKeyboardMarkup(create_buttons)
            bot.send_message(chat_id, string_dict(bot)["back_text"],
                             reply_markup=create_markup)

            return CHOOSING_EDIT_ACTION

    def handle_edit_action_finish(self, bot, update, user_data):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        chat_id, txt = initiate_chat_id(update)
        user_data['edit_action'] = txt
        if txt == string_dict(bot)["title_button"]:
            bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())
            bot.send_message(chat_id,
                             string_dict(bot)["donations_edit_str_7"],
                             reply_markup=reply_markup)
        elif txt == string_dict(bot)["description_button"]:
            bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())

            update.message.reply_text(
                string_dict(bot)["donations_edit_str_8"],
                reply_markup=reply_markup)
        elif txt == string_dict(bot)["currency_button"]:
            bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())

            currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
            update.message.reply_text(string_dict(bot)["donations_edit_str_9"],
                                      reply_markup=ReplyKeyboardMarkup(currency_keyboard,
                                                                       one_time_keyboard=True))
            # payment_token_button
        elif txt == string_dict(bot)["payment_token_button"]:
            bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())
            update.message.reply_text(
                string_dict(bot)["donations_edit_str_12"],
                reply_markup=reply_markup)

        user_data["action"] = txt


        return EDIT_FINISH

    def handle_edit_finish(self, bot, update, user_data):  # TODO double check
        finish_buttons = list()
        finish_buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")])
        finish_markup = InlineKeyboardMarkup(
            finish_buttons)

        chat_id, txt = initiate_chat_id(update)
        if user_data["action"] == string_dict(bot)["title_button"]:
            user_data['title'] = txt
        if user_data["action"] == string_dict(bot)["description_button"]:
            user_data["description"] = txt
        if user_data["action"] == string_dict(bot)["currency_button"]:
            user_data["currency"] = txt
        if user_data["action"] == string_dict(bot)["payment_token_button"]:
            if check_provider_token(provider_token=txt, bot=bot, update=update):
                chatbot = chatbots_table.find_one({"bot_id": bot.id}) or {}

                chatbot["donate"]["payment_token"] = txt
                chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)
                update.message.reply_text(string_dict(bot)["donations_edit_str_13"],
                                          reply_markup=finish_markup)

                logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
                    update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
                return ConversationHandler.END
            else:
                update.message.reply_text(
                    string_dict(bot)["donations_edit_str_14"],
                    reply_markup=finish_markup)

                return TYPING_TOKEN

        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        chatbot["donate"].update(user_data)
        chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)
        update.message.reply_text(string_dict(bot)["donations_edit_str_10"], reply_markup=finish_markup)

        logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
        user_data.clear()

        return ConversationHandler.END

    def handle_finish_delete(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if txt == string_dict(bot)["donations_edit_str_3"]:
            chatbot = chatbots_table.find_one({"bot_id": bot.id})
            chatbot["donate"] = {}
            chatbots_table.replace_one({"bot_id": bot.id}, chatbot)
            logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
                update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
            create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")]]
            create_markup = InlineKeyboardMarkup(create_buttons)
            update.message.reply_text(string_dict(bot)["donations_edit_str_11"],
                                      reply_markup=create_markup)

            user_data.clear()
            return ConversationHandler.END
        elif txt == string_dict(bot)["donations_edit_str_4"]:
            create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")]]
            create_markup = InlineKeyboardMarkup(create_buttons)
            update.message.reply_text(string_dict(bot)["back_text"],
                                      reply_markup=create_markup)
            user_data.clear()
            return ConversationHandler.END

    # def change_donation_token(self, bot, update, user_data):
    #     buttons = list()
    #     buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
    #                                          callback_data="help_back")])
    #     reply_markup = InlineKeyboardMarkup(
    #         buttons)
    #     update.message.reply_text(
    #         string_dict(bot)["donations_edit_str_12"], reply_markup=reply_markup
    #     )
    #     return TYPING_TOKEN

    def change_donation_token_finish(self, bot, update, user_data):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(buttons)
        chat_id, txt = initiate_chat_id(update)
        if check_provider_token(provider_token=txt, bot=bot, update=update):
            chatbot = chatbots_table.find_one({"bot_id": bot.id}) or {}

            chatbot["donate"]["payment_token"] = txt
            chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)
            update.message.reply_text(string_dict(bot)["donations_edit_str_13"],
                                      reply_markup=reply_markup)
            create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")]]
            create_markup = InlineKeyboardMarkup(create_buttons)
            bot.send_message(update.callback_query.message.chat.id, string_dict(bot)["back_text"],
                             reply_markup=create_markup)

            logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
                update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
            return ConversationHandler.END
        else:
            update.message.reply_text(
                string_dict(bot)["donations_edit_str_14"],
                reply_markup=reply_markup)

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
                                       pass_user_data=True)],
        CHOOSING_EDIT_ACTION: [MessageHandler(Filters.text,
                                              EditPaymentHandler().handle_edit_action_finish,
                                              pass_user_data=True)],

        TYPING_TOKEN: [MessageHandler(Filters.text,
                                      EditPaymentHandler().change_donation_token_finish,
                                      pass_user_data=True)],
        # TYPING_TOKEN_FINISH: [MessageHandler(Filters.text,
        #                                      EditPaymentHandler().change_donation_token_finish,
        #                                      pass_user_data=True)],
        DELETE_FINISH: [MessageHandler(Filters.text,
                                       EditPaymentHandler().handle_finish_delete,
                                       pass_user_data=True)],
        EDIT_FINISH: [MessageHandler(Filters.text,
                                     EditPaymentHandler().handle_edit_finish,
                                     pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=EditPaymentHandler().back, pattern=r"help_back"),
        CallbackQueryHandler(callback=EditPaymentHandler().back, pattern=r"help_module"),

    ]
)
