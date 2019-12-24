# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
from haikunator import Haikunator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from database import users_messages_to_admin_table, user_categories_table, users_table
from helper_funcs.helper import get_help
from helper_funcs.lang_strings.strings import emoji
from helper_funcs.misc import delete_messages, lang_timestamp
from helper_funcs.pagination import Pagination, set_page_key

# categories_table,
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOPIC, SEND_ANONIM, MESSAGE = range(3)
CHOOSE_CATEGORY, MESSAGE_TO_USERS = range(2)
BLOCK_CONFIRMATION = 1


def messages_menu(update, context):
    string_d_str = context.bot.lang_dict
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
    not_read_messages_count = users_messages_to_admin_table.find(
        {"bot_id": context.bot.id, "is_new": True}).count() or ""
    no_channel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=string_d_str["send_message_button_2"] +
                               f" {not_read_messages_count}",
                               callback_data="inbox_message")],
         [InlineKeyboardButton(text=string_d_str["send_message_button_1"],
                               callback_data="send_message_to_users")],
         [InlineKeyboardButton(text=string_d_str["send_message_button_5"],
                               callback_data="send_message_to_donators")],
         [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                               callback_data="help_module(users)")]
         ]
    )
    context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["polls_str_9"],
                             reply_markup=no_channel_keyboard)
    return ConversationHandler.END


# class AddMessageCategory(object):
#
#     def add_category(self, update, context):
#         buttons = list()
#         buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                              callback_data="help_module(users)")])
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         bot.send_message(update.callback_query.message.chat_id,
#                          context.bot.lang_dict["send_message_14"], reply_markup=reply_markup)
#
#         return TOPIC
#
#     def add_category_finish(self, update, context):
#         categories_table.update({"category": update.message.text},
#                                 {"$set": {"category": update.message.text}},
#                                 upsert=True)
#         buttons = list()
#         buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                              callback_data="help_module(users)")])
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.send_message(update.message.chat_id,
#                          context.bot.lang_dict["send_message_15"],
#                          reply_markup=reply_markup)
#         return ConversationHandler.END
#
#
# class MessageCategory(object):
#
#     def show_category(self, update, context):
#         buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                          callback_data="help_module(users)"),
#                     InlineKeyboardButton(text=context.bot.lang_dict["add_message_category"],
#                                          callback_data="add_message_category"),
#                     ]]
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.send_message(update.callback_query.message.chat_id,
#                          context.bot.lang_dict["send_message_16"], reply_markup=reply_markup)
#
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         categories = categories_table.find()
#         for category in categories:
#             delete_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
#                                                     callback_data="delete_category_{}"
#                                                     .format(category["category"]))]]
#             delete_markup = InlineKeyboardMarkup(
#                 delete_buttons)
#             bot.send_message(update.callback_query.message.chat_id, category["category"],
#                              reply_markup=delete_markup)
#
#         return ConversationHandler.END
#
#
# class DeleteMessageCategory(object):
#
#     def delete_category(self, update, context):
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                          callback_data="help_module(users)")]]
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         categories_table.delete_one({"category": update.callback_query.data.replace("delete_category_", "")})
#
#         bot.send_message(update.callback_query.message.chat_id,
#                          context.bot.lang_dict["send_message_17"], reply_markup=reply_markup)
#
#         return ConversationHandler.END


