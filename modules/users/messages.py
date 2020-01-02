# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging

from bson.objectid import ObjectId
from haikunator import Haikunator
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from helper_funcs.helper import get_help
from helper_funcs.lang_strings.strings import emoji
from helper_funcs.misc import delete_messages, lang_timestamp, user_mention
from helper_funcs.pagination import Pagination
from modules.users.users import UserTemplate
from modules.users.message_helper import (
    send_message_content, send_message_template, add_to_content)
from database import (users_messages_to_admin_table,
                      user_categories_table, users_table)


# categories_table,
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def messages_menu(update, context):
    string_d_str = context.bot.lang_dict
    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id)
    # Get unread messages count.
    new_messages_count = users_messages_to_admin_table.find(
        {"bot_id": context.bot.id, "is_new": True}).count()
    messages_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=string_d_str["send_message_button_2"]
                              + (f" ({new_messages_count})"
                                 if new_messages_count else ""),
                              callback_data="inbox_message")],
        [InlineKeyboardButton(text=string_d_str["send_message_button_1"],
                              callback_data="send_message_to_users")],
        [InlineKeyboardButton(text=string_d_str["send_message_button_5"],
                              callback_data="send_message_to_donators")],
        [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                              callback_data="help_module(users)")]
    ])
    context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                             text=context.bot.lang_dict["polls_str_9"],
                             reply_markup=messages_keyboard)
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
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)
        buttons = [[InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="help_back")]]
        reply_markup = InlineKeyboardMarkup(buttons)

        user = users_table.find_one({"user_id": context.effective_user.id,
                                     "bot_id": context.bot.id})

        if "anonim" in update.callback_query.data:
            if (user.get("anonim_messages_blocked")
                    or user.get("regular_messages_blocked")):
                # TODO STRINGS
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="You have been blocked "
                                              "so u can't send anonim "
                                              "messages anymore")
                update.callback_query.answer("You have been blocked")
                get_help(update, context)
                return ConversationHandler.END

            context.user_data["anonim"] = True
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict[
                    "send_message_from_user_to_admin_anonim_text"],
                reply_markup=reply_markup)
        else:
            if user.get("regular_messages_blocked"):
                # TODO STRINGS
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="You have been blocked "
                                              "so u can't send "
                                              "messages anymore")
                update.callback_query.answer("You have been blocked")
                get_help(update, context)
                return ConversationHandler.END
            context.user_data["anonim"] = False
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict[
                    "send_message_from_user_to_admin_text"],
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
        """if "content" not in context.user_data:
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
            context.user_data["content"].append({"video_file": video_note_file})"""
        add_to_content(update, context)
        # TODO STRINGS
        final_reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="Done",
                callback_data="send_message_finish")],
            [InlineKeyboardButton(
                text="Cancel",
                callback_data="help_back")]
        ])
        context.bot.send_message(update.message.chat_id,
                                 context.bot.lang_dict["send_message_4"],
                                 reply_markup=final_reply_markup)

        return MESSAGE

    def send_message_finish(self, update, context):
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(
                            text=context.bot.lang_dict["back_button"],
                            callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(buttons)
        # if context.user_data.get("anonim", None) is True:
        #     context.user_data["user_full_name"] = "anonim_" + haikunator.haikunate()
        #     context.user_data["chat_id"] = update.callback_query.message.chat_id
        # else:
        #     context.user_data["user_full_name"] = update.callback_query.from_user.mention_markdown()
        #     context.user_data["chat_id"] = update.callback_query.message.chat_id
        if context.user_data.get("anonim", None):
            context.user_data["user_full_name"] = \
                "anonim_" + Haikunator().haikunate()
        else:
            context.user_data["user_full_name"] = \
                update.callback_query.from_user.full_name

        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=context.bot.lang_dict["send_message_5"],
            reply_markup=final_reply_markup)

        logger.info("User {} on bot {}:{} sent a message to the admin".format(
            update.effective_user.first_name, context.bot.first_name,
            context.bot.id))

        if "_id" in context.user_data:
            context.user_data.pop("_id", None)
        context.user_data.pop("to_delete", None)


        # context.user_data["message_id"] =
        # update.callback_query.message.message_id
        # context.user_data["mention_markdown"] = update.effective_user.mention_markdown()
        # context.user_data["mention_html"] = update.effective_user.mention_html()
        context.user_data["is_new"] = True
        context.user_data["user_id"] = update.effective_user.id
        context.user_data["bot_id"] = context.bot.id
        context.user_data["chat_id"] = update.callback_query.message.chat_id
        context.user_data["timestamp"] = \
            datetime.datetime.now().replace(microsecond=0)
        users_messages_to_admin_table.insert(context.user_data)
        context.user_data.clear()
        # TODO MAYBE JUST RETURN TO THE MAIN MENU WITH BLINK MESSAGE
        return ConversationHandler.END

    def send_message_cancel(self, update, context):
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(
                            text=context.bot.lang_dict["back_button"],
                            callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=context.bot.lang_dict["send_message_9"],
            reply_markup=final_reply_markup)
        context.user_data.clear()
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
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
        """if "content" not in context.user_data:
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
            context.user_data["content"].append({"sticker_file": sticker_file})"""
        add_to_content(update, context)
        final_reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                  callback_data="send_message_finish")],
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                  callback_data="help_module(users)")]
        ])
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=context.bot.lang_dict["send_message_4"],
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
        delete_messages(update, context, True)
        buttons = list()
        buttons.append([InlineKeyboardButton(
                            text=context.bot.lang_dict["back_button"],
                            callback_data="help_module(users)")])
        reply_markup = InlineKeyboardMarkup(buttons)
        context.user_data["message_id"] = update.callback_query.data.replace(
            "answer_to_message_", "")
        message = users_messages_to_admin_table.find_one(
            {"_id": ObjectId(context.user_data["message_id"])})
        context.user_data["chat_id"] = message["chat_id"]

        # context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
        #                            message_id=update.callback_query.message.message_id)
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=context.bot.lang_dict["send_message_3"],
            reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    def received_message(self, update, context):
        """if "content" not in context.user_data:
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
            context.user_data["content"].append({"sticker_file": sticker_file})"""
        add_to_content(update, context)
        final_reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                  callback_data="send_message_finish")],
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                  callback_data="help_module(users)")]
        ])
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=context.bot.lang_dict["send_message_4"],
                                 reply_markup=final_reply_markup)
        return MESSAGE_TO_USERS

    def send_message_finish(self, update, context):
        context.bot.send_message(
            chat_id=context.user_data["chat_id"],
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
        # Set current page integer in user_data.
        if update.callback_query.data.startswith("inbox_pagination_"):
            context.user_data["page"] = int(
                update.callback_query.data.replace("inbox_pagination_", ""))
        if not context.user_data.get("page"):
            context.user_data["page"] = 1

        buttons = list()
        buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="inbox_back")])

        delete_buttons = buttons
        delete_buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["delete_button_str_all"],
                callback_data="delete_message_all")])
        delete_buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["delete_button_str_last_week"],
                callback_data="delete_message_week"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["delete_button_str_last_month"],
                 callback_data="delete_message_month")])

        messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id}).sort([["_id", -1]])
        if messages.count() != 0:
            pagination = Pagination(messages, context.user_data["page"])
            for message in pagination.content:
                message_buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["view_message_str"],
                        callback_data=f"view_message_{message['_id']}")]
                ])

                # context.user_data["to_delete"].append(
                #     context.bot.send_message(
                #         chat_id=update.callback_query.message.chat_id,
                #         text=(f"{emoji['new']}\n"
                #               if message["is_new"] else "")
                #         + context.bot.lang_dict["message_temp"].format(
                #             f"<code>{message['user_full_name']}</code>"
                #             if message["anonim"]
                #             else user_mention(message["user_id"],
                #                               message["user_full_name"]),
                #             lang_timestamp(context, message["timestamp"])),
                #         reply_markup=message_buttons,
                #         parse_mode=ParseMode.HTML))
                send_message_template(update, context, message,
                                      reply_markup=message_buttons)

            pagination.send_keyboard(
                update, context,
                buttons=delete_buttons, page_prefix="inbox_pagination",
                text=context.bot.lang_dict["back_text"]
                + context.bot.lang_dict["message_count_str"].format(
                    messages.count()))
        else:
            # back_markup = InlineKeyboardMarkup([
            #     [InlineKeyboardButton(
            #         text=context.bot.lang_dict["back_button"],
            #         callback_data="help_module(users)")]])
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["send_message_6"],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="help_module(users)")]
                ]))
        return ConversationHandler.END

    def view_message(self, update, context):
        # context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
        #                            message_id=update.callback_query.message.message_id)
        delete_messages(update, context, True)
        if update.callback_query.data.startswith("view_message"):
            context.user_data["message"] = \
                users_messages_to_admin_table.find_one(
                    {"_id": ObjectId(
                        update.callback_query.data.replace(
                            "view_message_", ""))})

        user_sender = users_table.find_one(
            {"user_id": context.user_data["message"]["user_id"],
             "bot_id": context.bot.id})
        if context.user_data["message"]["is_new"]:
            users_messages_to_admin_table.update_one(
                {"_id": context.user_data["message"]["_id"]},
                {"$set": {"is_new": False}})
        send_message_content(update, context, context.user_data["message"])
        """for content_dict in message["content"]:
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
                context.user_data["to_delete"].append(query.message.reply_sticker(photo=content_dict["sticker_file"]))"""
        buttons = [
            [InlineKeyboardButton(
                text=context.bot.lang_dict["answer_button_str"],
                callback_data="answer_to_message_"
                              + str(context.user_data["message"]["_id"])),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["delete_button_str"],
                 callback_data="delete_message_"
                               + str(context.user_data["message"]["_id"]))],
        ]
        if context.user_data["message"]["anonim"]:
            if user_sender["anonim_messages_blocked"]:
                # TODO NEW CALLBACK
                buttons.append([InlineKeyboardButton(
                    text=context.bot.lang_dict["unblock_messages_button"],
                    callback_data="unblock_anonim_messaging_"
                                  + str(user_sender["user_id"]))])
            else:
                # TODO NEW CALLBACK
                buttons.append([InlineKeyboardButton(
                    text=context.bot.lang_dict["block_button_str"],
                    callback_data="block_anonim_messaging_"
                                  + str(user_sender["user_id"]))])
        else:
            if user_sender["regular_messages_blocked"]:
                # TODO NEW CALLBACK
                buttons.append([InlineKeyboardButton(
                    text=context.bot.lang_dict["unblock_messages_button"],
                    callback_data=f"unblock_messages_from_inbox_"
                                  + str(user_sender['user_id']))])
            else:
                # TODO NEW CALLBACK
                buttons.append([InlineKeyboardButton(
                    text=context.bot.lang_dict["block_messages_button"],
                    callback_data=f"block_messages_from_inbox_"
                                  + str(user_sender['user_id']))])
        # Back button.
        buttons.append([InlineKeyboardButton(
            text=context.bot.lang_dict["back_button"],
            callback_data="back_to_inbox")])


        # reply_markup = InlineKeyboardMarkup([
        #     [InlineKeyboardButton(
        #         text=context.bot.lang_dict["answer_button_str"],
        #         callback_data="answer_to_message_"
        #                       + str(message["_id"]))],
        #     [InlineKeyboardButton(
        #         text=context.bot.lang_dict["delete_button_str"],
        #         callback_data="delete_message_"
        #                       + str(message["_id"]))],
            # TODO IF anonim block - block just anonnim message -
            #  Warning that will never send anonim messages
        #     [InlineKeyboardButton(
        #         text=context.bot.lang_dict["block_button_str"],
        #         callback_data="block_user_"
        #                       + str(message["user_id"]))]
        # ])
        send_message_template(update, context, context.user_data["message"],
                              reply_markup=InlineKeyboardMarkup(buttons),
                              text=context.bot.lang_dict["back_text"])
        """context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["message_temp"].format(
                    f"<code>{message['user_full_name']}</code>"
                    if message["anonim"]
                    else user_mention(message["user_id"],
                                      message["user_full_name"]),
                    lang_timestamp(context, message["timestamp"])),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["answer_button_str"],
                        callback_data="answer_to_message_"
                                      + str(message["_id"]))],
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["delete_button_str"],
                        callback_data="delete_message_"
                                      + str(message["_id"]))],
                    # TODO IF anonim block - block just anonnim message -
                    #  Warning that will never send anonim messages
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["block_button_str"],
                        callback_data="block_user_"
                                      + str(message["user_id"]))]]),
                parse_mode=ParseMode.HTML))"""
        # context.bot.send_message(
        #     chat_id=update.callback_query.message.chat_id,
        #     text=context.bot.lang_dict["back_text"],
        #     reply_markup=InlineKeyboardMarkup([
        #         [InlineKeyboardButton(
        #             text=context.bot.lang_dict["back_button"],
        #             callback_data="view_back_message")]]))
        return ConversationHandler.END

    def block_anonim_messaging_confirmation(self, update, context):
        delete_messages(update, context, True)
        context.user_data["user_id"] = int(
            update.callback_query.data.replace("block_anonim_messaging_", ""))

        # user = users_table.find_one({"user_id": context.user_data["user_id"],
        #                              "bot_id": context.bot.id})
        # user["blocked"] = True
        # users_table.update({"user_id": context.user_data["user_id"]}, user)
        reply_markup = InlineKeyboardMarkup([
            # TODO NEW CALLBACK
            [InlineKeyboardButton(
                text=context.bot.lang_dict["block_messages_button"],
                callback_data="block_anonim_messaging_confirm_true"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["back_button"],
                 callback_data="back_to_inbox_view_message")]])

        send_message_template(update, context, context.user_data["message"],
                              reply_markup=reply_markup,
                              text="Are you sure that you want to block "
                                   "anonim messages for this user?"
                                   "\n This User won't be able to send "
                                   "anonim messages anymore")

        # context.user_data["to_delete"].append(
        #     context.bot.send_message(
        #         chat_id=update.effective_chat.id,
        #         text="Are you sure that you want to block anonim messages "
        #              "for this user?\n This User won't be able "
        #              "to send anonim messages anymore",
        #         reply_markup=reply_markup))
        # UserTemplate(user).send(
        #     update, context,
        #     text="Are you sure that you want to block messages for this user?"
        #          "\nUser won't be able to send messages anymore",
        #     reply_markup=markup)
        return ConversationHandler.END

    def block_anonim_messaging_finish(self, update, context):
        users_table.update_one({"bot_id": context.bot.id,
                                "user_id": context.user_data["user_id"]},
                               {"$set": {"anonim_messages_blocked": True}})
        update.callback_query.answer(
            "User won't be able to send anonim messages anymore")
        return self.back_to_view_message(update, context)

    def unblock_anonim_messaging_finish(self, update, context):
        users_table.update_one({"bot_id": context.bot.id,
                                "user_id": context.user_data["user_id"]},
                               {"$set": {"anonim_messages_blocked": False}})
        update.callback_query.answer("For now user can send anonim messages")
        return self.back_to_view_message(update, context)

    def block_messaging_confirmation(self, update, context):
        delete_messages(update, context, True)
        context.user_data["user_id"] = int(
            update.callback_query.data.replace("block_messages_from_inbox_",
                                               ""))
        user = users_table.find_one({"user_id": context.user_data["user_id"],
                                     "bot_id": context.bot.id})

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=context.bot.lang_dict["block_messages_button"],
                callback_data="block_messaging_confirm_true_from_inbox"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["back_button"],
                 callback_data="back_to_inbox_view_message")]])
        # TODO STRINGS
        UserTemplate(user).send(
            update, context,
            text="Are you sure that you want to block messages for this user?"
                 "\nUser won't be able to send any messages anymore",
            reply_markup=markup)
        return ConversationHandler.END

    def block_messaging_finish(self, update, context):
        delete_messages(update, context, True)
        users_table.update_one({"bot_id": context.bot.id,
                                "user_id": context.user_data["user_id"]},
                               {"$set": {"regular_messages_blocked": True,
                                         "anonim_messages_blocked": True}})
        # TODO STRINGS
        update.callback_query.answer(
            "User won't be able to send messages anymore")
        return self.back_to_view_message(update, context)

    def unblock_messaging_finish(self, update, context):
        user_id = int(update.callback_query.data.replace(
            "unblock_messages_from_inbox_", ""))
        users_table.update_one({"user_id": user_id},
                               {"$set": {"regular_messages_blocked": False,
                                         "anonim_messages_blocked": False}})
        # TODO STRINGS
        update.callback_query.answer("User has been removed from the mute")
        return self.back_to_view_message(update, context)

    """def blocked_users_list(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        blocked_users = users_table.find({"bot_id": context.bot.id, "blocked": True})
        for user in blocked_users:
            context.bot.send_message(update.callback_query.message.chat_id, "{}\n".format(user["full_name"]),
                                     InlineKeyboardMarkup([[InlineKeyboardButton(text=context.bot.lang_dict["unblock_button_str"],
                                                                                 callback_data="unblock_{}".format(
                                                                                     user["user_id"]))]])
                             )
        context.bot.send_message(update.callback_query.message.chat_id, "This is the list of all blocked users",
                                 reply_markup=InlineKeyboardMarkup([
                                     [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                           callback_data="help_module(users)")]]))
        # return ConversationHandler.END"""

    """def unblock(self, update, context):
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
        return ConversationHandler.END"""

    def back_to_view_message(self, update, context):
        """
        All backs to the opened user message must be done through this method
        """
        delete_messages(update, context, True)
        try:
            message = context.user_data["message"]
            page = context.user_data["page"]
        except KeyError:
            context.user_data.clear()
            return get_help(update, context)

        context.user_data.clear()
        context.user_data["message"] = users_messages_to_admin_table.find_one(
            {"_id": message["_id"]})
        context.user_data["page"] = page
        return self.view_message(update, context)

    def back_to_inbox(self, update, context):
        """
        All backs to the messages list must be done through this method
        """
        delete_messages(update, context, True)
        page = context.user_data.get("page", 1)

        context.user_data.clear()
        context.user_data["page"] = page
        return self.view_message(update, context)
    # def back(self, update, context):
    #     context.bot.delete_message(
    #         chat_id=update.callback_query.message.chat_id,
    #         message_id=update.callback_query.message.message_id)
    #     delete_messages(update, context)
    #     get_help(update, context)
    #     return ConversationHandler.END


