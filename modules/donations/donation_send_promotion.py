# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from database import chatbots_table, users_table
from helper_funcs.helper import get_help

DONATION_TO_USERS, DONATION_TO_USERS_FINISH = range(2)


class SendDonationToUsers(object):
    def send_donation(self, update, context):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
        if chatbot.get("donate") != {} and "donate" in chatbot:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["send_donation_request_1"],
                                     reply_markup=reply_markup)
            return DONATION_TO_USERS
        else:
            admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["allow_donations_button"],
                                                   callback_data="allow_donation"),
                              InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                   callback_data="help_module(shop)")]
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["allow_donation_text"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def received_donation(self, update, context):
        if "content" not in context.user_data:
            context.user_data["content"] = []
        if update.message.text:
            context.user_data["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            context.user_data["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            context.user_data["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            context.user_data["content"].append({"audio_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            context.user_data["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            context.user_data["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            context.user_data["content"].append({"video_file": video_note_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                   callback_data="send_donation_finish")],
             [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                   callback_data="help_module(shop)k")]
             ]
        )
        context.bot.send_message(update.message.chat_id,
                                 context.bot.lang_dict["send_donation_request_2"],
                                 reply_markup=final_reply_markup)

        return DONATION_TO_USERS

    def send_donation_finish(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(shop)"), ])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.send_message(update.callback_query.message.chat_id,
                                 context.bot.lang_dict["send_donation_request_3"],
                                 reply_markup=final_reply_markup)
        if "user_category" not in context.user_data:
            chats = users_table.find({"bot_id": context.bot.id})
            chats2 = users_table.find({"bot_id": context.bot.id})

        elif context.user_data["user_category"] == "All":
            chats = users_table.find({"bot_id": context.bot.id})
            chats2 = users_table.find({"bot_id": context.bot.id})
        else:
            chats = users_table.find({"bot_id": context.bot.id, "user_category": context.user_data["user_category"]})
            chats2 = users_table.find({"bot_id": context.bot.id, "user_category": context.user_data["user_category"]})
        for chat in chats:
            if "chat_id" in chat:
                if chat["chat_id"] != update.callback_query.message.chat_id:
                    for content_dict in context.user_data["content"]:
                        if "text" in content_dict:
                            context.bot.send_message(chat["chat_id"],
                                                     content_dict["text"])
                        if "audio_file" in content_dict:
                            context.bot.send_audio(chat["chat_id"], content_dict["audio_file"])
                        if "voice_file" in content_dict:
                            context.bot.send_voice(chat["chat_id"], content_dict["voice_file"])
                        if "video_file" in content_dict:
                            context.bot.send_video(chat["chat_id"], content_dict["video_file"])
                        if "video_note_file" in content_dict:
                            context.bot.send_video_note(chat["chat_id"], content_dict["video_note_file"])
                        if "document_file" in content_dict:
                            if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                                context.bot.send_photo(chat["chat_id"], content_dict["document_file"])
                            else:
                                context.bot.send_document(chat["chat_id"], content_dict["document_file"])
                        if "photo_file" in content_dict:
                            context.bot.send_photo(chat["chat_id"], content_dict["photo_file"])
                        if "animation_file" in content_dict:
                            context.bot.send_animation(chat["chat_id"], content_dict["animation_file"])
                        if "sticker_file" in content_dict:
                            context.bot.send_sticker(chat["chat_id"], content_dict["sticker_file"])
        for chat in chats2:
            if chat["chat_id"] != update.callback_query.message.chat_id:
                context.bot.send_message(chat["chat_id"],
                                         text=context.bot.lang_dict["donate_button"],
                                         reply_markup=final_reply_markup)
        context.user_data.clear()
        return ConversationHandler.END

    def send_donation_cancel(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(shop)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.send_message(update.callback_query.message.chat_id,
                                 text=context.bot.lang_dict["send_message_9"],
                                 reply_markup=final_reply_markup)
        context.user_data.clear()
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        get_help(update, context)
        return ConversationHandler.END

    def cancel(self, update, context):
        update.message.reply_text(
            "Command is cancelled =("
        )

        get_help(update, context)
        return ConversationHandler.END


SEND_DONATION_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_donation_to_users",
                                       callback=SendDonationToUsers().send_donation)],

    states={
        DONATION_TO_USERS: [MessageHandler(Filters.all, SendDonationToUsers().received_donation), ],
    },

    fallbacks=[CallbackQueryHandler(callback=SendDonationToUsers().send_donation_finish,
                                    pattern=r"send_donation_finish"),
               CallbackQueryHandler(callback=SendDonationToUsers().send_donation_cancel,
                                    pattern="help_module"),
               ]
)
