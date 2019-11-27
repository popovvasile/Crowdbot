# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
# import random
from haikunator import Haikunator
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from database import users_messages_to_admin_table, user_categories_table, users_table
from helper_funcs.helper import get_help
from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.misc import delete_messages

# categories_table,
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOPIC, SEND_ANONIM, MESSAGE = range(3)
CHOOSE_CATEGORY, MESSAGE_TO_USERS = range(2)
BLOCK_CONFIRMATION = 1


def messages_menu(bot, update):
    string_d_str = string_dict(bot)
    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    no_channel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=string_d_str["send_message_button_2"],
                               callback_data="inbox_message")],
         [InlineKeyboardButton(text=string_d_str["send_message_button_1"],
                               callback_data="send_message_to_users")],
         [InlineKeyboardButton(text=string_d_str["send_message_button_5"],
                               callback_data="send_message_to_donators")],
         [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                               callback_data="help_module(users)")]
         ]
    )
    bot.send_message(update.callback_query.message.chat.id,
                     string_dict(bot)["polls_str_9"], reply_markup=no_channel_keyboard)
    return ConversationHandler.END


# class AddMessageCategory(object):
#
#     def add_category(self, bot, update):
#         buttons = list()
#         buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
#                                              callback_data="help_module(messages)")])
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         bot.send_message(update.callback_query.message.chat_id,
#                          string_dict(bot)["send_message_14"], reply_markup=reply_markup)
#
#         return TOPIC
#
#     def add_category_finish(self, bot, update):
#         categories_table.update({"category": update.message.text},
#                                 {"$set": {"category": update.message.text}},
#                                 upsert=True)
#         buttons = list()
#         buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
#                                              callback_data="help_module(messages)")])
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.send_message(update.message.chat_id,
#                          string_dict(bot)["send_message_15"],
#                          reply_markup=reply_markup)
#         return ConversationHandler.END
#
#
# class MessageCategory(object):
#
#     def show_category(self, bot, update):
#         buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
#                                          callback_data="help_module(messages)"),
#                     InlineKeyboardButton(text=string_dict(bot)["add_message_category"],
#                                          callback_data="add_message_category"),
#                     ]]
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.send_message(update.callback_query.message.chat_id,
#                          string_dict(bot)["send_message_16"], reply_markup=reply_markup)
#
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         categories = categories_table.find()
#         for category in categories:
#             delete_buttons = [[InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
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
#     def delete_category(self, bot, update):
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
#                                          callback_data="help_module(messages)")]]
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         categories_table.delete_one({"category": update.callback_query.data.replace("delete_category_", "")})
#
#         bot.send_message(update.callback_query.message.chat_id,
#                          string_dict(bot)["send_message_17"], reply_markup=reply_markup)
#
#         return ConversationHandler.END


class SendMessageToAdmin(object):

    def send_message(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_back")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        if "anonim" in update.callback_query.data:
            user_data["anonim"] = True
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_from_user_to_admin_anonim_text"],
                             reply_markup=reply_markup)
        else:
            user_data["anonim"] = False
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_from_user_to_admin_text"], reply_markup=reply_markup)

        return MESSAGE

    # def send_topic(self, bot, update, user_data):
    #     bot.send_message(update.message.chat_id,
    #                      random.choice(string_dict(bot)["polls_affirmations"]), reply_markup=ReplyKeyboardRemove())
    #     user_data["topic"] = update.message.text
    #     buttons = list()
    #     buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
    #                                          callback_data="help_back")])
    #     reply_markup = InlineKeyboardMarkup(
    #         buttons)
    #     bot.send_message(update.message.chat_id,
    #                      string_dict(bot)["send_message_1"], reply_markup=reply_markup)
    #
    #     return MESSAGE

    # def send_anonim(self, bot, update, user_data):
    #     bot.send_message(update.message.chat_id,
    #                      random.choice(string_dict(bot)["polls_affirmations"]), reply_markup=ReplyKeyboardRemove())
    #     user_data["anonim"] = update.message.text
    #     buttons = list()
    #     buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
    #                                          callback_data="help_back")])
    #     reply_markup = InlineKeyboardMarkup(
    #         buttons)
    #     bot.send_message(update.message.chat_id,
    #                      string_dict(bot)["send_message_1"], reply_markup=reply_markup)
    #     return MESSAGE

    def received_message(self, bot, update, user_data):

        if "content" not in user_data:
            user_data["content"] = []
        if update.message.text:
            user_data["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            user_data["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            user_data["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            user_data["content"].append({"audio_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            user_data["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            user_data["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.video_note.get_file().file_id
            user_data["content"].append({"video_file": video_note_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Done", callback_data="send_message_finish")],
             [InlineKeyboardButton(text="Cancel", callback_data="help_back")]]
        )
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_4"],
                         reply_markup=final_reply_markup)

        return MESSAGE

    def send_message_finish(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        haikunator = Haikunator()
        if user_data.get("anonim", None) is True:
            user_data["user_full_name"] = "anonim_" + haikunator.haikunate()
            user_data["chat_id"] = update.callback_query.message.chat_id
        else:
            user_data["user_full_name"] = update.callback_query.from_user.mention_markdown()
            user_data["chat_id"] = update.callback_query.message.chat_id
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_5"],
                         reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        if "_id" in user_data:
            user_data.pop("_id", None)
        user_data["timestamp"] = datetime.datetime.now().replace(microsecond=0)
        user_data["user_id"] = update.effective_user.id
        user_data["message_id"] = update.callback_query.message.message_id
        user_data["bot_id"] = bot.id
        users_messages_to_admin_table.insert(user_data)
        user_data.clear()
        return ConversationHandler.END

    def send_message_cancel(self, bot, update, user_data):
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


class SendMessageToUsers(object):

    def send_message(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(messages)")])
        reply_markup = InlineKeyboardMarkup(buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        categories = user_categories_table.find()
        if categories.count() > 0:
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["back_text"],
                             reply_markup=reply_markup)
            categories_list = ["All"] + [x["category"] for x in categories]
            category_markup = ReplyKeyboardMarkup([categories_list])

            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_1_1"],
                             reply_markup=category_markup)
            return CHOOSE_CATEGORY
        else:
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_to_users_text"],
                             reply_markup=reply_markup
                             )
            return MESSAGE_TO_USERS

    def choose_question(self, bot, update, user_data):
        user_data["user_category"] = update.message.text
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(messages)")])
        reply_markup = InlineKeyboardMarkup(buttons)
        bot.send_message(update.message.chat_id,
                         "Cool",
                         reply_markup=ReplyKeyboardRemove())
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_1"],
                         reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    def received_message(self, bot, update, user_data):
        if "content" not in user_data:
            user_data["content"] = []
        if update.message.text:
            user_data["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            user_data["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            user_data["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            user_data["content"].append({"audio_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            user_data["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            user_data["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.video_note.get_file().file_id
            user_data["content"].append({"video_note_file": video_note_file})

        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            user_data["content"].append({"animation_file": animation_file})

        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            user_data["content"].append({"sticker_file": sticker_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=string_dict(bot)["done_button"], callback_data="send_message_finish")],
             [InlineKeyboardButton(text=string_dict(bot)["cancel_button"], callback_data="help_module(messages)")]]
        )
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_4"],
                         reply_markup=final_reply_markup)

        return MESSAGE_TO_USERS

    def send_message_finish(self, bot, update, user_data):  # TODO does not work
        if "user_category" not in user_data:
            chats = users_table.find({"bot_id": bot.id})
        elif user_data["user_category"] == "All":
            chats = users_table.find({"bot_id": bot.id})
        else:
            chats = users_table.find({"bot_id": bot.id, "user_category": user_data["user_category"]})
        for chat in chats:
            if "chat_id" in chat:
                if chat["chat_id"] != update.callback_query.message.chat_id:
                    for content_dict in user_data["content"]:
                        if "text" in content_dict:
                            bot.send_message(chat["chat_id"],
                                             content_dict["text"])
                        if "audio_file" in content_dict:
                            bot.send_audio(chat["chat_id"], content_dict["audio_file"])
                        if "voice_file" in content_dict:
                            bot.send_voice(chat["chat_id"], content_dict["voice_file"])
                        if "video_file" in content_dict:
                            bot.send_video(chat["chat_id"], content_dict["video_file"])
                        if "video_note_file" in content_dict:
                            bot.send_video_note(chat["chat_id"], content_dict["video_note_file"])
                        if "document_file" in content_dict:
                            if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                                bot.send_photo(chat["chat_id"], content_dict["document_file"])
                            else:
                                bot.send_document(chat["chat_id"], content_dict["document_file"])
                        if "photo_file" in content_dict:
                            bot.send_photo(chat["chat_id"], content_dict["photo_file"])
                        if "animation_file" in content_dict:
                            bot.send_animation(chat["chat_id"], content_dict["animation_file"])
                        if "sticker_file" in content_dict:
                            bot.send_sticker(chat["chat_id"], content_dict["sticker_file"])

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(messages)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_5"],
                         reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        user_data.clear()

        return ConversationHandler.END

    def send_message_cancel(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(messages)")])
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


class AnswerToMessage(object):

    def send_message(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(messages)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        user_data["message_id"] = update.callback_query.data.replace("answer_to_message_", "")
        user = users_messages_to_admin_table.find_one(
            {"message_id": int(user_data["message_id"])})
        user_data["chat_id"] = user["chat_id"]

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_3"],
                         reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    def received_message(self, bot, update, user_data):
        if "content" not in user_data:
            user_data["content"] = []
        if update.message.text:
            user_data["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            user_data["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            user_data["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            user_data["content"].append({"audio_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            user_data["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            user_data["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.video_note.get_file().file_id
            user_data["content"].append({"video_note_file": video_note_file})

        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            user_data["content"].append({"animation_file": animation_file})

        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            user_data["content"].append({"sticker_file": sticker_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=string_dict(bot)["done_button"], callback_data="send_message_finish")],
             [InlineKeyboardButton(text=string_dict(bot)["cancel_button"], callback_data="help_module(messages)")]]
        )
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_4"],
                         reply_markup=final_reply_markup)

        return MESSAGE_TO_USERS

    def send_message_finish(self, bot, update, user_data):
        # user_name = bot.get_chat_member(user_data["chat_id"]).user.mention_markdown()

        bot.send_message(user_data["chat_id"],
                         text=string_dict(bot)["send_message_answer_user"])
        for content_dict in user_data["content"]:
            if "text" in content_dict:
                bot.send_message(user_data["chat_id"],
                                 content_dict["text"])
            if "audio_file" in content_dict:
                bot.send_audio(user_data["chat_id"], content_dict["audio_file"])
            if "voice_file" in content_dict:
                bot.send_voice(user_data["chat_id"], content_dict["voice_file"])
            if "video_file" in content_dict:
                bot.send_video(user_data["chat_id"], content_dict["video_file"])
            if "video_note_file" in content_dict:
                bot.send_video_note(user_data["chat_id"], content_dict["video_note_file"])
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    bot.send_photo(user_data["chat_id"], content_dict["document_file"])
                else:
                    bot.send_document(user_data["chat_id"], content_dict["document_file"])
            if "photo_file" in content_dict:
                bot.send_photo(user_data["chat_id"], content_dict["photo_file"])
            if "animation_file" in content_dict:
                bot.send_animation(user_data["chat_id"], content_dict["animation_file"])
            if "sticker_file" in content_dict:
                bot.send_sticker(user_data["chat_id"], content_dict["sticker_file"])

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(messages)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_5"],
                         reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        user_data.clear()

        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END


class DeleteMessage(object):
    # def delete_message_double_check(self, bot, update):  #TODO
    #     buttons = list()
    #     buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
    #                                          callback_data="help_module(messages)")])
    #     reply_markup = InlineKeyboardMarkup(
    #         buttons)
    #     bot.delete_message(chat_id=update.callback_query.message.chat_id,
    #                        message_id=update.callback_query.message.message_id)

    def delete_message(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_module(messages)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        messages = users_messages_to_admin_table.find({"bot_id": bot.id})
        if messages.count() > 0:
            message_id = update.callback_query.data.replace("delete_message_", "")  # message_id
            if any(x in message_id for x in ["all", "week", "month"]):
                buttons = [[InlineKeyboardButton(text=string_dict(bot)["yes"],
                                                 callback_data="trash_messages_" + message_id),
                            InlineKeyboardButton(text=string_dict(bot)["no"],
                                                 callback_data="help_module(messages)")]]
                reply_markup = InlineKeyboardMarkup(
                    buttons)
                bot.send_message(update.callback_query.message.chat_id,
                                 string_dict(bot)["delete_messages_double_check"],
                                 reply_markup=reply_markup)
                user_data["message_id"] = message_id
                return DOUBLE_CHECK  # TODO send a keyboard with callback depending on previous callback data
            else:
                users_messages_to_admin_table.delete_one({"bot_id": bot.id, "message_id": int(message_id)})
                bot.send_message(update.callback_query.message.chat_id,
                                 string_dict(bot)["delete_message_str_1"],
                                 reply_markup=reply_markup)
                return ConversationHandler.END
        else:
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_6"],
                             reply_markup=reply_markup)
            return ConversationHandler.END

    def delete_message_double_check(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_module(messages)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)

        if "all" in user_data["message_id"]:
            users_messages_to_admin_table.delete_many({"bot_id": bot.id})  # delete all messages from the users
        elif "week" in user_data["message_id"]:
            time_past = datetime.datetime.now() - datetime.timedelta(days=7)
            users_messages_to_admin_table.delete_many({"bot_id": bot.id,
                                                       "timestamp": {'$gt': time_past}})
            # delete all messages from the users for last week

        elif "month" in user_data["message_id"]:
            # delete all messages from the users for last month
            time_past = datetime.datetime.now() - datetime.timedelta(days=30)
            users_messages_to_admin_table.delete_many({"bot_id": bot.id,
                                                       "timestamp": {'$gt': time_past}})
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["delete_message_str_1"],
                         reply_markup=reply_markup)
        return ConversationHandler.END


class SeeMessageToAdmin(object):

    def see_messages(self, bot, update, user_data):
        user_data["to_delete"] = []
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="inbox_back")])
        delete_buttons = buttons
        delete_buttons.append([InlineKeyboardButton(text=string_dict(bot)["delete_button_str_all"],
                                                    callback_data="delete_message_all")
                               ])
        delete_buttons.append([InlineKeyboardButton(text=string_dict(bot)["delete_button_str_last_week"],
                                                    callback_data="delete_message_week"),
                               InlineKeyboardButton(text=string_dict(bot)["delete_button_str_last_month"],
                                                    callback_data="delete_message_month")
                               ])
        delete_markup = InlineKeyboardMarkup(
            delete_buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        messages = users_messages_to_admin_table.find({"bot_id": bot.id})

        if messages.count() != 0:
            for message in messages:
                if message["timestamp"] + datetime.timedelta(days=14) > datetime.datetime.now():
                    if message["anonim"] is False:
                        user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat_id,
                                                                       "User's name: {}, \n\nTime: {}".format(
                                                                           message["user_full_name"],
                                                                           message["timestamp"].strftime(
                                                                               '%d, %b %Y, %H:%M'),
                                                                           # message["topic"] \n\nTopic {}
                                                                       ),
                                                                       reply_markup=InlineKeyboardMarkup(
                                                                           [[InlineKeyboardButton(
                                                                               text=string_dict(bot)[
                                                                                   "view_message_str"],
                                                                               callback_data="view_message_" +
                                                                                             str(message[
                                                                                                     "message_id"]))]
                                                                           ]
                                                                       ),
                                                                       parse_mode=ParseMode.MARKDOWN))
                    else:
                        user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat_id,
                                                                       "User's name: {}, \n\nTime: {}".format(
                                                                           message["user_full_name"],
                                                                           message["timestamp"].strftime(
                                                                               '%d, %b %Y, %H:%M'),
                                                                           # message["topic"] \n\nTopic {}
                                                                       ),
                                                                       reply_markup=InlineKeyboardMarkup(
                                                                           [[InlineKeyboardButton(
                                                                               text=string_dict(bot)[
                                                                                   "view_message_str"],
                                                                               callback_data="view_message_" +
                                                                                             str(message["message_id"]))
                                                                           ]
                                                                           ]
                                                                       )))
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat_id,
                                                           string_dict(bot)["back_text"], reply_markup=delete_markup))
        else:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                                 callback_data="help_module(messages)")]])
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_6"], reply_markup=markup)

        return ConversationHandler.END

    def view_message(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        delete_messages(bot, update, user_data)
        query = update.callback_query
        message = users_messages_to_admin_table.find_one({"bot_id": bot.id,
                                                          "message_id": int(query.data.replace("view_message_", ""))})

        for content_dict in message["content"]:
            if "text" in content_dict:
                user_data["to_delete"].append(query.message.reply_text(text=content_dict["text"]))
            if "audio_file" in content_dict:
                user_data["to_delete"].append(query.message.reply_audio(content_dict["audio_file"]))
            if "voice_file" in content_dict:
                user_data["to_delete"].append(query.message.reply_audio(content_dict["voice_file"]))
            if "video_file" in content_dict:
                user_data["to_delete"].append(query.message.reply_video(content_dict["video_file"]))
            if "video_note_file" in content_dict:
                user_data["to_delete"].append(query.message.reply_video_note(content_dict["video_note_file"]))
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    user_data["to_delete"].append(query.message.reply_photo(photo=content_dict["document_file"]))
                else:
                    user_data["to_delete"].append(query.message.reply_document(document=content_dict["document_file"]))
            if "photo_file" in content_dict:
                user_data["to_delete"].append(query.message.reply_photo(photo=content_dict["photo_file"]))
            if "animation_file" in content_dict:
                user_data["to_delete"].append(query.message.reply_animation(photo=content_dict["animation_file"]))
            if "sticker_file" in content_dict:
                user_data["to_delete"].append(query.message.reply_sticker(photo=content_dict["sticker_file"]))
        user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat_id,
                                                       "User's name: {}, \n Timestamp:{}".format(
                                                           message["user_full_name"],
                                                           message["timestamp"]
                                                       ),
                                                       reply_markup=InlineKeyboardMarkup(
                                                           [[InlineKeyboardButton(
                                                               text=string_dict(bot)["answer_button_str"],
                                                               callback_data="answer_to_message_" +
                                                                             str(message["message_id"]))],
                                                               [InlineKeyboardButton(
                                                                   text=string_dict(bot)["delete_button_str"],
                                                                   callback_data="delete_message_" +
                                                                                 str(message["message_id"]))],
                                                               [InlineKeyboardButton(
                                                                   text=string_dict(bot)["block_button_str"],
                                                                   callback_data="block_user_" +
                                                                                 str(message["user_id"]))],

                                                           ]
                                                       )))
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["back_text"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="view_back_message")]]))
        return ConversationHandler.END

    def blocked_users_list(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        blocked_users = users_table.find({"bot_id": bot.id, "blocked": True})
        for user in blocked_users:
            bot.send_message(update.callback_query.message.chat_id, "{}\n".format(user["full_name"]),
                             InlineKeyboardMarkup([[InlineKeyboardButton(text="UNBLOCK",
                                                                         callback_data="unblock_{}".format(
                                                                             user["user_id"]))]])
                             )
        bot.send_message(update.callback_query.message.chat_id, "This is the list of all blocked users",
                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                                                 callback_data="help_module(users)")]]))

    def unblock(self, bot, update):
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(messages)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)

        user_id = update.callback_query.data.replace("unblock_", "")
        user = users_table.find_one({"user_id": user_id})
        user["blocked"] = False
        users_table.update({"user_id": user_id}, user)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat_id, "User has been removed from the blacklist",
                         reply_markup=final_reply_markup)
        return ConversationHandler.END

    def block_user(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        user_data["user_id"] = int(update.callback_query.data.replace("block_user_", ""))
        bot.send_message(update.callback_query.message.chat_id, "Are you sure that you want to block this user? \n"
                                                                "He won't be able to use this chatbot anymore",
                         reply_markup=ReplyKeyboardMarkup([["YES", "NO"]], one_time_keyboard=True))
        return BLOCK_CONFIRMATION

    def block_confirmation(self, bot, update, user_data):
        user = users_table.find_one({"user_id": user_data["user_id"]})
        user["blocked"] = True
        users_table.update({"user_id": user_data["user_id"]}, user)
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                             callback_data="inbox_message")]])
        if update.message.text == "YES":
            bot.send_message(update.message.chat_id, "User {} has been blocked".format(
                user_data["user_name"], reply_markup=markup
            ))
        else:
            bot.send_message(update.message.chat_id, "Blocking has been canceled", reply_markup=markup)
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        delete_messages(bot, update, user_data)
        get_help(bot, update)
        return ConversationHandler.END