TOPIC, SEND_ANONIM, MESSAGE = range(3)
CHOOSE_CATEGORY, MESSAGE_TO_USERS = range(2)
BLOCK_CONFIRMATION = 1
DOUBLE_CHECK = 1


MESSAGES_MENU = CallbackQueryHandler(
    pattern="admin_messages",
    callback=messages_menu)


DELETE_MESSAGES_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern="delete_message",
            callback=DeleteMessage().delete_message)],

    states={
        DOUBLE_CHECK: [
            CallbackQueryHandler(
                pattern="trash_messages_",
                callback=DeleteMessage().delete_message_double_check)]},

    fallbacks=[
        CallbackQueryHandler(
            pattern="help_back",
            callback=SendMessageToUsers().send_message_cancel)]
)


SEND_MESSAGE_TO_ADMIN_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern="send_message_to_admin",
            callback=SendMessageToAdmin().send_message)],

    states={
        MESSAGE: [
            MessageHandler(
                filters=Filters.all,
                callback=SendMessageToAdmin().received_message)],
        # TOPIC: [MessageHandler(Filters.all, SendMessageToAdmin().send_topic), ]
        # SEND_ANONIM: [MessageHandler(Filters.all, SendMessageToAdmin().send_anonim), ]
    },

    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=SendMessageToAdmin().send_message_finish),
        CallbackQueryHandler(
            pattern="help_back",
            callback=SendMessageToUsers().send_message_cancel)]
)


