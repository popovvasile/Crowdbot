# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)

from database import chatbots_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.constants import MIN_ADDRESS_LENGTH, MAX_ADDRESS_LENGTH
from helper_funcs.helper import get_help, boolmoji, answer_callback_query
from helper_funcs.misc import delete_messages
from logs import logger
from modules.shop.admin_side.welcome import Welcome
from modules.shop.helper.keyboards import currency_markup

(ASK_TOKEN, TYPING_TOKEN, TYPING_DESCRIPTION,
 TYPING_SHOP_ADDRESS, SHOP_FINISH, CHOOSING_PICK_UP_OR_DELIVERY,
 DELIVERY_FEE, ASK_CURRENCY, CHOOSING_SHIPPING) = range(9)


class CreateShopHandler(object):
    @staticmethod
    def facts_to_str(context):
        facts = list()

        for key, value in context.user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    def start_create_shop(self, update, context):
        text = context.bot.lang_dict

        if "to_delete" not in context.user_data:
            context.user_data["to_delete"] = []
        data = update.callback_query.data
        delete_messages(update, context, True)
        if "delivery" not in context.user_data:
            context.user_data["delivery"] = False
        if "pick_up" not in context.user_data:
            context.user_data["pick_up"] = False

        if "delivery_true" in data and not context.user_data["delivery"]:
            context.user_data["delivery"] = True
        elif "delivery_false" in data:
            context.user_data["delivery"] = False
        if "pick_up_true" in data and not context.user_data["pick_up"]:
            context.user_data["pick_up"] = True
        elif "pick_up_false" in data:
            context.user_data["pick_up"] = False

        delivery_str = "delivery_true" if context.user_data["delivery"] else "delivery_false"
        delivery_callback = "delivery_false" if context.user_data["delivery"] else "delivery_true"
        pick_up_str = "pick_up_true" if context.user_data["pick_up"] else "pick_up_false"
        pick_up_callback = "pick_up_false" if context.user_data["pick_up"] else "pick_up_true"

        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                text=f'{boolmoji(context.user_data["delivery"])} {text[delivery_str]}',
                callback_data=delivery_callback)],
                [InlineKeyboardButton(
                    text=f'{boolmoji(context.user_data["pick_up"])} {text[pick_up_str]}',
                    callback_data=pick_up_callback)],
                [InlineKeyboardButton(text=text['continue_button_text'],
                                      callback_data='agree_with_terms')],
                [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                      callback_data="help_module(shop)")]
            ]
        )
        context.user_data['checkbox_id'] = context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text["create_shop_str_13"],
            reply_markup=keyboard,
            disable_web_page_preview=True).message_id

        answer_callback_query(update)

        return CHOOSING_PICK_UP_OR_DELIVERY

    def handle_type(self, update, context):
        delete_messages(update, context, True)
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                   callback_data="help_module(shop)")]])

        if context.user_data["delivery"]:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.callback_query.message.chat_id,
                                         context.bot.lang_dict["create_shop_str_6"],
                                         reply_markup=reply_markup))
            return TYPING_DESCRIPTION
        elif context.user_data["pick_up"]:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.callback_query.message.chat_id,
                                         context.bot.lang_dict["create_shop_str_9"],
                                         reply_markup=reply_markup))
            return TYPING_SHOP_ADDRESS

    def handle_address(self, update, context):
        # delete_list = context.user_data["to_delete"]
        # delete_list.append(update.message)
        delete_messages(update, context, True)

        chat_id, txt = initiate_chat_id(update)
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                   callback_data="help_module(shop)")]])
        if len(txt) < MIN_ADDRESS_LENGTH:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         context.bot.lang_dict["short_address"]
                                         + context.bot.lang_dict["create_shop_str_9"],
                                         reply_markup=reply_markup))
            return TYPING_SHOP_ADDRESS
        elif len(txt) > MAX_ADDRESS_LENGTH:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         context.bot.lang_dict["long_address"]
                                         + context.bot.lang_dict["create_shop_str_9"],
                                         reply_markup=reply_markup))
            return TYPING_SHOP_ADDRESS

        context.user_data["address"] = txt
        context.user_data["to_delete"].append(update.message.reply_text(
            context.bot.lang_dict["create_shop_str_7"],
            reply_markup=currency_markup(context)))
        return SHOP_FINISH

    def handle_delivery_fee(self, update, context):
        delete_messages(update, context, True)
        chat_id, txt = initiate_chat_id(update)
        context.user_data["delivery_fee"] = float(txt)
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                   callback_data="help_module(shop)")]])

        if context.user_data["pick_up"]:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.message.chat_id,
                                         context.bot.lang_dict["create_shop_str_9"],
                                         reply_markup=reply_markup))
            return TYPING_SHOP_ADDRESS
        else:
            context.user_data["to_delete"].append(update.message.reply_text(
                context.bot.lang_dict["create_shop_str_7"],
                reply_markup=currency_markup(context)))
            return SHOP_FINISH

    def handle_description(self, update, context):
        delete_messages(update, context, True)
        chat_id, txt = initiate_chat_id(update)
        context.user_data["description"] = txt
        if context.user_data["delivery"] and "delivery_fee" not in context.user_data:
            context.user_data["to_delete"].append(update.message.reply_text(
                context.bot.lang_dict["create_shop_str_14"]))
            return DELIVERY_FEE
        else:
            context.user_data["to_delete"].append(update.message.reply_text(
                context.bot.lang_dict["create_shop_str_7"],
                reply_markup=currency_markup(context)))
            return SHOP_FINISH

    def handle_shop_finish(self, update, context):
        context.user_data["currency"] = update.callback_query.data.split("/")[1]
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id}) or {}
        context.user_data.pop("to_delete", None)
        chatbot["shop_enabled"] = True
        chatbot["shop"] = context.user_data
        chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot}, upsert=True)
        update.callback_query.answer(context.bot.lang_dict["create_shop_str_8"])
        logger.info("Admin {} on bot {}:{} added a shop config".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id))
        delete_messages(update, context, True)
        context.user_data.clear()
        Welcome.start(update, context)
        return ConversationHandler.END

    def cancel(self, update, context):
        update.message.reply_text("Command is cancelled =(")
        get_help(update, context)
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=update.effective_message.message_id)
        get_help(update, context)
        return ConversationHandler.END


