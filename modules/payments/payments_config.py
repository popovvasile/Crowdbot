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
from helper_funcs.helper import get_help
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


# TODO enable/diasble shop/donations


class EnableDisableShopDonations(object):
    def payments_configs(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        admin_keyboard = [[InlineKeyboardButton(text=string_dict(bot)["donations"],
                                                callback_data="donations_config")],
                          [InlineKeyboardButton(text=string_dict(bot)["shop"],
                                                callback_data="shop_config")],
                          [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(settings)")]]
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["payments_config_text"],
                         reply_markup=InlineKeyboardMarkup(admin_keyboard))

    def config_donations(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        admin_keyboard = []
        if chatbot["donations_enabled"] is True:
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["disable_donations_button"],
                                                        callback_data="change_donations_config")]),
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["change_payment_token"],
                                                        callback_data="edit_change_donation_payment_token")]),
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["change_donation_greeting"],
                                                        callback_data="edit_change_donation_description")]),
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["change_donation_currency"],
                                                        callback_data="edit_change_donation_currency")]),
        elif "donations" in chatbot:
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                                        callback_data="change_donations_config")]),
        else:
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                                        callback_data='allow_donations')])

        admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(settings)")])
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["payments_config_text"],
                         reply_markup=InlineKeyboardMarkup(admin_keyboard))
        return ConversationHandler.END

    def config_shop(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        admin_keyboard = []
        if chatbot["shop_enabled"] is True and "shop" in chatbot:
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["disable_shop_button"],
                                                        callback_data="change_shop_config")]),
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["change_payment_token"],
                                                        callback_data="edit_change_shop_payment_token")]),
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["change_donation_greeting"],
                                                        callback_data="edit_change_shop_description")]),
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["change_donation_currency"],
                                                        callback_data="edit_change_shop_currency")]),
        elif "shop" in chatbot:
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["allow_shop_button"],
                                                        callback_data="change_shop_config")]),
        else:
            admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["allow_shop_button"],
                                                        callback_data='allow_shop')])
        admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(settings)")])
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["payments_config_text"],
                         reply_markup=InlineKeyboardMarkup(admin_keyboard))
        return ConversationHandler.END

    def enable_shop(self, bot, update):  # TODO ask token if there is none
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                               callback_data="help_module(settings)")]
        chatbot["shop_enabled"] = not (chatbot["shop_enabled"])
        chatbots_table.update({"bot_id": bot.id}, chatbot)
        if chatbot["shop_enabled"]:
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["payments_config_text_shop_enabled"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        else:
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["payments_config_text_shop_disabled"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        return

    def enable_donations(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                               callback_data="help_module(settings)")]
        chatbot["donations_enabled"] = not (chatbot["donations_enabled"])
        chatbots_table.update({"bot_id": bot.id}, chatbot)
        if chatbot["donations_enabled"]:
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["payments_config_text_donations_enabled"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        else:
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["payments_config_text_donations_disabled"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        return


CONFIGS_DONATIONS_GENERAL = CallbackQueryHandler(callback=EnableDisableShopDonations().config_donations,
                                                 pattern="donations_config")
CONFIGS_SHOP_GENERAL = CallbackQueryHandler(callback=EnableDisableShopDonations().config_shop,
                                            pattern="shop_config")
PAYMENTS_CONFIG_KEYBOARD = CallbackQueryHandler(callback=EnableDisableShopDonations().payments_configs,
                                                pattern="payments_config")
CHNAGE_SHOP_CONFIG = CallbackQueryHandler(pattern="change_shop_config",
                                          callback=EnableDisableShopDonations().enable_shop)
CHNAGE_DONATIONS_CONFIG = CallbackQueryHandler(pattern="change_donations_config",
                                               callback=EnableDisableShopDonations().enable_donations)


class EditPaymentHandler(object):  # TODO change as a payment config, not donation

    def handle_edit_action_finish(self, bot, update, user_data):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(settings)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        update = update.callback_query
        data = update.data
        chat_id = update.message.chat_id
        if "donation" in data:
            user_data["target"] = "donations"
            if "description" in data:
                user_data["action"] = "description"
                bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())

                update.message.reply_text(
                    string_dict(bot)["donations_edit_str_8"],
                    reply_markup=reply_markup)
            elif "currency" in data:
                user_data["action"] = "currency"
                bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())

                currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
                update.message.reply_text(string_dict(bot)["donations_edit_str_9"],
                                          reply_markup=ReplyKeyboardMarkup(currency_keyboard,
                                                                           one_time_keyboard=True))
                # payment_token_button
            elif "payment_token" in data:
                user_data["action"] = "payment_token"
                bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())
                update.message.reply_text(
                    string_dict(bot)["donations_edit_str_12"],
                    reply_markup=reply_markup)

            return EDIT_FINISH

        if "shop" in data:
            user_data["target"] = "shop"
            if "description" in data:
                user_data["action"] = "description"
                bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())

                update.message.reply_text(
                    string_dict(bot)["donations_edit_str_8"],
                    reply_markup=reply_markup)
            elif "currency" in data:
                user_data["action"] = "currency"
                bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())

                currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
                update.message.reply_text(string_dict(bot)["donations_edit_str_9"],
                                          reply_markup=ReplyKeyboardMarkup(currency_keyboard,
                                                                           one_time_keyboard=True))
                # payment_token_button
            elif "payment_token" in data:
                user_data["action"] = "payment_token"
                bot.send_message(chat_id, string_dict(bot)["great_text"], reply_markup=ReplyKeyboardRemove())
                update.message.reply_text(
                    string_dict(bot)["donations_edit_str_12"],
                    reply_markup=reply_markup)

            return EDIT_FINISH

    def handle_edit_finish(self, bot, update, user_data):  # TODO double check
        finish_buttons = list()
        finish_buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(settings)")])
        finish_markup = InlineKeyboardMarkup(
            finish_buttons)

        chat_id, txt = initiate_chat_id(update)
        update_dict = {}
        if user_data["action"] == "description":
            update_dict["description"] = txt
        if user_data["action"] == "currency":
            update_dict["currency"] = txt
        if user_data["action"] == "payment_token":
            update_dict["payment_token"] = txt
            if check_provider_token(provider_token=txt, bot=bot, update=update):
                if user_data["target"] == "donations":
                    chatbot = chatbots_table.find_one({"bot_id": bot.id})
                    chatbot["donate"].update(update_dict)
                    update.message.reply_text(string_dict(bot)["donations_edit_str_10"], reply_markup=finish_markup)
                    chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)

                elif user_data["target"] == "shop":
                    chatbot = chatbots_table.find_one({"bot_id": bot.id})
                    chatbot["shop"].update(update_dict)
                    chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)
                    update.message.reply_text(string_dict(bot)["donations_edit_str_10"], reply_markup=finish_markup)

                logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
                    update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
                return ConversationHandler.END
            else:
                update.message.reply_text(
                    string_dict(bot)["donations_edit_str_14"],
                    reply_markup=finish_markup)

                return EDIT_FINISH
        if user_data["target"] == "donations":
            chatbot = chatbots_table.find_one({"bot_id": bot.id})
            chatbot["donate"].update(update_dict)
            update.message.reply_text(string_dict(bot)["donations_edit_str_10"], reply_markup=finish_markup)
            chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)

        elif user_data["target"] == "shop":
            chatbot = chatbots_table.find_one({"bot_id": bot.id})
            chatbot["shop"].update(update_dict)
            chatbots_table.update_one({"bot_id": bot.id}, {'$set': chatbot}, upsert=True)
            update.message.reply_text(string_dict(bot)["donations_edit_str_10"], reply_markup=finish_markup)

        logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["action"]))
        user_data.clear()

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
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END


EDIT_DONATION_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=EditPaymentHandler().handle_edit_action_finish,
                             pass_user_data=True,
                             pattern=r'edit_change_')
    ],

    states={

        EDIT_FINISH: [MessageHandler(Filters.text,
                                     EditPaymentHandler().handle_edit_finish,
                                     pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=EditPaymentHandler().back, pattern=r"help_back"),
        CallbackQueryHandler(callback=EditPaymentHandler().back, pattern=r"help_module"),

    ]
)