MESSAGES_MENU = CallbackQueryHandler(callback=messages_menu, pattern="admin_messages")
DOUBLE_CHECK = 1
DELETE_MESSAGES_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="delete_message",
                                       callback=DeleteMessage().delete_message,
                                       pass_user_data=True)],
    states={DOUBLE_CHECK: [CallbackQueryHandler(pattern="trash_messages_",
                                                callback=DeleteMessage().delete_message_double_check,
                                                pass_user_data=True)]},
    fallbacks=[
        CallbackQueryHandler(SendMessageToUsers().send_message_cancel,
                             pattern="help_back",
                             pass_user_data=True)
    ]
)

SEND_MESSAGE_TO_ADMIN_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_admin",
                                       callback=SendMessageToAdmin().send_message,
                                       pass_user_data=True),
                  ],

    states={
        MESSAGE: [MessageHandler(Filters.all, SendMessageToAdmin().received_message, pass_user_data=True), ],
        # TOPIC: [MessageHandler(Filters.all, SendMessageToAdmin().send_topic, pass_user_data=True), ]
        # SEND_ANONIM: [MessageHandler(Filters.all, SendMessageToAdmin().send_anonim, pass_user_data=True), ]

    },

    fallbacks=[
        CallbackQueryHandler(callback=SendMessageToAdmin().send_message_finish,
                             pattern=r"send_message_finish", pass_user_data=True),
        CallbackQueryHandler(SendMessageToUsers().send_message_cancel,
                             pattern="help_back",
                             pass_user_data=True),
    ]
)