SEND_MESSAGE_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern="send_message_to_users",
            callback=SendMessageToUsers().send_message)],

    states={
        CHOOSE_CATEGORY: [
            MessageHandler(
                filters=Filters.all,
                callback=SendMessageToUsers().choose_question)],

        MESSAGE_TO_USERS: [
            MessageHandler(
                filters=Filters.all,
                callback=SendMessageToUsers().received_message)],
    },

    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=SendMessageToUsers().send_message_finish),
        CallbackQueryHandler(
            pattern=r"help_module",
            callback=SendMessageToUsers().send_message_cancel),
        CallbackQueryHandler(
            pattern=r"help_back",
            callback=SendMessageToUsers().send_message_cancel)]
)


SEE_MESSAGES_HANDLER = CallbackQueryHandler(
    pattern="^(inbox_message|inbox_pagination)",
    callback=SeeMessageToAdmin().see_messages)


CONFIRM_BLOCK_ANONIM_MESSAGING = CallbackQueryHandler(
    pattern=r"block_anonim_messaging",
    callback=SeeMessageToAdmin().block_anonim_messaging_confirmation)

FINISH_BLOCK_ANONIM_MESSAGING = CallbackQueryHandler(
    pattern="block_anonim_messaging_confirm_true",
    callback=SeeMessageToAdmin().block_anonim_messaging_finish)

