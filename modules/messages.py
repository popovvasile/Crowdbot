# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
from database import users_messages_to_admin_table, chats_table, categories_table, user_categories_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TOPIC, MESSAGE = range(2)
CHOOSE_CATEGORY, MESSAGE_TO_USERS = range(2)


class AddMessageCategory(object):

    def add_category(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="cancel_send_message")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_14"], reply_markup=reply_markup)

        return TOPIC

    def add_category_finish(self, bot, update):
        categories_table.update({"category": update.message.text},
                                {"$set": {"category": update.message.text}},
                                upsert=True)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(messages)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_15"],
                         reply_markup=reply_markup)
        return ConversationHandler.END


class MessageCategory(object):

    def show_category(self, bot, update):
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_module(messages)"),
                    InlineKeyboardButton(text=string_dict(bot)["add_message_category"],
                                         callback_data="add_message_category"),
                    ]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_16"], reply_markup=reply_markup)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        categories = categories_table.find()
        for category in categories:
            delete_buttons = [[InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                    callback_data="delete_category_{}"
                                                    .format(category["category"]))]]
            delete_markup = InlineKeyboardMarkup(
                delete_buttons)
            bot.send_message(update.callback_query.message.chat_id, category["category"],
                             reply_markup=delete_markup)

        return ConversationHandler.END


class DeleteMessageCategory(object):

    def delete_category(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                         callback_data="help_module(messages)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        categories_table.delete_one({"category": update.callback_query.data.replace("delete_category_", "")})

        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_17"], reply_markup=reply_markup)

        return ConversationHandler.END


class SendMessageToAdmin(object):

    def send_message(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="cancel_send_message")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_12"], reply_markup=reply_markup)
        # categories = categories_table.find()
        # if categories.count() > 0:
        #     bot.send_message(update.callback_query.message.chat_id,
        #                      string_dict(bot)["send_message_13"],
        #                      reply_markup=ReplyKeyboardMarkup([[
        #                          x["category"]] for x in categories
        #                      ]))
        #
        # else:
        #     bot.send_message(update.callback_query.message.chat_id,
        #                      string_dict(bot)["send_message_13"])

        return MESSAGE

    def send_topic(self, bot, update, user_data):
        bot.send_message(update.message.chat_id,
                         random.choice(string_dict(bot)["polls_affirmations"]), reply_markup=ReplyKeyboardRemove())
        user_data["topic"] = update.message.text
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="cancel_send_message")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_1"], reply_markup=reply_markup)

        return MESSAGE

    def received_message(self, bot, update, user_data):
        user_data["user_full_name"] = update.message.from_user.full_name
        user_data["user_id"] = update.message.from_user.id
        user_data["chat_id"] = update.message.chat_id
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
            video_note_file = update.message.audio.get_file().file_id
            user_data["content"].append({"video_file": video_note_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Done", callback_data="send_message_finish")]]
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
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_5"],
                         reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        if "_id" in user_data:
            user_data.pop("_id", None)
        user_data["timestamp"] = datetime.datetime.now()
        user_data["message_id"] = update.callback_query.message.message_id
        user_data["bot_id"] = bot.id
        print(user_data)
        users_messages_to_admin_table.insert(user_data)
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
                                             callback_data="cancel_send_message")])
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
                             string_dict(bot)["send_message_4"],
                             reply_markup=reply_markup
                             )
            return MESSAGE_TO_USERS

    def choose_question(self, bot, update, user_data):
        user_data["user_category"] = update.message.text
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="cancel_send_message")])
        reply_markup = InlineKeyboardMarkup(buttons)
        bot.send_message(update.message.chat_id,
                         "Cool",
                         reply_markup=ReplyKeyboardRemove())
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_1"],
                         reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    def received_message(self, bot, update, user_data):
        if "user_category" not in user_data:
            chats = chats_table.find({"bot_id": bot.id})
        elif user_data["user_category"] == "All":
            chats = chats_table.find({"bot_id": bot.id})
        else:
            chats = chats_table.find({"bot_id": bot.id, "user_category": user_data["user_category"]})
        for chat in chats:
            if chat["chat_id"] != update.message.chat_id:
                if update.message.text:
                    bot.send_message(chat["chat_id"], update.message.text)

                elif update.message.photo:
                    photo_file = update.message.photo[0].get_file().file_id
                    bot.send_photo(chat_id=chat["chat_id"], photo=photo_file)

                elif update.message.audio:
                    audio_file = update.message.audio.get_file().file_id
                    bot.send_audio(chat["chat_id"], audio_file)

                elif update.message.voice:
                    voice_file = update.message.voice.get_file().file_id
                    bot.send_voice(chat["chat_id"], voice_file)

                elif update.message.document:
                    document_file = update.message.document.get_file().file_id
                    bot.send_document(chat["chat_id"], document_file)

                elif update.message.sticker:
                    sticker_file = update.message.sticker.get_file().file_id
                    bot.send_sticker(chat["chat_id"], sticker_file)

                elif update.message.game:
                    sticker_file = update.message.game.get_file().file_id
                    bot.send_game(chat["chat_id"], sticker_file)

                elif update.message.animation:
                    animation_file = update.message.animation.get_file().file_id
                    bot.send_animation(chat["chat_id"], animation_file)

                elif update.message.video:
                    video_file = update.message.video.get_file().file_id
                    bot.send_video(chat["chat_id"], video_file)

                elif update.message.video_note:
                    video_note_file = update.message.audio.get_file().file_id
                    bot.send_video_note(chat["chat_id"], video_note_file)

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Done", callback_data="send_message_finish")]]
        )
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_4"],
                         reply_markup=final_reply_markup)

        return MESSAGE_TO_USERS

    def send_message_finish(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(messages)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_5"],
                         reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END


class AnswerToMessage(object):

    def send_message(self, bot, update, user_data):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="cancel_send_message")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        user_data["message_id"] = update.callback_query.data.replace("answer_to_message_", "")
        user_data["chat_id"] = users_messages_to_admin_table.find_one(
            {"message_id": int(user_data["message_id"])})["chat_id"]

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_3"],
                         reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    def received_message(self, bot, update, user_data):
        if update.message.text:
            bot.send_message(user_data["chat_id"], update.message.text)

        elif update.message.photo:
            photo_file = update.message.photo[0].get_file().file_id
            bot.send_photo(chat_id=user_data["chat_id"], photo=photo_file)

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            bot.send_audio(user_data["chat_id"], audio_file)

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            bot.send_voice(user_data["chat_id"], voice_file)

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            bot.send_document(user_data["chat_id"], document_file)

        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            bot.send_sticker(user_data["chat_id"], sticker_file)

        elif update.message.game:
            sticker_file = update.message.game.get_file().file_id
            bot.send_game(user_data["chat_id"], sticker_file)

        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            bot.send_animation(user_data["chat_id"], animation_file)

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            bot.send_video(user_data["chat_id"], video_file)

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            bot.send_video_note(user_data["chat_id"], video_note_file)

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Done", callback_data="answer_to_message_finish")]]
        )
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_4"],
                         reply_markup=final_reply_markup)

        return MESSAGE_TO_USERS

    def send_message_finish(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(messages)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_5"],
                         reply_markup=final_reply_markup)
        ask_if_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                   callback_data="delete_message_" +
                                                 str(user_data["message_id"]))
              ]]
        )
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_6"],
                         reply_markup=ask_if_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END


