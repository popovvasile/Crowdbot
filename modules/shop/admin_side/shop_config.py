# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import requests
import telegram
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, ParseMode)
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from config import conf
from helper_funcs.constants import MIN_ADDRESS_LENGTH, MAX_ADDRESS_LENGTH
from logs import logger
from database import chatbots_table, products_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.helper import (get_help, check_provider_token,
                                 currency_limits_dict, boolmoji, answer_callback_query)
from helper_funcs.misc import delete_messages
from modules.shop.admin_side.welcome import Welcome
from modules.shop.helper.keyboards import back_btn, currency_markup

(START, CHOOSING_ACTION, FINISH_ACTION, EDIT_PAYMENT, CHOOSING_EDIT_ACTION,
 TYPING_TITLE, TYPING_DESCRIPTION, TYPING_CURRENCY,
 TYPING_TOKEN, TYPING_TOKEN_FINISH, EDIT_FINISH,
 DOUBLE_CHECK_DELETE, DELETE_FINISH, CURRENCY_FINISH,
 TYPING_SHOP_ADDRESS) = range(15)


class EnableDisableShopDonations(object):
    def config_shop(self, update, context):
        if update.callback_query:
            update_data = update.callback_query
        else:
            update_data = update
        delete_messages(update, context)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
        context.user_data["delivery"] = chatbot["shop"]["delivery"]
        context.user_data["pick_up"] = chatbot["shop"]["pick_up"]
        text = context.bot.lang_dict

        delivery_callback = "edit_change_delivery_false" if context.user_data["delivery"] \
            else "edit_change_delivery_true"
        pick_up_callback = "edit_change_pick_up_false" if context.user_data["pick_up"] \
            else "edit_change_pick_up_true"

        if chatbot["shop"]["shop_type"] == "online":
            payment_token_text = "change_payment_token"
            antitype = "offline_shop"
        else:
            payment_token_text = "add_payment_token"
            antitype = "online_shop"

        if chatbot["shop"]["delivery"] is False:
            admin_keyboard = [
                [InlineKeyboardButton(text=context.bot.lang_dict["change_shop_address_button"],
                                      callback_data="edit_change_shop_address")]]
        else:
            admin_keyboard = []

        if chatbot["shop_enabled"] is True and "shop" in chatbot and chatbot["premium"]:
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["disable_shop_button"],
                callback_data="change_shop_config")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["edit_change_shop_type"].format(antitype.split("_")[0]),
                callback_data="edit_change_shop_type")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["edit_change_shipping_fee"].format(antitype.split(
                    "_")[0]),
                callback_data="edit_change_shipping_fee")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict[payment_token_text],
                callback_data="edit_change_shop_payment_token")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=f'{boolmoji(context.user_data["delivery"])} {text["delivery"]}',
                callback_data=delivery_callback)])
            admin_keyboard.append([InlineKeyboardButton(
                    text=f'{boolmoji(context.user_data["pick_up"])} {text["pick_up"]}',
                    callback_data=pick_up_callback)])
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["change_donation_greeting"],
                callback_data="edit_change_shop_description")]),
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["change_donation_currency"],
                callback_data="edit_change_shop_currency")])
        elif chatbot["premium"]:
            admin_keyboard.append([InlineKeyboardButton(
                text=context.bot.lang_dict["allow_shop_button"],
                callback_data="change_shop_config")]),
        else:
            admin_keyboard.append(
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["buy_subscription"],
                    url='tg://{}?start={}'.format(
                        conf.CROWDBOT_USERNAME,
                        "buy_premium_{}".format(
                            str(context.bot.id))
                    ))])

        admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                    callback_data="help_module(shop)")])
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
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.callback_query.message.chat.id,
                    context.bot.lang_dict["payments_config_text_shop_enabled"]))

            self.config_shop(update, context)
        else:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["payments_config_text_shop_disabled"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        return


CONFIGS_SHOP_GENERAL = CallbackQueryHandler(
    callback=EnableDisableShopDonations().config_shop,
    pattern="shop_config")

CHANGE_SHOP_CONFIG = CallbackQueryHandler(
    pattern="change_shop_config",
    callback=EnableDisableShopDonations().enable_shop)


class EditPaymentHandler(object):

    def handle_edit_action_finish(self, update, context):
        delete_messages(update, context, True)

        reply_markup = InlineKeyboardMarkup([[back_btn("shop_config", context=context)]])
        update = update.callback_query
        data = update.data
        chat_id = update.message.chat_id
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})

        context.user_data["target"] = "shop"
        if "shipping_fee" in data:
            context.user_data["action"] = "delivery_fee"
            if "delivery_fee" in chatbot["shop"]:
                context.user_data["to_delete"].append(update.message.reply_text(
                    context.bot.lang_dict["payments_current_delivery_fee"].format(
                        chatbot["shop"]["delivery_fee"],
                        chatbot["shop"]["currency"]
                    )))
            context.user_data["to_delete"].append(update.message.reply_text(
                context.bot.lang_dict["donations_edit_str_8"],
                reply_markup=reply_markup))

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
            text = context.bot.lang_dict["payments_current_payments"].format(chatbot["shop"][
                                                                                 "currency"]) + \
                   "\n" + context.bot.lang_dict["donations_edit_str_9"]
            context.user_data["to_delete"].append(
                update.message.reply_text(
                    text,
                    reply_markup=currency_markup(context)))

        elif "address" in data:
            context.user_data["action"] = "address"
            text = context.bot.lang_dict["create_shop_str_9"]
            if "address" in chatbot["shop"]:
                text += "\n" + context.bot.lang_dict["payments_change_address"].format(
                    chatbot["shop"]["address"])

            context.user_data["to_delete"].append(
                update.message.reply_text(text, reply_markup=reply_markup))

        elif "payment_token" in data:
            context.user_data["action"] = "payment_token"
            context.user_data["to_delete"].append(update.message.reply_text(
                context.bot.lang_dict["payments_guide"]
                + "\n\n"
                + context.bot.lang_dict["donations_edit_str_12"],
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup))
        elif "delivery" in data or "pick_up" in data:
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
            if "delivery_true" in data and not context.user_data["delivery"]:
                chatbot["shop"]["delivery"] = True
            elif "delivery_false" in data:
                chatbot["shop"]["delivery"] = False
            if "pick_up_true" in data:
                chatbot["shop"]["pick_up"] = True
            elif "pick_up_false" in data:
                chatbot["shop"]["pick_up"] = False
            if not chatbot["shop"]["pick_up"] and not chatbot["shop"]["delivery"]:
                chatbot["shop"]["pick_up"] = False
                chatbot["shop"]["delivery"] = True

            if "address" in chatbot["shop"]:
                if chatbot["shop"]["delivery"]:
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
                chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
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
                    context.bot.lang_dict["payments_guide"]
                    + "\n\n"
                    + context.bot.lang_dict["donations_edit_str_12"],
                    parse_mode=ParseMode.HTML,
                    reply_markup=reply_markup))
            else:
                chatbot["shop"].update({"shop_type": shoptype})
                chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
                context.user_data["to_delete"].append(
                    context.bot.send_message(
                        chat_id, context.bot.lang_dict["create_shop_str_11"].format(shoptype),
                        reply_markup=reply_markup))
                return

        return EDIT_FINISH

    def handle_edit_finish(self, update, context):
        delete_messages(update, context)
        finish_markup = InlineKeyboardMarkup(
            [[back_btn("shop_config", context=context)]])
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
        chat_id, txt = initiate_chat_id(update)
        update_dict = {}
        if context.user_data["action"] == "delivery_fee":
            update_dict["delivery_fee"] = float(txt)
        if context.user_data["action"] == "description":
            update_dict["description"] = txt

        if context.user_data["action"] == "address":
            if len(txt) < MIN_ADDRESS_LENGTH:
                context.user_data["to_delete"].append(
                    context.bot.send_message(update.effective_chat.id,
                                             context.bot.lang_dict["short_address"]
                                             + context.bot.lang_dict["create_shop_str_9"],
                                             reply_markup=finish_markup))
                return EDIT_FINISH
            elif len(txt) > MAX_ADDRESS_LENGTH:
                context.user_data["to_delete"].append(
                    context.bot.send_message(update.effective_chat.id,
                                             context.bot.lang_dict["long_address"]
                                             + context.bot.lang_dict["create_shop_str_9"],
                                             reply_markup=finish_markup))
                return EDIT_FINISH
            update_dict["address"] = txt
        if context.user_data["action"] == "currency":
            if update.callback_query is None:
                context.user_data["action"] = "currency"
                text = context.bot.lang_dict["payments_current_payments"].format(chatbot["shop"][
                                                                                     "currency"]) + \
                       "\n" + context.bot.lang_dict["donations_edit_str_9"]
                context.user_data["to_delete"].append(
                    update.message.reply_text(
                        text,
                        reply_markup=currency_markup(context)))
                return EDIT_FINISH
            currency = update.callback_query.data.replace("currency/", "")
            if chatbot["shop"]["shop_type"] == "online":
                check = check_provider_token(provider_token=chatbot["shop"]["payment_token"],
                                             update=update, context=context,
                                             currency=currency)
            else:
                check = (True, "All good")
            if check[0]:
                update_dict["currency"] = currency
                context.user_data["currency"] = currency

                url = 'https://prime.exchangerate-api.com/v5/d50bf30b0f53baa26ac17d80/latest/'
                url += chatbot["shop"]["currency"]

                # Making our request
                converted = float(requests.get(url).json()["conversion_rates"][currency])

                keyboard_markup = InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text=context.bot.lang_dict["yes"],
                                           callback_data="change_currency_finish_YES")],
                     [InlineKeyboardButton(text=context.bot.lang_dict["no"],
                                           callback_data="change_currency_finish_NO")],
                     [back_btn("shop_config", context=context)]])

                context.user_data["to_delete"].append(update.callback_query.message.reply_text(
                    context.bot.lang_dict["payments_currency_change"].format(
                        chatbot["shop"]["currency"], str(round(converted * 100, 2)), currency),
                    reply_markup=keyboard_markup,
                    parse_mode=ParseMode.HTML))
                context.user_data["converted"] = converted
                return CURRENCY_FINISH
            else:
                context.user_data["to_delete"].append(update.message.reply_text(
                    context.bot.lang_dict["donations_edit_str_14"].format(check[1]),
                    reply_markup=finish_markup))
                return EDIT_FINISH

        if context.user_data["action"] == "payment_token":
            update_dict["payment_token"] = txt
            update_dict["shop_type"] = "online"
            check = check_provider_token(provider_token=txt, update=update,
                                         context=context, currency=chatbot["shop"]["currency"])
            if check[0]:
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
                    context.bot.lang_dict["donations_edit_str_14"].format(check[1]),
                    reply_markup=finish_markup))

                return EDIT_FINISH
        chatbot["shop"].update(update_dict)
        chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})
        context.user_data["to_delete"].append(
            update.message.reply_text(context.bot.lang_dict["donations_edit_str_10"],
                                      reply_markup=finish_markup))

        logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id,
            context.user_data["action"]))
        context.user_data.clear()

        return ConversationHandler.END

    def change_currency_finish(self, update, context):
        converted = context.user_data["converted"]
        context.bot.delete_message(update.effective_chat.id,
                                   update.effective_message.message_id)
        if "YES" in update.callback_query.data:
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
            chatbot["shop"]["currency"] = context.user_data["currency"]
            chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot})

            products_table.update_many(
                {"bot_id": context.bot.id},
                {"$mul": {"price": converted,
                          "discount_price": converted}})
            all_products = products_table.find({"bot_id": context.bot.id})
            # stupid solution, couldn't find anything inside
            # the pymongo framework which would make it easy
            # old solution below (does not work)
            currency = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]["currency"]
            currency_limits = currency_limits_dict[currency]
            for prod in all_products:
                try:
                    assert currency_limits["min"] < float(prod["price"]) < currency_limits[
                        "max"]
                except AssertionError:
                    if float(prod["price"]) > currency_limits["max"]:
                        prod["price"] = currency_limits["max"]
                    else:
                        prod["price"] = currency_limits["min"]
                products_table.update_one(
                    {"_id": prod["_id"]},
                    {"$set": {"price": round(prod["price"], 2),
                              "discount_price": round(prod["discount_price"], 2)}})
            delete_messages(update, context)
            update.callback_query.message.reply_text(
                context.bot.lang_dict["payments_currency_has_changed"],
                reply_markup=InlineKeyboardMarkup([[back_btn("shop_config", context)]]))
        else:
            EnableDisableShopDonations().config_shop(update=update, context=context)

        logger.info("Admin {} on bot {}:{} did  the following edit on donation: {}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id,
            context.user_data["action"]))

        context.user_data.clear()

        return ConversationHandler.END

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


EDIT_SHOP_HANDLER = ConversationHandler(
    allow_reentry=True,
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
            CallbackQueryHandler(callback=EditPaymentHandler().handle_edit_finish,
                                 pattern=r"currency/"),
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
        CallbackQueryHandler(callback=EnableDisableShopDonations().config_shop,
                             pattern=r"shop_config"),
        CallbackQueryHandler(callback=Welcome().back_to_main_menu,
                             pattern=r"back_to_main_menu_btn"),
        CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_back"),
        CallbackQueryHandler(callback=Welcome().back_to_main_menu, pattern=r"help_module"),

    ]
)
