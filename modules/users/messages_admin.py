# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from database import user_categories_table, users_table
from helper_funcs.helper import get_help


TOPIC,SEND_ANONIM, MESSAGE = range(3)
CHOOSE_CATEGORY, MESSAGE_TO_USERS = range(2)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class SendMessageToAdminsOnly(object):

    def send_message(self, update, context):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(messages)")])
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        categories = user_categories_table.find()
        if categories.count() > 0:
            context.bot.send_message(update.callback_query.message.chat_id,
                             context.bot.lang_dict["back_text"],
                             reply_markup=reply_markup)
            categories_list = ["All"] + [x["category"] for x in categories]
            category_markup = ReplyKeyboardMarkup([categories_list])

            context.bot.send_message(update.callback_query.message.chat_id,
                             context.bot.lang_dict["send_message_1_1"],
                             reply_markup=category_markup)
            return CHOOSE_CATEGORY
        else:
            context.bot.send_message(update.callback_query.message.chat_id,
                             context.bot.lang_dict["send_message_to_admins_text"],
                             reply_markup=reply_markup
                             )
            return MESSAGE_TO_USERS

    def choose_question(self, update, context):
        context.user_data["user_category"] = update.message.text
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(messages)")])
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(update.message.chat_id,
                         "Cool",
                         reply_markup=ReplyKeyboardRemove())
        context.bot.send_message(update.message.chat_id,
                         context.bot.lang_dict["send_message_1"],
                         reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    def received_message(self, update, context):
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
            video_note_file = update.message.video_note.get_file().file_id
            context.user_data["content"].append({"video_note_file": video_note_file})

        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            context.user_data["content"].append({"animation_file": animation_file})

        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            context.user_data["content"].append({"sticker_file": sticker_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["done_button"], callback_data="send_message_finish")],
             [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"], callback_data="help_module(messages)")]]
        )
        context.bot.send_message(update.message.chat_id,
                         context.bot.lang_dict["send_message_4"],
                         reply_markup=final_reply_markup)

        return MESSAGE_TO_USERS

    def send_message_finish(self, update, context):

        if "user_category" not in context.user_data:
            chats = users_table.find({"bot_id": context.bot.id,
                                      "is_admin": True})
            chats2 = users_table.find({"bot_id": context.bot.id,
                                      "is_admin": True})
        elif context.user_data["user_category"] == "All":
            chats = users_table.find({"bot_id": context.bot.id,
                                      "is_admin": True})
            chats2 = users_table.find({"bot_id": context.bot.id,
                                      "is_admin": True})

        else:
            chats = users_table.find({"bot_id": context.bot.id,
                                      "user_category": context.user_data["user_category"],
                                      "is_admin": True})
            chats2 = users_table.find({"bot_id": context.bot.id,
                                       "user_category": context.user_data["user_category"]})
        for chat in chats2:
            if chat["chat_id"] != update.callback_query.message.chat_id:
                context.bot.send_message(chat["chat_id"],
                                 text=context.bot.lang_dict["you_have_a_message_from"].format(update.effective_user.name))
        for chat in chats:
            if "chat_id" in chat:
                # if chat["chat_id"] != update.callback_query.message.chat_id:
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

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(messages)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.send_message(update.callback_query.message.chat_id,
                         context.bot.lang_dict["send_message_5"],
                         reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id))
        context.user_data.clear()

        return ConversationHandler.END

    def send_message_cancel(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(messages)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.send_message(update.callback_query.message.chat_id,
                         context.bot.lang_dict["send_message_9"],
                         reply_markup=final_reply_markup)
        context.user_data.clear()
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(update, context)
        return ConversationHandler.END


SEND_MESSAGE_ONLY_TO_ADMINS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_only_to_admins",
                                       callback=SendMessageToAdminsOnly().send_message)],

    states={
        CHOOSE_CATEGORY: [MessageHandler(Filters.all, SendMessageToAdminsOnly().choose_question, pass_user_data=True)],
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendMessageToAdminsOnly().received_message, pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=SendMessageToAdminsOnly().send_message_finish,
                             pattern=r"send_message_finish", pass_user_data=True),
        CallbackQueryHandler(pattern=r"help_module",
                             callback=SendMessageToAdminsOnly().send_message_cancel,
                             pass_user_data=True),
        CallbackQueryHandler(pattern=r"help_back",
                             callback=SendMessageToAdminsOnly().send_message_cancel,
                             pass_user_data=True),
    ]
)