SEND_MESSAGE_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_users",
                                       callback=SendMessageToUsers().send_message)],

    states={
        CHOOSE_CATEGORY: [MessageHandler(Filters.all, SendMessageToUsers().choose_question, pass_user_data=True)],
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendMessageToUsers().received_message, pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=SendMessageToUsers().send_message_finish,
                             pattern=r"send_message_finish", pass_user_data=True),
        CallbackQueryHandler(pattern=r"help_module",
                             callback=SendMessageToUsers().send_message_cancel,
                             pass_user_data=True),
        CallbackQueryHandler(pattern=r"help_back",
                             callback=SendMessageToUsers().send_message_cancel,
                             pass_user_data=True),
    ]
)

SEE_MESSAGES_HANDLER = CallbackQueryHandler(pattern="inbox_message", callback=SeeMessageToAdmin().see_messages,
                                            pass_user_data=True)
SEE_MESSAGES_BACK_HANDLER = CallbackQueryHandler(pattern="inbox_back", callback=SeeMessageToAdmin().back,
                                                 pass_user_data=True)
SEE_MESSAGES_FINISH_HANDLER = CallbackQueryHandler(pattern="view_message_",
                                                   callback=SeeMessageToAdmin().view_message, pass_user_data=True)
SEE_MESSAGES_FINISH_BACK_HANDLER = CallbackQueryHandler(pattern="view_back_message",
                                                        callback=SeeMessageToAdmin().back, pass_user_data=True)