class SendMessageToAdmin(object):

    def send_message(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="help_back")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        if "anonim" in update.callback_query.data:
            context.user_data["anonim"] = True
            context.bot.send_message(update.callback_query.message.chat_id,
                                     context.bot.lang_dict["send_message_from_user_to_admin_anonim_text"],
                                     reply_markup=reply_markup)
        else:
            context.user_data["anonim"] = False
            context.bot.send_message(update.callback_query.message.chat_id,
                                     context.bot.lang_dict["send_message_from_user_to_admin_text"],
                                     reply_markup=reply_markup)

        return MESSAGE

    # def send_topic(self, update, context):
    #     bot.send_message(update.message.chat_id,
    #                      random.choice(context.bot.lang_dict["polls_affirmations"]),
    #                      reply_markup=ReplyKeyboardRemove())
    #     user_data["topic"] = update.message.text
    #     buttons = list()
    #     buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
    #                                          callback_data="help_back")])
    #     reply_markup = InlineKeyboardMarkup(
    #         buttons)
    #     bot.send_message(update.message.chat_id,
    #                      context.bot.lang_dict["send_message_1"], reply_markup=reply_markup)
    #
    #     return MESSAGE

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
            context.user_data["content"].append({"video_file": video_note_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Done", callback_data="send_message_finish")],
             [InlineKeyboardButton(text="Cancel", callback_data="help_back")]]
        )
        context.bot.send_message(update.message.chat_id,
                                 context.bot.lang_dict["send_message_4"],
                                 reply_markup=final_reply_markup)

        return MESSAGE

    def send_message_finish(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        haikunator = Haikunator()
        if context.user_data.get("anonim", None) is True:
            context.user_data["user_full_name"] = "anonim_" + haikunator.haikunate()
            context.user_data["chat_id"] = update.callback_query.message.chat_id
        else:
            context.user_data["user_full_name"] = update.callback_query.from_user.mention_markdown()
            context.user_data["chat_id"] = update.callback_query.message.chat_id
        context.bot.send_message(update.callback_query.message.chat_id,
                                 context.bot.lang_dict["send_message_5"],
                                 reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id))
        if "_id" in context.user_data:
            context.user_data.pop("_id", None)
        context.user_data["timestamp"] = datetime.datetime.now().replace(microsecond=0)
        context.user_data["user_id"] = update.effective_user.id
        context.user_data["message_id"] = update.callback_query.message.message_id
        context.user_data["bot_id"] = context.bot.id
        context.user_data["mention_markdown"] = update.effective_user.mention_markdown()
        context.user_data["mention_html"] = update.effective_user.mention_html()
        context.user_data["is_new"] = True
        users_messages_to_admin_table.insert(context.user_data)
        context.user_data.clear()
        return ConversationHandler.END

    def send_message_cancel(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_back")])
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


class SendMessageToUsers(object):

    def send_message(self, update, context):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(users)")])
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
                                     context.bot.lang_dict["send_message_to_users_text"],
                                     reply_markup=reply_markup)
            return MESSAGE_TO_USERS

    def choose_question(self, update, context):
        context.user_data["user_category"] = update.message.text
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(users)")])
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(update.message.chat_id,
                                 "Cool", reply_markup=ReplyKeyboardRemove())
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
             [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"], callback_data="help_module(users)")]]
        )
        context.bot.send_message(update.message.chat_id,
                                 context.bot.lang_dict["send_message_4"],
                                 reply_markup=final_reply_markup)

        return MESSAGE_TO_USERS

    def send_message_finish(self, update, context):  # TODO does not work
        if "user_category" not in context.user_data:
            chats = users_table.find({"bot_id": context.bot.id})
        elif context.user_data["user_category"] == "All":
            chats = users_table.find({"bot_id": context.bot.id})
        else:
            chats = users_table.find({"bot_id": context.bot.id, "user_category": context.user_data["user_category"]})
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

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(users)")])
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
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(users)")])
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


