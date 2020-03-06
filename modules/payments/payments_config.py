# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging
import telegram

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)

from database import chatbots_table, products_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.helper import get_help, check_provider_token
from helper_funcs.misc import delete_messages
from modules.shop.admin_side.welcome import Welcome
from modules.shop.helper.keyboards import back_btn

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START, CHOOSING_ACTION, FINISH_ACTION, EDIT_PAYMENT, CHOOSING_EDIT_ACTION, \
    TYPING_TITLE, TYPING_DESCRIPTION, TYPING_CURRENCY, \
    TYPING_TOKEN, TYPING_TOKEN_FINISH, EDIT_FINISH, \
    DOUBLE_CHECK_DELETE, DELETE_FINISH, CURRENCY_FINISH = range(14)


class EnableDisableShopDonations(object):
    def payments_configs(self, update, context):
        delete_messages(update, context, True)
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
        delete_messages(update, context, True)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
        admin_keyboard = []
        if chatbot["donations_enabled"] is True:
            admin_keyboard.append(
                [InlineKeyboardButton(text=context.bot.lang_dict["disable_donations_button"],
                                      callback_data="change_donations_config")]),
            admin_keyboard.append(
                [InlineKeyboardButton(text=context.bot.lang_dict["change_payment_token"],
                                      callback_data="edit_change_donation_payment_token")]),
            admin_keyboard.append(
                [InlineKeyboardButton(text=context.bot.lang_dict["change_donation_greeting"],
                                      callback_data="edit_change_donation_description")]),
            admin_keyboard.append(
                [InlineKeyboardButton(text=context.bot.lang_dict["change_donation_currency"],
                                      callback_data="edit_change_donation_currency")]),
        else:
            admin_keyboard.append(
                [InlineKeyboardButton(text=context.bot.lang_dict["allow_donations_button"],
                                      callback_data="change_donations_config")]),

        admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                    callback_data="help_module(shop)")])
        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["payments_config_text"],
                                 reply_markup=InlineKeyboardMarkup(admin_keyboard))
        return ConversationHandler.END

    def config_shop(self, update, context):
        if update.callback_query:
            update_data = update.callback_query
        else:
            update_data = update
        try:
            context.bot.delete_message(chat_id=update_data.message.chat_id,
                                       message_id=update_data.message.message_id)
        except telegram.error.BadRequest:
            pass
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})

        if chatbot["shop"]["shop_type"] == "online":
            payment_token_text = "change_payment_token"
            antitype = "offline_shop"
        else:
            payment_token_text = "add_payment_token"
            antitype = "online_shop"

        if chatbot["shop"]["shipping"] is False:
            admin_keyboard = [
                [InlineKeyboardButton(text=context.bot.lang_dict["change_shop_address_button"],
                                      callback_data="edit_change_shop_address")]]
            anti_shipping_text = "to customer delivery"
        else:
            admin_keyboard = []
            anti_shipping_text = "self-delivery"

        if chatbot["shop_enabled"] is True and "shop" in chatbot:
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["disable_shop_button"],
                callback_data="change_shop_config")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["edit_change_shop_type"].format(antitype.split("_")[0]),
                callback_data="edit_change_shop_type")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict[payment_token_text],
                callback_data="edit_change_shop_payment_token")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict[anti_shipping_text],
                callback_data="edit_change_shop_shipping")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["change_donation_greeting"],
                callback_data="edit_change_shop_description")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["change_donation_currency"],
                callback_data="edit_change_shop_currency")]),
        else:
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["allow_shop_button"],
                callback_data="change_shop_config")]),

        admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                    callback_data="back_to_main_menu")])
        context.bot.send_message(update_data.message.chat.id,
                                 context.bot.lang_dict["payments_config_text"],
                                 reply_markup=InlineKeyboardMarkup(admin_keyboard))
        return ConversationHandler.END

    def enable_shop(self, update, context):
        delete_messages(update, context, True)
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
        delete_messages(update, context, True)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
        admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                               callback_data="help_module(shop)")]
        chatbot["donations_enabled"] = not (chatbot["donations_enabled"])
        chatbots_table.update({"bot_id": context.bot.id}, chatbot)
        if chatbot["donations_enabled"]:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict[
                                         "payments_config_text_donations_enabled"])
            self.config_donations(update, context)

        else:
            context.bot.send_message(
                update.callback_query.message.chat.id,
                context.bot.lang_dict["payments_config_text_donations_disabled"],
                reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        return


CONFIGS_DONATIONS_GENERAL = CallbackQueryHandler(
    callback=EnableDisableShopDonations().config_donations,
    pattern="donations_config")
CONFIGS_SHOP_GENERAL = CallbackQueryHandler(
    callback=EnableDisableShopDonations().config_shop,
    pattern="shop_config")
PAYMENTS_CONFIG_KEYBOARD = CallbackQueryHandler(
    callback=EnableDisableShopDonations().payments_configs,
    pattern="payments_config")
CHANGE_SHOP_CONFIG = CallbackQueryHandler(
    pattern="change_shop_config",
    callback=EnableDisableShopDonations().enable_shop)
CHANGE_DONATIONS_CONFIG = CallbackQueryHandler(
    pattern="change_donations_config",
    callback=EnableDisableShopDonations().enable_donations)


class EditPaymentHandler(object):

    def handle_edit_action_finish(self, update, context):
        delete_messages(update, context, True)

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

                currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["KZT", "UAH", "RON", "PLN"]]
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
                    context.user_data["to_delete"].append(update.message.reply_text(
                        context.bot.lang_dict["payments_current_description"].format(
                            chatbot["shop"]["description"])))

                context.user_data["to_delete"].append(update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_8"],
                    reply_markup=reply_markup))
            elif "currency" in data:

                context.user_data["action"] = "currency"

                if "currency" in chatbot["shop"]:
                    context.user_data["to_delete"].append(update.message.reply_text(
                        context.bot.lang_dict["payments_current_payments"]
                            .format(chatbot["shop"]["currency"]),
                        reply_markup=reply_markup))

                currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["KZT", "UAH", "RON", "PLN"]]
                context.user_data["to_delete"].append(
                    update.message.reply_text(
                        context.bot.lang_dict["donations_edit_str_9"],
                        reply_markup=ReplyKeyboardMarkup(currency_keyboard,
                                                         one_time_keyboard=True)))
            elif "address" in data:
                context.user_data["action"] = "address"
                if "address" in chatbot["shop"]:
                    context.user_data["to_delete"].append(update.message.reply_text(
                        context.bot.lang_dict["payments_change_address"]
                            .format(chatbot["shop"]["address"]),
                        reply_markup=reply_markup))

                context.user_data["to_delete"].append(update.message.reply_text(
                    context.bot.lang_dict["create_shop_str_9"],
                    reply_markup=reply_markup))

            elif "payment_token" in data:
                context.user_data["action"] = "payment_token"
                context.user_data["to_delete"].append(update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_12"],
                    reply_markup=reply_markup))
            elif "shipping" in data:
                chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
                chatbot["shop"].update({"shipping": not (chatbot["shop"]["shipping"])})
                if "address" in chatbot["shop"]:
                    if chatbot["shop"]["shipping"]:
                        context.user_data["to_delete"].append(update.message.reply_text(
                            context.bot.lang_dict["create_shop_str_12"],
                            reply_markup=reply_markup))
                    else:
                        context.user_data["to_delete"].append(update.message.reply_text(
                            context.bot.lang_dict["create_shop_str_10"],
                            reply_markup=reply_markup))
                    chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
                    return ConversationHandler.END
                else:
                    context.user_data["action"] = "address"
                    context.user_data["to_delete"].append(update.message.reply_text(
                        context.bot.lang_dict["create_shop_str_9"],
                        reply_markup=reply_markup))

            elif "type" in data:
                chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
                if chatbot["shop"]["shop_type"] == "online":
                    shoptype = "offline"
                else:
                    shoptype = "online"

                if shoptype == "online" and "payment_token" not in chatbot["shop"]:
                    context.user_data["action"] = "payment_token"
                    context.user_data["to_delete"].append(update.message.reply_text(
                        context.bot.lang_dict["donations_edit_str_12"],
                        reply_markup=reply_markup))

                else:
                    context.user_data["to_delete"].append(update.message.reply_text(
                        context.bot.lang_dict["create_shop_str_11"].format(shoptype)))
                    chatbot["shop"].update({"shop_type": shoptype})
                    chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
                    context.user_data["to_delete"].append(
                        context.bot.send_message(
                            chat_id, context.bot.lang_dict["great_text"],
                            reply_markup=reply_markup))
                    return ConversationHandler.END

            return EDIT_FINISH

    def handle_edit_finish(self, update, context):
        finish_markup = InlineKeyboardMarkup(
            [[back_btn("back_to_main_menu_btn", context=context)]])

        chat_id, txt = initiate_chat_id(update)
        update_dict = {}
        if context.user_data["action"] == "description":
            update_dict["description"] = txt
        if context.user_data["action"] == "address":
            update_dict["address"] = txt

        if context.user_data["action"] == "currency":
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})

            update_dict["currency"] = txt
            context.user_data["currency"] = txt
            from currency_converter import CurrencyConverter
            c = CurrencyConverter()
            converted = c.convert(1, chatbot["shop"]["currency"], txt)
            keyboard_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["yes"],
                                   callback_data="change_currency_finish_YES")],
             [InlineKeyboardButton(text=context.bot.lang_dict["no"],
                                   callback_data="change_currency_finish_NO")],
             [back_btn("back_to_main_menu_btn", context=context)]])

            context.user_data["to_delete"].append(update.message.reply_text(
                context.bot.lang_dict["payments_currency_change"].format(
                    chatbot["shop"]["currency"], txt, chatbot["shop"]["currency"],
                    str(round(converted * 1, 2)), txt
                ), reply_markup=keyboard_markup))
            context.user_data["converted"] = converted
            return CURRENCY_FINISH

        if context.user_data["action"] == "payment_token":
            update_dict["payment_token"] = txt
            update_dict["shop_type"] = context.user_data["shop_type"]
            if check_provider_token(provider_token=txt, update=update, context=context):
                if context.user_data["target"] == "donations":
                    chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
                    chatbot["donate"].update(update_dict)
                    context.user_data["to_delete"].append(
                        update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"],
                                              reply_markup=finish_markup))
                    chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})

                elif context.user_data["target"] == "shop":
                    chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
                    chatbot["shop"].update(update_dict)
                    chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
                    context.user_data["to_delete"].append(
                        update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"],
                                              reply_markup=finish_markup))

                logger.info("Admin {} on bot {}:{} did  the following edit on shop: {}".format(
                    update.effective_user.first_name, context.bot.first_name, context.bot.id,
                    context.user_data["action"]))
                return ConversationHandler.END
            else:
                context.user_data["to_delete"].append(update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_14"],
                    reply_markup=finish_markup))

                return EDIT_FINISH
        if context.user_data["target"] == "donations":
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
            chatbot["donate"].update(update_dict)
            context.user_data["to_delete"].append(
                update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"],
                                      reply_markup=finish_markup))
            chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})

        elif context.user_data["target"] == "shop":
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
            chatbot["shop"].update(update_dict)
            chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
            context.user_data["to_delete"].append(
                update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"],
                                      reply_markup=finish_markup))

        logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id,
            context.user_data["action"]))
        delete_messages(update, context)
        context.user_data.clear()

        return ConversationHandler.END

    def change_currency_finish(self, update, context):
        converted = context.user_data["converted"]
        if "YES" in update.callback_query.data:
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
            chatbot["shop"]["currency"] = context.user_data["currency"]
            chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
            products_table.update_many(
                {"bot_id": context.bot.id},
                {"$mul": {"price": converted,
                          "discount_price": converted}})
            products_table.update_many(
                {"bot_id": context.bot.id},
                {"$set": { "$round": ["$price", 2]}})
            products_table.update_many(
                {"bot_id": context.bot.id},
                {"$set": {"$round": ["$discount_price", 2]}})
            delete_messages(update, context)
            update.callback_query.message.reply_text(
                context.bot.lang_dict["payments_currency_has_changed"])
            EnableDisableShopDonations().config_shop(update=update, context=context)
        else:
            EnableDisableShopDonations().config_shop(update=update, context=context)

        logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id,
            context.user_data["action"]))

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
        delete_messages(update, context, True)
        get_help(update, context)
        return ConversationHandler.END


EDIT_DONATION_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=EditPaymentHandler().handle_edit_action_finish,
                             pattern=r'edit_change_')
    ],

    states={
        EDIT_FINISH: [
            CallbackQueryHandler(callback=Welcome().back_to_main_menu,
                                 pattern=r"back_to_main_menu_btn"),
            CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_back"),
            CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_module"),
            MessageHandler(Filters.text, EditPaymentHandler().handle_edit_finish)
        ],
        CURRENCY_FINISH: [
            CallbackQueryHandler(callback=EditPaymentHandler().change_currency_finish,
                                 pattern=r"change_currency_finish"),
            CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_back"),
            CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_module"),

        ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=Welcome().back_to_main_menu,
                             pattern=r"back_to_main_menu_btn"),
        CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_back"),
        CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_module"),

    ]
)
