# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, run_async, CallbackQueryHandler)
from database import chats_table, chatbots_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
DONATION_TO_USERS, DONATION_TO_USERS_FINISH = range(2)


class SendDonationToUsers(object):
    def send_donation(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="cancel_send_donation")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        if chatbot.get("donate") != {} and "donate" in chatbot:
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["send_donation_request_1"],
                             reply_markup=reply_markup)
            return DONATION_TO_USERS
        else:
            admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                                   callback_data="allow_donation"),
                              InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                   callback_data="help_module(donation_payment)")]
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["allow_donation_text"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def received_donation(self, bot, update, user_data):
        if "user_category" not in user_data:
            chats = chats_table.find({"bot_id": bot.id})
        elif user_data["user_category"] == "All":
            chats = chats_table.find({"bot_id": bot.id})
        else:
            chats = chats_table.find({"bot_id": bot.id, "user_category": user_data["user_category"]})
        for chat in chats:
            if chat["chat_id"] != update.message.chat_id:
                for content_dict in user_data["content"]:
                    if "text" in content_dict:
                        bot.send_message(chat["chat_id"],
                                         content_dict["text"])
                    if "audio_file" in content_dict:
                        bot.send_audio(chat["chat_id"], content_dict["audio_file"])
                    if "video_file" in content_dict:
                        bot.send_video(chat["chat_id"], content_dict["video_file"])
                    if "document_file" in content_dict:
                        if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                            bot.send_photo(chat["chat_id"], content_dict["document_file"])
                        else:
                            bot.send_document(chat["chat_id"], content_dict["document_file"])
                    if "photo_file" in content_dict:
                        bot.send_photo(chat["chat_id"], content_dict["photo_file"])
        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=string_dict(bot)["done_button"],
                                   callback_data="send_donation_finish")],
             [InlineKeyboardButton(text=string_dict(bot)["send_message_9"],
                                   callback_data="send_donation_cancel")]
             ]
        )
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_donation_request_2"],
                         reply_markup=final_reply_markup)

        return DONATION_TO_USERS

    def send_donation_finish(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["donate_button"],
                                             callback_data="pay_donation"),
                        InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(donation_payment)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_donation_request_3"],
                         reply_markup=final_reply_markup)
        chats = chats_table.find({"bot_id": bot.id})  # TODO it sends to everybody =/
        for chat in chats:
            if chat["chat_id"] != update.callback_query.message.chat_id:
                bot.send_message(chat["chat_id"],
                                 string_dict(bot)["donate_button"],
                                 reply_markup=final_reply_markup)
        return ConversationHandler.END

    def send_donation_cancel(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_9"],
                         reply_markup=final_reply_markup)
        user_data.clear()
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )

        get_help(bot, update)
        return ConversationHandler.END


SEND_DONATION_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_donation_to_users",
                                       callback=SendDonationToUsers().send_donation)],

    states={
        DONATION_TO_USERS: [MessageHandler(Filters.all, SendDonationToUsers().received_donation),],
    },

    fallbacks=[CallbackQueryHandler(callback=SendDonationToUsers().send_donation_finish,
                                    pattern=r"send_donation_finish", pass_user_data=True),
               CallbackQueryHandler(callback=SendDonationToUsers().back,
                                    pattern=r"cancel_send_donation"),
               CallbackQueryHandler(callback=SendDonationToUsers().send_donation_cancel,
                                    pattern="send_donation_cancel",
                                    pass_user_data=True),
               CommandHandler('cancel', SendDonationToUsers().cancel),
               MessageHandler(filters=Filters.command, callback=SendDonationToUsers().cancel),
               CallbackQueryHandler(callback=SendDonationToUsers().back, pattern=r"error_back"),
               ]
)