class AnswerToMessage(object):

    def send_message(self, update, context):
        delete_messages(update, context)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(users)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        context.user_data["message_id"] = update.callback_query.data.replace("answer_to_message_", "")
        user = users_messages_to_admin_table.find_one(
            {"message_id": int(context.user_data["message_id"])})
        context.user_data["chat_id"] = user["chat_id"]

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        context.bot.send_message(update.callback_query.message.chat_id,
                                 context.bot.lang_dict["send_message_3"],
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
             [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"], callback_data="help_module(users)")]]
        )
        context.bot.send_message(update.message.chat_id,
                                 context.bot.lang_dict["send_message_4"],
                                 reply_markup=final_reply_markup)

        return MESSAGE_TO_USERS

    def send_message_finish(self, update, context):
        # user_name = bot.get_chat_member(user_data["chat_id"]).user.mention_markdown()

        context.bot.send_message(context.user_data["chat_id"],
                                 text=context.bot.lang_dict["send_message_answer_user"])
        for content_dict in context.user_data["content"]:
            if "text" in content_dict:
                context.bot.send_message(context.user_data["chat_id"],
                                         content_dict["text"])
            if "audio_file" in content_dict:
                context.bot.send_audio(context.user_data["chat_id"], content_dict["audio_file"])
            if "voice_file" in content_dict:
                context.bot.send_voice(context.user_data["chat_id"], content_dict["voice_file"])
            if "video_file" in content_dict:
                context.bot.send_video(context.user_data["chat_id"], content_dict["video_file"])
            if "video_note_file" in content_dict:
                context.bot.send_video_note(context.user_data["chat_id"], content_dict["video_note_file"])
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    context.bot.send_photo(context.user_data["chat_id"], content_dict["document_file"])
                else:
                    context.bot.send_document(context.user_data["chat_id"], content_dict["document_file"])
            if "photo_file" in content_dict:
                context.bot.send_photo(context.user_data["chat_id"], content_dict["photo_file"])
            if "animation_file" in content_dict:
                context.bot.send_animation(context.user_data["chat_id"], content_dict["animation_file"])
            if "sticker_file" in content_dict:
                context.bot.send_sticker(context.user_data["chat_id"], content_dict["sticker_file"])

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(users)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.send_message(update.callback_query.message.chat_id,
                                 context.bot.lang_dict["send_message_5"],
                                 reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id))
        context.user_data.clear()

        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        get_help(update, context)
        return ConversationHandler.END