class DeleteMessage(object):

    def delete_message(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(messages)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        message_id = update.callback_query.data.replace("delete_message_", "")  # message_id
        if message_id == "all":
            users_messages_to_admin_table.delete_many({"bot_id": bot.id})  # delete all messages from the users
        elif message_id == "week":
            time_past = datetime.datetime.now() - datetime.timedelta(days=7)
            users_messages_to_admin_table.delete_many({"bot_id": bot.id,
                                                       "timestamp": {'$gt': time_past}})
            # delete all messages from the users
        elif message_id == "month":
            time_past = datetime.datetime.now() - datetime.timedelta(days=30)

            users_messages_to_admin_table.delete_many({"bot_id": bot.id,
                                                       "timestamp": {'$gt': time_past}})
            # delete all messages from the users
        else:
            users_messages_to_admin_table.delete_one({"bot_id": bot.id, "message_id": int(message_id)})
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["delete_message_str_1"],
                         reply_markup=reply_markup)
        return ConversationHandler.END


class SeeMessageToAdmin(object):

    def see_messages(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(messages)")])
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
                    bot.send_message(update.callback_query.message.chat_id,
                                     "User's name: {}, \n\nTime: {}".format(
                                         message["user_full_name"],
                                         message["timestamp"].strftime('%d, %b %Y, %H:%M'),
                                         # message["topic"] \n\nTopic {}
                                     ),
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text=string_dict(bot)["view_message_str"],
                                                                callback_data="view_message_" +
                                                                              str(message["message_id"]))]
                                          ]
                                     ))
        else:
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_6"])
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["back_text"], reply_markup=delete_markup)
        return ConversationHandler.END

    def view_message(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        query = update.callback_query
        message = users_messages_to_admin_table.find_one({"bot_id": bot.id,
                                                          "message_id": int(query.data.replace("view_message_", ""))})
        for content_dict in message["content"]:
            if "text" in content_dict:
                query.message.reply_text(text=content_dict["text"])
            if "audio_file" in content_dict:
                query.message.reply_audio(content_dict["audio_file"])
            if "video_file" in content_dict:
                query.message.reply_video(content_dict["video_file"])
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    query.message.reply_photo(photo=content_dict["document_file"])
                else:
                    query.message.reply_document(document=content_dict["document_file"])
            if "photo_file" in content_dict:
                query.message.reply_photo(photo=content_dict["photo_file"])
        bot.send_message(update.callback_query.message.chat_id,
                         "User's name: {}, \n Timestamp:{}".format(
                             message["user_full_name"],
                             message["timestamp"]
                         ),
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["answer_button_str"],
                                                    callback_data="answer_to_message_" +
                                                                  str(message["message_id"]))],
                              [InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                    callback_data="delete_message_" +
                                                                  str(message["message_id"]))],

                              ]
                         ))
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["back_text"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(messages)")]]))
        return ConversationHandler.END


DELETE_MESSAGES_HANDLER = CallbackQueryHandler(pattern="delete_message",
                                               callback=DeleteMessage().delete_message)

SEND_MESSAGE_TO_ADMIN_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_admin",
                                       callback=SendMessageToAdmin().send_message),
                  ],

    states={
        MESSAGE: [MessageHandler(Filters.all, SendMessageToAdmin().received_message, pass_user_data=True), ],
        TOPIC: [MessageHandler(Filters.all, SendMessageToAdmin().send_topic, pass_user_data=True), ]

    },

    fallbacks=[
        CallbackQueryHandler(callback=SendMessageToAdmin().send_message_finish,
                             pattern=r"send_message_finish", pass_user_data=True),
        CallbackQueryHandler(callback=SendMessageToAdmin().back,
                             pattern=r"cancel_send_message"),
        CallbackQueryHandler(callback=AnswerToMessage().back, pattern=r"error_back"),

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
        CallbackQueryHandler(callback=SendMessageToUsers().back,
                             pattern=r"cancel_send_message"),
        CallbackQueryHandler(callback=SendMessageToUsers().send_message_finish,
                             pattern=r"send_message_finish"),
        CallbackQueryHandler(callback=AnswerToMessage().back, pattern=r"error_back"),

    ]
)