UNBLOCK_ANONIM_MESSAGING = CallbackQueryHandler(
    pattern=r"unblock_anonim_messaging",
    callback=SeeMessageToAdmin(). unblock_anonim_messaging_finish)


CONFIRM_BLOCK_MESSAGING_FROM_INBOX = CallbackQueryHandler(
    pattern=r"block_messages_from_inboxv",
    callback=SeeMessageToAdmin().block_messaging_confirmation)

FINISH_BLOCK_MESSAGING_FROM_INBOX = CallbackQueryHandler(
    pattern="block_messaging_confirm_true_from_inbox",
    callback=SeeMessageToAdmin().block_messaging_finish)

FINISH_UNBLOCK_MESSAGING_FROM_INBOX = CallbackQueryHandler(
    pattern=r"unblock_messages_from_inbox",
    callback=SeeMessageToAdmin().unblock_messaging_finish)


BACK_TO_INBOX_VIEW_MESSAGE = CallbackQueryHandler(
    pattern="back_to_inbox_view_message",
    callback=SeeMessageToAdmin().back_to_view_message)

BACK_TO_INBOX = CallbackQueryHandler(
    pattern=r"back_to_inbox",
    callback=SeeMessageToAdmin().back_to_inbox)

# SEE_MESSAGES_BACK_HANDLER = CallbackQueryHandler(
#     pattern="inbox_back",
#     callback=SeeMessageToAdmin().back)

SEE_MESSAGES_FINISH_HANDLER = CallbackQueryHandler(
    pattern="view_message_",
    callback=SeeMessageToAdmin().view_message)

# SEE_MESSAGES_FINISH_BACK_HANDLER = CallbackQueryHandler(
#     pattern="view_back_message",
#     callback=SeeMessageToAdmin().back)

# SEE_MESSAGES_PAGINATION_HANDLER = CallbackQueryHandler(
#     callback=SeeMessageToAdmin().see_messages, pattern="inbox_pagination")


ANSWER_TO_MESSAGE_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern=r"answer_to_message",
            callback=AnswerToMessage().send_message)],

    states={
        MESSAGE_TO_USERS: [
            MessageHandler(
                filters=Filters.all,
                callback=AnswerToMessage().received_message)]
    },

    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=AnswerToMessage().send_message_finish),
        CallbackQueryHandler(
            pattern=r"help_module",
            callback=AnswerToMessage().back),
        CallbackQueryHandler(
            pattern=r"help_back",
            callback=AnswerToMessage().back)]
)

"""BLOCK_USER = ConversationHandler(
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
                                    callback=SeeMessageToAdmin().unblock)"""
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