class DeleteMessage(object):
    # def delete_message_double_check(self, update, context):  #TODO
    #     buttons = list()
    #     buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
    #                                          callback_data="help_module(users)")])
    #     reply_markup = InlineKeyboardMarkup(
    #         buttons)
    #     bot.delete_message(chat_id=update.callback_query.message.chat_id,
    #                        message_id=update.callback_query.message.message_id)

    def delete_message(self, update, context):
        delete_messages(update, context)
        buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="help_module(users)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        messages = users_messages_to_admin_table.find({"bot_id": context.bot.id})
        if messages.count() > 0:
            message_id = update.callback_query.data.replace("delete_message_", "")  # message_id
            if any(x in message_id for x in ["all", "week", "month"]):
                buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["yes"],
                                                 callback_data="trash_messages_" + message_id),
                            InlineKeyboardButton(text=context.bot.lang_dict["no"],
                                                 callback_data="help_module(users)")]]
                reply_markup = InlineKeyboardMarkup(
                    buttons)
                context.bot.send_message(update.callback_query.message.chat_id,
                                         context.bot.lang_dict["delete_messages_double_check"],
                                         reply_markup=reply_markup)
                context.user_data["message_id"] = message_id
                return DOUBLE_CHECK  # TODO send a keyboard with callback depending on previous callback data
            else:
                users_messages_to_admin_table.delete_one({"bot_id": context.bot.id, "message_id": int(message_id)})
                context.bot.send_message(update.callback_query.message.chat_id,
                                         context.bot.lang_dict["delete_message_str_1"],
                                         reply_markup=reply_markup)
                return ConversationHandler.END
        else:
            context.bot.send_message(update.callback_query.message.chat_id,
                                     context.bot.lang_dict["send_message_6"],
                                     reply_markup=reply_markup)
            return ConversationHandler.END

    def delete_message_double_check(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="help_module(users)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)

        if "all" in context.user_data["message_id"]:
            users_messages_to_admin_table.delete_many({"bot_id": context.bot.id})  # delete all messages from the users
        elif "week" in context.user_data["message_id"]:
            time_past = datetime.datetime.now() - datetime.timedelta(days=7)
            users_messages_to_admin_table.delete_many({"bot_id": context.bot.id,
                                                       "timestamp": {'$gt': time_past}})
            # delete all messages from the users for last week

        elif "month" in context.user_data["message_id"]:
            # delete all messages from the users for last month
            time_past = datetime.datetime.now() - datetime.timedelta(days=30)
            users_messages_to_admin_table.delete_many({"bot_id": context.bot.id,
                                                       "timestamp": {'$gt': time_past}})
        context.bot.send_message(update.callback_query.message.chat_id,
                                 context.bot.lang_dict["delete_message_str_1"],
                                 reply_markup=reply_markup)
        return ConversationHandler.END


class SeeMessageToAdmin(object):
    def see_messages(self, update, context):
        delete_messages(update, context, True)
        set_page_key(update, context, "inbox_message")
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="inbox_back")])
        delete_buttons = buttons
        delete_buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str_all"],
                                                    callback_data="delete_message_all")
                               ])
        delete_buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str_last_week"],
                                                    callback_data="delete_message_week"),
                               InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str_last_month"],
                                                    callback_data="delete_message_month")
                               ])
        messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id}).sort([["_id", -1]])
        per_page = 5
        if messages.count() != 0:
            pagination = Pagination(messages, context.user_data["page"], per_page)
            for message in pagination.content:
                message_buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["view_message_str"],
                        callback_data=f"view_message_{message['message_id']}")]
                ])
                context.user_data["to_delete"].append(
                    context.bot.send_message(
                        update.callback_query.message.chat_id,
                        (f"{emoji['email']}\n" if message["is_new"] else "") +
                        context.bot.lang_dict["message_temp"].format(
                            f"<code>{message['user_full_name']}</code>"
                            if message["anonim"] else message["mention_html"],
                            lang_timestamp(context, message["timestamp"])),
                        reply_markup=message_buttons,
                        parse_mode=ParseMode.HTML))
            pagination.send_keyboard(
                update, context, delete_buttons,
                context.bot.lang_dict["back_text"] +
                context.bot.lang_dict["message_count_str"].format(
                    messages.count()))
        else:
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                      callback_data="help_module(users)")]])
            context.bot.send_message(update.callback_query.message.chat_id,
                                     context.bot.lang_dict["send_message_6"],
                                     reply_markup=markup)

        return ConversationHandler.END

    def view_message(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        delete_messages(update, context)
        query = update.callback_query
        message = users_messages_to_admin_table.find_one(
            {"bot_id": context.bot.id,
             "message_id": int(query.data.replace("view_message_", ""))})
        if message["is_new"]:
            users_messages_to_admin_table.update_one({"_id": message["_id"]},
                                                     {"$set": {"is_new": False}})
        for content_dict in message["content"]:
            if "text" in content_dict:
                context.user_data["to_delete"].append(query.message.reply_text(text=content_dict["text"]))
            if "audio_file" in content_dict:
                context.user_data["to_delete"].append(query.message.reply_audio(content_dict["audio_file"]))
            if "voice_file" in content_dict:
                context.user_data["to_delete"].append(query.message.reply_audio(content_dict["voice_file"]))
            if "video_file" in content_dict:
                context.user_data["to_delete"].append(query.message.reply_video(content_dict["video_file"]))
            if "video_note_file" in content_dict:
                context.user_data["to_delete"].append(query.message.reply_video_note(content_dict["video_note_file"]))
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    context.user_data["to_delete"].append(
                        query.message.reply_photo(photo=content_dict["document_file"]))
                else:
                    context.user_data["to_delete"].append(
                        query.message.reply_document(document=content_dict["document_file"]))
            if "photo_file" in content_dict:
                context.user_data["to_delete"].append(query.message.reply_photo(photo=content_dict["photo_file"]))
            if "animation_file" in content_dict:
                context.user_data["to_delete"].append(
                    query.message.reply_animation(photo=content_dict["animation_file"]))
            if "sticker_file" in content_dict:
                context.user_data["to_delete"].append(query.message.reply_sticker(photo=content_dict["sticker_file"]))
        context.user_data["to_delete"].append(
            context.bot.send_message(update.callback_query.message.chat_id,
                                     context.bot.lang_dict["message_temp"].format(
                                         f"<code>{message['user_full_name']}</code>"
                                         if message["anonim"] else message["mention_html"],
                                         lang_timestamp(context, message["timestamp"])),
                                     reply_markup=InlineKeyboardMarkup([
                                         [InlineKeyboardButton(text=context.bot.lang_dict["answer_button_str"],
                                                               callback_data="answer_to_message_" +
                                                                             str(message["message_id"]))],
                                         [InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                               callback_data="delete_message_" +
                                                                             str(message["message_id"]))],
                                          [InlineKeyboardButton(text=context.bot.lang_dict["block_button_str"],
                                                                callback_data="block_user_" +
                                                                              str(message["user_id"]))]]),
                                     parse_mode=ParseMode.HTML))
        context.bot.send_message(update.callback_query.message.chat_id,
                                 context.bot.lang_dict["back_text"],
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                           callback_data="view_back_message")]]))
        return ConversationHandler.END

    def blocked_users_list(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        blocked_users = users_table.find({"bot_id": context.bot.id, "blocked": True})
        for user in blocked_users:
            context.bot.send_message(update.callback_query.message.chat_id, "{}\n".format(user["full_name"]),
                                     InlineKeyboardMarkup([[InlineKeyboardButton(text="UNBLOCK",
                                                                                 callback_data="unblock_{}".format(
                                                                                     user["user_id"]))]])
                             )
        context.bot.send_message(update.callback_query.message.chat_id, "This is the list of all blocked users",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                           callback_data="help_module(users)")]]))

    def unblock(self, update, context):
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(users)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)

        user_id = update.callback_query.data.replace("unblock_", "")
        user = users_table.find_one({"user_id": user_id})
        user["blocked"] = False
        users_table.update({"user_id": user_id}, user)
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        context.bot.send_message(update.callback_query.message.chat_id, "User has been removed from the blacklist",
                                 reply_markup=final_reply_markup)
        return ConversationHandler.END

    def block_user(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        context.user_data["user_id"] = int(update.callback_query.data.replace("block_user_", ""))
        context.bot.send_message(update.callback_query.message.chat_id,
                                 "Are you sure that you want to block this user? \n"
                                 "He won't be able to use this chatbot anymore",
                                 reply_markup=ReplyKeyboardMarkup([["YES", "NO"]], one_time_keyboard=True))
        return BLOCK_CONFIRMATION

    def block_confirmation(self, update, context):
        user = users_table.find_one({"user_id": context.user_data["user_id"],
                                     "bot_id": context.bot.id})
        user["blocked"] = True
        users_table.update({"user_id": context.user_data["user_id"]}, user)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                             callback_data="inbox_message")]])
        if update.message.text == "YES":
            context.bot.send_message(update.message.chat_id, "User {} has been blocked".format(
                context.user_data["user_name"], reply_markup=markup
            ))
        else:
            context.bot.send_message(update.message.chat_id, "Blocking has been canceled", reply_markup=markup)
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        delete_messages(update, context)
        get_help(update, context)
        return ConversationHandler.END