ANSWER_TO_MESSAGE_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern=r"answer_to_message",
                                       callback=AnswerToMessage().send_message, pass_user_data=True)],

    states={
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, AnswerToMessage().received_message, pass_user_data=True)],

    },

    fallbacks=[CallbackQueryHandler(callback=AnswerToMessage().send_message_finish,
                                    pattern=r"send_message_finish",
                                    pass_user_data=True),
               CallbackQueryHandler(callback=AnswerToMessage().back,
                                    pattern=r"help_module",
                                    pass_user_data=True),
               CallbackQueryHandler(callback=AnswerToMessage().back,
                                    pattern=r"help_back",
                                    pass_user_data=True),
               ]
)
BLOCK_USER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="block_user",
                                       callback=SeeMessageToAdmin().block_user,
                                       pass_user_data=True),
                  ],

    states={
        BLOCK_CONFIRMATION: [
            MessageHandler(Filters.all, SeeMessageToAdmin().block_confirmation, pass_user_data=True), ],
        # TOPIC: [MessageHandler(Filters.all, SendMessageToAdmin().send_topic, pass_user_data=True), ]
        # SEND_ANONIM: [MessageHandler(Filters.all, SendMessageToAdmin().send_anonim, pass_user_data=True), ]

    },

    fallbacks=[
        CallbackQueryHandler(SendMessageToUsers().send_message_cancel,
                             pattern="help_back",
                             pass_user_data=True),
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
