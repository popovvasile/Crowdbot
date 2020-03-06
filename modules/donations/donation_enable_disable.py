# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)

from database import chatbots_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.helper import get_help, check_provider_token

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TYPING_TOKEN, TYPING_DESCRIPTION, DONATION_FINISH = range(3)


def donation_menu(update, context):
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
    chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
    admin_keyboard = []
    if chatbot["donations_enabled"] is True:
        no_channel_keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["ask_donation_button"],
                                   callback_data="send_donation_to_users")],
             [InlineKeyboardButton(text=context.bot.lang_dict["configure_button"],
                                   callback_data="donations_config")],
             [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                   callback_data="help_module(shop)")],
             ]
        )
        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["donations"], reply_markup=no_channel_keyboard)
        return ConversationHandler.END
    elif "donations" in chatbot:
        admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["allow_donations_button"],
                                                    callback_data="change_donations_config")]),
    else:
        admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["allow_donations_button"],
                                                    callback_data="allow_donations")]),
    admin_keyboard.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                callback_data="help_module(shop)")])
    context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["shop"], reply_markup=InlineKeyboardMarkup(admin_keyboard))
    return ConversationHandler.END


class CreateDonationHandler(object):
    @staticmethod
    def facts_to_str(context):
        facts = list()

        for key, value in context.user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    def start_create_donation(self, update, context):
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                  callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        chatbot = chatbots_table.find_one({"bot_id": context.bot.id}) or {}
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        if "donate" in chatbot:
            if "payment_token" in chatbot["donate"]:
                context.bot.send_message(update.callback_query.message.chat.id,
                                         context.bot.lang_dict["create_donation_str_4"], reply_markup=reply_markup)

                return TYPING_DESCRIPTION
            else:
                context.bot.send_message(update.callback_query.message.chat.id,
                                         context.bot.lang_dict["create_donation_str_3"],
                                         reply_markup=reply_markup)
                return TYPING_TOKEN
        else:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["create_donation_str_3"],
                                     reply_markup=reply_markup)
            return TYPING_TOKEN

    def handle_token(self, update, context):
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                  callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        chat_id, txt = initiate_chat_id(update)
        if check_provider_token(provider_token=txt, update=update, context=context):

            context.user_data['payment_token'] = txt

            update.message.reply_text(context.bot.lang_dict["create_donation_str_4"],
                                      reply_markup=reply_markup)

            return TYPING_DESCRIPTION
        else:
            update.message.reply_text(
                context.bot.lang_dict["create_donation_str_5"],
                reply_markup=reply_markup)

        return TYPING_TOKEN

    def handle_description(self, update, context):
        chat_id, txt = initiate_chat_id(update)
        context.user_data["description"] = txt
        currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["KZT", "UAH", "RON", "PLN"]]
        update.message.reply_text(context.bot.lang_dict["create_donation_str_7"],
                                  reply_markup=ReplyKeyboardMarkup(currency_keyboard,
                                                                   one_time_keyboard=True))

        return DONATION_FINISH

    def handle_donation_finish(self, update, context):

        create_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["send_donation_request_button"],
                                                callback_data="send_donation_to_users")],
                          [InlineKeyboardButton(text=context.bot.lang_dict["send_donation_to_channel"],
                                                callback_data="send_donation_to_channel")],
                          [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                callback_data="help_module(shop)")]]
        create_markup = InlineKeyboardMarkup(
            create_buttons)

        chat_id, txt = initiate_chat_id(update)
        currency = txt
        context.user_data["currency"] = currency

        context.bot.send_message(chat_id,
                                 context.bot.lang_dict["create_donation_str_8"],
                                 reply_markup=create_markup)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id}) or {}

        context.user_data.pop("to_delete", None)
        if 'payment_token' not in context.user_data:
            # chatbot["donate"]["payment_token"] = user_data['payment_token']
            context.user_data["payment_token"] = chatbot["donate"]["payment_token"]
        chatbot["donate"] = context.user_data
        chatbot["donations_enabled"] = True
        chatbots_table.update_one({"bot_id": context.bot.id}, {'$set': chatbot}, upsert=True)

        logger.info("Admin {} on bot {}:{} added a donation config:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id,
            context.user_data["description"]))
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
                                   message_id=update.callback_query.message.message_id, )
        get_help(update, context)
        return ConversationHandler.END


# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY'

CREATE_DONATION_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=CreateDonationHandler().start_create_donation,
                                       pattern=r'allow_donation'),
                  ],
    # TYPING_TOKEN, TYPING_TITLE,  TYPING_DESCRIPTION, TYPING_AMOUNT, TYPING_CURRENCY,\
    # TYPING_TAGS, TYPING_TAGS_FINISH, TYPING_TYPE, TYPING_DEADLINE, TYPING_REPEAT
    states={
        TYPING_TOKEN: [MessageHandler(Filters.text,
                                      CreateDonationHandler().handle_token)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.text,
                                            CreateDonationHandler().handle_description)],
        DONATION_FINISH: [MessageHandler(Filters.text,
                                         CreateDonationHandler().handle_donation_finish)],
    },

    fallbacks=[CallbackQueryHandler(callback=CreateDonationHandler().back, pattern=r"help_back"),
               CallbackQueryHandler(callback=CreateDonationHandler().back, pattern=r"help_module"),
               MessageHandler(filters=Filters.command, callback=CreateDonationHandler().back),
               ]
)

DONATIONS_MENU = CallbackQueryHandler(callback=donation_menu, pattern="donations_menu")
