# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import telegram
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
import logging
import requests
import json

from telegram import LabeledPrice
# Enable logging
from database import chatbots_table, products_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.helper import get_help
from modules.shop.admin_side.welcome import Welcome
from modules.shop.helper.keyboards import back_btn

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START, CHOOSING_ACTION, FINISH_ACTION, EDIT_PAYMENT, CHOOSING_EDIT_ACTION, \
TYPING_TITLE, TYPING_DESCRIPTION, TYPING_CURRENCY, \
TYPING_TOKEN, TYPING_TOKEN_FINISH, EDIT_FINISH, DOUBLE_CHECK_DELETE, DELETE_FINISH = range(13)


# TODO change type of shop in settings and instructions for payment

# def payment(self, update: Update, context: CallbackContext):
#     delete_messages(update, context, True)
#     context.bot.send_message(
#         chat_id=update.callback_query.message.chat_id,
#         text="Do you want to make this product with online payment, offline payment or both?",
#         reply_markup=InlineKeyboardMarkup([
#             [InlineKeyboardButton("Online payment",
#                                   callback_data="set_payment_online")],
#             [InlineKeyboardButton("Offline payment",
#                                   callback_data="set_payment_offline")],
#             [InlineKeyboardButton("Both options",
#                                   callback_data="set_payment_both")],
#             [back_btn("back_to_main_menu_btn", context=context)]
#         ]))
#     return PAYMENT
#
#
# def finish_payment(self, update: Update, context: CallbackContext):
#     delete_messages(update, context, True)
#     if "online" in update.callback_query.data:
#         context.user_data["product"].update(dict(online_payment=True))
#         context.user_data["product"].update(dict(offline_payment=False))
#     elif "offline" in update.callback_query.data:
#         context.user_data["product"].update(dict(online_payment=False))
#         context.user_data["product"].update(dict(offline_payment=True))
#     elif "both" in update.callback_query.data:
#         context.user_data["product"].update(dict(online_payment=True))
#         context.user_data["product"].update(dict(offline_payment=True))
#     return self.edit(update, context)
#


def check_provider_token(provider_token, update, context):
    bot_token = chatbots_table.find_one({"bot_id": context.bot.id})["token"]
    prices = [LabeledPrice(context.bot.lang_dict["create_donation_str_1"], 10000)]
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