MESSAGE_CATEGORY_HANDLER = CallbackQueryHandler(pattern="show_message_categories",
                                                callback=MessageCategory().show_category)
DELETE_MESSAGE_CATEGORY_HANDLER = CallbackQueryHandler(pattern="delete_category_",
                                                       callback=DeleteMessageCategory().delete_category)
ADD_MESSAGE_CATEGORY_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="add_message_category",
                                       callback=AddMessageCategory().add_category)],

    states={
        TOPIC: [MessageHandler(Filters.all, AddMessageCategory().add_category_finish)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=SendMessageToUsers().back,
                             pattern=r"cancel_send_message"),
        CallbackQueryHandler(callback=AnswerToMessage().back, pattern=r"error_back"),

    ]
)

SEE_MESSAGES_HANDLER = CallbackQueryHandler(pattern="inbox_message", callback=SeeMessageToAdmin().see_messages)
SEE_MESSAGES_FINISH_HANDLER = CallbackQueryHandler(pattern="view_message_",
                                                   callback=SeeMessageToAdmin().view_message)

ANSWER_TO_MESSAGE_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern=r"answer_to_message",
                                       callback=AnswerToMessage().send_message, pass_user_data=True)],

    states={
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, AnswerToMessage().received_message, pass_user_data=True)],

    },

    fallbacks=[CallbackQueryHandler(callback=AnswerToMessage().send_message_finish,
                                    pattern=r"answer_to_message_finish",
                                    pass_user_data=True),
               CallbackQueryHandler(callback=AnswerToMessage().back,
                                    pattern=r"cancel_send_message",
                                    pass_user_data=True),
               CallbackQueryHandler(callback=AnswerToMessage().back, pattern=r"error_back"),

               ]
)