CREATE_SHOP_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[CallbackQueryHandler(callback=CreateShopHandler().start_create_shop,
                                       pattern=r'allow_shop'),
                  ],
    states={
        DELIVERY_FEE: [MessageHandler(Filters.text,
                                      CreateShopHandler().handle_delivery_fee)],
        CHOOSING_PICK_UP_OR_DELIVERY: [
            CallbackQueryHandler(callback=CreateShopHandler().handle_type,
                                 pattern=r"agree_with_terms"),
            CallbackQueryHandler(callback=CreateShopHandler().start_create_shop,
                                 pattern=r"delivery"),
            CallbackQueryHandler(callback=CreateShopHandler().start_create_shop,
                                 pattern=r"pick_up")
        ],
        TYPING_SHOP_ADDRESS: [MessageHandler(Filters.text,
                                             CreateShopHandler().handle_address)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.text,
                                            CreateShopHandler().handle_description)],
        SHOP_FINISH: [CallbackQueryHandler(pattern=r"currency",
                                           callback=CreateShopHandler().handle_shop_finish)],
    },

    fallbacks=[CallbackQueryHandler(callback=CreateShopHandler().back, pattern=r"help_back"),
               CallbackQueryHandler(callback=CreateShopHandler().back, pattern=r"help_module"),
               MessageHandler(filters=Filters.command, callback=CreateShopHandler().back),
               ]
)