# class Message(object):
#     def __init__(self):
#         pass


MESSAGES_MENU = CallbackQueryHandler(callback=messages_menu, pattern="admin_messages")
DOUBLE_CHECK = 1
DELETE_MESSAGES_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="delete_message",
                                       callback=DeleteMessage().delete_message)],
    states={DOUBLE_CHECK: [CallbackQueryHandler(pattern="trash_messages_",
                                                callback=DeleteMessage().delete_message_double_check)]},
    fallbacks=[
        CallbackQueryHandler(SendMessageToUsers().send_message_cancel,
                             pattern="help_back")
    ]
)

SEND_MESSAGE_TO_ADMIN_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_admin",
                                       callback=SendMessageToAdmin().send_message),
                  ],

    states={
        MESSAGE: [MessageHandler(Filters.all, SendMessageToAdmin().received_message), ],
        # TOPIC: [MessageHandler(Filters.all, SendMessageToAdmin().send_topic), ]
        # SEND_ANONIM: [MessageHandler(Filters.all, SendMessageToAdmin().send_anonim), ]

    },

    fallbacks=[
        CallbackQueryHandler(callback=SendMessageToAdmin().send_message_finish,
                             pattern=r"send_message_finish"),
        CallbackQueryHandler(SendMessageToUsers().send_message_cancel,
                             pattern="help_back"),
    ]
)