class EnableDisableShopDonations(object):
    def payments_configs(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        admin_keyboard = [[InlineKeyboardButton(text=context.bot.lang_dict["donations"],
                                                callback_data="donations_config")],
                          [InlineKeyboardButton(text=context.bot.lang_dict["shop"],
                                                callback_data="shop_config")],
                          [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                callback_data="help_module(shop)")]]
        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["payments_config_text"],
                                 reply_markup=InlineKeyboardMarkup(admin_keyboard))

    def config_donations(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
        admin_keyboard = []
        if chatbot["donations_enabled"] is True:
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["disable_donations_button"],
                                                        callback_data="change_donations_config")]),
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["change_payment_token"],
                                                        callback_data="edit_change_donation_payment_token")]),
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["change_donation_greeting"],
                                                        callback_data="edit_change_donation_description")]),
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["change_donation_currency"],
                                                        callback_data="edit_change_donation_currency")]),
        else:
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["allow_donations_button"],
                                                        callback_data="change_donations_config")]),

        admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                    callback_data="help_module(shop)")])
        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["payments_config_text"],
                                 reply_markup=InlineKeyboardMarkup(admin_keyboard))
        return ConversationHandler.END

    def config_shop(self, update, context):
        try:
            context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                       message_id=update.callback_query.message.message_id)
        except telegram.error.BadRequest:
            pass
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})

        if chatbot["shop"]["shop_type"] == "online":
            payment_token_text = "change_payment_token"
            antitype = "offline_shop"
        else:
            payment_token_text = "add_payment_token"
            antitype = "online_shop"

        if chatbot["shop"]["shipping"] is True:
            admin_keyboard = [[InlineKeyboardButton(text=context.bot.lang_dict["change_shop_address_button"],
                                                    callback_data="edit_change_shop_address")]]
            anti_shipping_text = "self-delivery"
        else:
            admin_keyboard = []
            anti_shipping_text = "to customer delivery"

        if chatbot["shop_enabled"] is True and "shop" in chatbot:
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["disable_shop_button"],
                                                        callback_data="change_shop_config")]),

            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["edit_change_shop_type"]
                                                        .format(antitype.split("_")[0]),
                                                        callback_data="edit_change_shop_type")]),
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict[payment_token_text],
                                                        callback_data="edit_change_shop_payment_token")]),
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict[anti_shipping_text],
                                                        callback_data="edit_change_shop_shipping")]),

            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["change_donation_greeting"],
                                                        callback_data="edit_change_shop_description")]),
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["change_donation_currency"],
                                                        callback_data="edit_change_shop_currency")]),
        else:
            admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["allow_shop_button"],
                                                        callback_data="change_shop_config")]),

        admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                    callback_data="back_to_main_menu")])
        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["payments_config_text"],
                                 reply_markup=InlineKeyboardMarkup(admin_keyboard))
        return ConversationHandler.END

    def enable_shop(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
        admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                               callback_data="help_module(shop)")]
        chatbot["shop_enabled"] = not (chatbot["shop_enabled"])
        chatbots_table.update({"bot_id": context.bot.id}, chatbot)
        if chatbot["shop_enabled"]:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["payments_config_text_shop_enabled"])
            self.config_shop(update, context)
        else:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["payments_config_text_shop_disabled"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        return

    def enable_donations(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
        admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                               callback_data="help_module(shop)")]
        chatbot["donations_enabled"] = not (chatbot["donations_enabled"])
        chatbots_table.update({"bot_id": context.bot.id}, chatbot)
        if chatbot["donations_enabled"]:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["payments_config_text_donations_enabled"])
            self.config_donations(update, context)

        else:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["payments_config_text_donations_disabled"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        return


CONFIGS_DONATIONS_GENERAL = CallbackQueryHandler(callback=EnableDisableShopDonations().config_donations,
                                                 pattern="donations_config")
CONFIGS_SHOP_GENERAL = CallbackQueryHandler(callback=EnableDisableShopDonations().config_shop,
                                            pattern="shop_config")
PAYMENTS_CONFIG_KEYBOARD = CallbackQueryHandler(callback=EnableDisableShopDonations().payments_configs,
                                                pattern="payments_config")
CHANGE_SHOP_CONFIG = CallbackQueryHandler(pattern="change_shop_config",
                                          callback=EnableDisableShopDonations().enable_shop)
CHANGE_DONATIONS_CONFIG = CallbackQueryHandler(pattern="change_donations_config",
                                               callback=EnableDisableShopDonations().enable_donations)


class EditPaymentHandler(object):

    def handle_edit_action_finish(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)

        reply_markup = InlineKeyboardMarkup([[back_btn("back_to_main_menu_btn", context=context)]])
        update = update.callback_query
        data = update.data
        chat_id = update.message.chat_id
        if "donation" in data:
            context.user_data["target"] = "donations"
            if "description" in data:
                context.user_data["action"] = "description"
                context.bot.send_message(chat_id, context.bot.lang_dict["great_text"],
                                         reply_markup=ReplyKeyboardRemove())

                update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_8"],
                    reply_markup=reply_markup)
            elif "currency" in data:
                context.user_data["action"] = "currency"
                context.bot.send_message(chat_id, context.bot.lang_dict["great_text"],
                                         reply_markup=ReplyKeyboardRemove())

                currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
                update.message.reply_text(context.bot.lang_dict["donations_edit_str_9"],
                                          reply_markup=ReplyKeyboardMarkup(currency_keyboard,
                                                                           one_time_keyboard=True))
                # payment_token_button
            elif "payment_token" in data:
                context.user_data["action"] = "payment_token"
                context.bot.send_message(chat_id, context.bot.lang_dict["great_text"],
                                         reply_markup=ReplyKeyboardRemove())
                update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_12"],
                    reply_markup=reply_markup)

            return EDIT_FINISH
        # edit_change_shop_address
        # edit_change_shop_shipping

        if "shop" in data:
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})

            context.user_data["target"] = "shop"
            if "description" in data:
                context.user_data["action"] = "description"
                if "description" in chatbot["shop"]:
                    update.message.reply_text(
                        "Your current shop description is {}".format(chatbot["shop"]["description"]),
                        reply_markup=reply_markup)

                update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_8"],
                    reply_markup=reply_markup)
            elif "currency" in data:
                context.user_data["action"] = "currency"

                if "currency" in chatbot["shop"]:
                    update.message.reply_text(
                        "Your current currency is {}".format(chatbot["shop"]["currency"]),
                        reply_markup=reply_markup)

                currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
                update.message.reply_text(context.bot.lang_dict["donations_edit_str_9"],
                                          reply_markup=ReplyKeyboardMarkup(currency_keyboard,
                                                                           one_time_keyboard=True))
            elif "address" in data:
                context.user_data["action"] = "address"
                if "address" in chatbot["shop"]:
                    update.message.reply_text(
                        "Your current address is {}".format(chatbot["shop"]["address"]),
                        reply_markup=reply_markup)

                update.message.reply_text(
                    context.bot.lang_dict["create_shop_str_9"],
                    reply_markup=reply_markup)

            elif "payment_token" in data:
                context.user_data["action"] = "payment_token"
                update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_12"],
                    reply_markup=reply_markup)
            elif "shipping" in data:
                chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
                chatbot["shop"].update({"shipping": not (chatbot["shop"]["shipping"])})
                update.message.reply_text(
                    context.bot.lang_dict["create_shop_str_10"].format(str(not (chatbot["shop"]["shipping"]))),
                    reply_markup=reply_markup)
                chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
                return ConversationHandler.END
            elif "type" in data:
                chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
                if chatbot["shop"]["shop_type"] == "online":
                    shoptype = "offline"
                else:
                    shoptype = "online"

                if shoptype == "online" and "payment_token" not in chatbot["shop"]:
                    context.user_data["action"] = "payment_token"
                    update.message.reply_text(
                        context.bot.lang_dict["donations_edit_str_12"],
                        reply_markup=reply_markup)

                else:
                    update.message.reply_text(
                        context.bot.lang_dict["create_shop_str_11"].format(shoptype))
                    chatbot["shop"].update({"shop_type": shoptype})
                    chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
                    context.bot.send_message(chat_id, context.bot.lang_dict["great_text"],
                                             reply_markup=reply_markup)
                    return ConversationHandler.END

            return EDIT_FINISH

    def handle_edit_finish(self, update, context):

        finish_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                   callback_data="help_module(shop)")]])

        chat_id, txt = initiate_chat_id(update)
        update_dict = {}
        if context.user_data["action"] == "description":
            update_dict["description"] = txt
        if context.user_data["action"] == "currency":
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})

            update_dict["currency"] = txt
            from currency_converter import CurrencyConverter
            c = CurrencyConverter()
            converted = c.convert(1, chatbot["shop"]["currency"], txt)
            update.message.reply_text("All prices have been converted from {} to {}\n"
                                      "The current exchange rate is 100{}={}{}".format(
                chatbot["shop"]["currency"], txt, chatbot["shop"]["currency"], str(round(converted*100, 2)), txt
            ))
            # products_table.update({"bot_id": context.bot.id}, {}, multi=True)
            products_table.update_many(
                {"bot_id": context.bot.id},
                {"$mul": {"price": round(converted, 2),
                          "discount_price": round(converted, 2)}}
            )

        if context.user_data["action"] == "payment_token":
            update_dict["payment_token"] = txt
            if check_provider_token(provider_token=txt, update=update, context=context):
                if context.user_data["target"] == "donations":
                    chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
                    chatbot["donate"].update(update_dict)
                    update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"],
                                              reply_markup=finish_markup)
                    chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})

                elif context.user_data["target"] == "shop":
                    chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
                    chatbot["shop"].update(update_dict)
                    chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
                    update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"],
                                              reply_markup=finish_markup)

                logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
                    update.effective_user.first_name, context.bot.first_name, context.bot.id,
                    context.user_data["action"]))
                return ConversationHandler.END
            else:
                update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_14"],
                    reply_markup=finish_markup)

                return EDIT_FINISH
        if context.user_data["target"] == "donations":
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
            chatbot["donate"].update(update_dict)
            update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"], reply_markup=finish_markup)
            chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})

        elif context.user_data["target"] == "shop":
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
            chatbot["shop"].update(update_dict)
            chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
            update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"], reply_markup=finish_markup)

        logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, context.user_data["action"]))
        context.user_data.clear()

        return ConversationHandler.END

    @staticmethod
    def error(update, context, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

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
        return ConversationHandler.END


EDIT_DONATION_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=EditPaymentHandler().handle_edit_action_finish,
                             pattern=r'edit_change_')
    ],

    states={
        EDIT_FINISH: [
            CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"back_to_main_menu_btn"),
            CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_back"),
            CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_module"),
            MessageHandler(Filters.text, EditPaymentHandler().handle_edit_finish)
        ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"back_to_main_menu_btn"),
        CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_back"),
        CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_module"),

    ]
)