SEND_MESSAGE_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_users",
                                       callback=SendMessageToUsers().send_message)],

    states={
        CHOOSE_CATEGORY: [MessageHandler(Filters.all, SendMessageToUsers().choose_question)],
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendMessageToUsers().received_message)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=SendMessageToUsers().send_message_finish,
                             pattern=r"send_message_finish"),
        CallbackQueryHandler(pattern=r"help_module",
                             callback=SendMessageToUsers().send_message_cancel),
        CallbackQueryHandler(pattern=r"help_back",
                             callback=SendMessageToUsers().send_message_cancel),
    ]
)


SEE_MESSAGES_HANDLER = CallbackQueryHandler(pattern="inbox_message", callback=SeeMessageToAdmin().see_messages)
SEE_MESSAGES_BACK_HANDLER = CallbackQueryHandler(pattern="inbox_back", callback=SeeMessageToAdmin().back)
SEE_MESSAGES_FINISH_HANDLER = CallbackQueryHandler(pattern="view_message_",
                                                   callback=SeeMessageToAdmin().view_message)
SEE_MESSAGES_FINISH_BACK_HANDLER = CallbackQueryHandler(pattern="view_back_message",
                                                        callback=SeeMessageToAdmin().back)

# todo I think need to put all SEE_MESSAGES HANDLERS in ConversationHandler or not... I don't know
SEE_MESSAGES_PAGINATION_HANDLER = CallbackQueryHandler(SeeMessageToAdmin().see_messages,
                                                       pattern="^[0-9]+$")


ANSWER_TO_MESSAGE_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern=r"answer_to_message",
                                       callback=AnswerToMessage().send_message)],

    states={
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, AnswerToMessage().received_message)],

    },

    fallbacks=[CallbackQueryHandler(callback=AnswerToMessage().send_message_finish,
                                    pattern=r"send_message_finish"),
               CallbackQueryHandler(callback=AnswerToMessage().back,
                                    pattern=r"help_module"),
               CallbackQueryHandler(callback=AnswerToMessage().back,
                                    pattern=r"help_back"),
               ]
)
BLOCK_USER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="block_user",
                                       callback=SeeMessageToAdmin().block_user),
                  ],

    states={
        BLOCK_CONFIRMATION: [
            MessageHandler(Filters.all, SeeMessageToAdmin().block_confirmation), ],
        # TOPIC: [MessageHandler(Filters.all, SendMessageToAdmin().send_topic), ]
        # SEND_ANONIM: [MessageHandler(Filters.all, SendMessageToAdmin().send_anonim), ]

    },

    fallbacks=[
        CallbackQueryHandler(SendMessageToUsers().send_message_cancel,
                             pattern="help_back"),
    ]
)
BLOCKED_USERS_LIST = CallbackQueryHandler(pattern="blocked_users_list",
                                          callback=SeeMessageToAdmin().blocked_users_list)
UNBLOCK_USER = CallbackQueryHandler(pattern="unblock",
                                    callback=SeeMessageToAdmin().unblock)
# MESSAGE_CATEGORY_HANDLER = CallbackQueryHandler(pattern="show_message_categories",
#                                                 callback=MessageCategory().show_category)
# DELETE_MESSAGE_CATEGORY_HANDLER = CallbackQueryHandler(pattern="delete_category_",
#                                                        callback=DeleteMessageCategory().delete_category)
# ADD_MESSAGE_CATEGORY_HANDLER = ConversationHandler(
#     entry_points=[CallbackQueryHandler(pattern="add_message_category",
#                                        callback=AddMessageCategory().add_category)],
#
#     states={
#         TOPIC: [MessageHandler(Filters.all, AddMessageCategory().add_category_finish)],
#     },
#
#     fallbacks=[
#         CallbackQueryHandler(callback=SendMessageToUsers().back,
#                              pattern=r"help_module"),
#         CallbackQueryHandler(callback=SendMessageToUsers().back,
#                              pattern=r"help_back"),
#     ]
# )
