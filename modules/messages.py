# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, run_async, CallbackQueryHandler)
from database import users_messages_to_admin_table, chats_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1
MESSAGE_TO_USERS = 1


class SendMessageToAdmin(object):  # TODO save messages that contain files
    @run_async
    def send_message(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_message")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["send_message_1"], reply_markup=reply_markup)
        return MESSAGE

    @run_async
    def received_message(self, bot, update):
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_message_2"])
        users_messages_to_admin_table.insert({"user_full_name": update.message.from_user.full_name,
                                              "chat_id": update.message.chat_id,
                                              "user_id": update.message.from_user.id,
                                              "message_id": update.message.message_id,
                                              "message": update.message.text,
                                              "timestamp": datetime.datetime.now(),
                                              "bot_id": bot.id})
        get_help(bot, update)
        return ConversationHandler.END

    @run_async
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
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


class SendMessageToUsers(object):
    @run_async
    def send_message(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_message")])
        reply_markup = InlineKeyboardMarkup(buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["send_message_3"],
                         reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    @run_async
    def received_message(self, bot, update):
        chats = chats_table.find({"bot_id": bot.id})
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
        buttons.append([InlineKeyboardButton(text="Back", callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_5"],
                         reply_markup=final_reply_markup)
        chats = chats_table.find({"bot_id": bot.id})
        for chat in chats:
            if chat["chat_id"] != update.callback_query.message.chat_id:
                bot.send_message(chat["chat_id"],
                                 "Click here for menu",
                                 reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END

    @run_async
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
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


class AnswerToMessage(object):
    @run_async
    def send_message(self, bot, update, user_data):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_message")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        user_data["chat_id"] = update.callback_query.data.replace("answer_to_message_", "")  # chat_id
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["send_message_3"],
                         reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    @run_async
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
        buttons.append([InlineKeyboardButton(text="Back", callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_5"],
                         reply_markup=final_reply_markup)

        logger.info("Admin {} on bot {}:{} sent a message to the users".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END

    @run_async
    def error(self, bot, update, error, user_data):
        """Log Errors caused by Updates."""
        bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    def cancel(self, bot, update, user_data):
        update.message.reply_text(
            "Command is cancelled =("
        )

        get_help(bot, update)
        return ConversationHandler.END


class DeleteMessage(object):
    @run_async
    def delete_message(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="help_back")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        message_id = update.callback_query.data.replace("delete_message_", "")  # message_id
        if message_id == "all":
            users_messages_to_admin_table.delete_many({"bot_id": bot.id})  # delete all messages from the users
        elif message_id == "week":
            time_past = datetime.datetime.now() - datetime.timedelta(days=7)
            users_messages_to_admin_table.delete_many({"bot_id": bot,
                                                       "timestamp": {'$gt': time_past}})
            # delete all messages from the users
        elif message_id == "month":
            time_past = datetime.datetime.now() - datetime.timedelta(days=30)

            users_messages_to_admin_table.delete_many({"bot_id": bot.id,
                                                       "timestamp": {'$gt': time_past}})
            # delete all messages from the users
        else:
            print(bot.id)
            print(message_id)
            users_messages_to_admin_table.delete_one({"bot_id": bot.id, "message_id": int(message_id)})
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["delete_message_str_1"],
                         reply_markup=reply_markup)
        return ConversationHandler.END


class SeeMessageToAdmin(object):
    @run_async
    def see_messages(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")])
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
                    bot.send_message(update.callback_query.message.chat.id,
                                     "User's name: {}, \n\n"
                                     "Message: {}".format(message["user_full_name"],
                                                          message["message"]),
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text=string_dict(bot)["answer_button_str"],
                                                                callback_data="answer_to_message_" +
                                                                              str(message["chat_id"]))],
                                          [InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                                callback_data="delete_message_" +
                                                                              str(message["message_id"]))]
                                          ]
                                     ))  # TODO recheck

        else:
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["send_message_6"])
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["back_text"], reply_markup=delete_markup)


DELETE_MESSAGES_HANDLER = CallbackQueryHandler(pattern="delete_message",
                                               callback=DeleteMessage().delete_message)

SEND_MESSAGE_TO_ADMIN_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_admin",
                                       callback=SendMessageToAdmin().send_message),
                  CallbackQueryHandler(callback=SendMessageToUsers().back,
                                       pattern=r"cancel_send_message")],

    states={
        MESSAGE: [MessageHandler(Filters.all, SendMessageToAdmin().received_message),
                  CallbackQueryHandler(callback=SendMessageToUsers().back,
                                       pattern=r"cancel_send_message")],

    },

    fallbacks=[
        CallbackQueryHandler(callback=SendMessageToUsers().back,
                             pattern=r"cancel_send_message"),
        CommandHandler('cancel', SendMessageToUsers().back),
        MessageHandler(filters=Filters.command, callback=SendMessageToUsers().back)]
)

SEND_MESSAGE_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_message_to_users",
                                       callback=SendMessageToUsers().send_message),
                  CallbackQueryHandler(callback=SendMessageToUsers().back,
                                       pattern=r"cancel_send_message")],

    states={
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendMessageToUsers().received_message),
                           CallbackQueryHandler(callback=SendMessageToUsers().back,
                                                pattern=r"cancel_send_message")],

    },

    fallbacks=[CallbackQueryHandler(callback=SendMessageToUsers().send_message_finish,
                                    pattern=r"send_message_finish"),
               CallbackQueryHandler(callback=SendMessageToUsers().back,
                                    pattern=r"cancel_send_message"),
               CommandHandler('cancel', SendMessageToUsers().back),
               MessageHandler(filters=Filters.command, callback=SendMessageToUsers().back)]
)

SEE_MESSAGES_HANDLER = CallbackQueryHandler(pattern="inbox_message", callback=SeeMessageToAdmin().see_messages)

ANSWER_TO_MESSAGE_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern=r"answer_to_message",
                                       callback=AnswerToMessage().send_message, pass_user_data=True),
                  CallbackQueryHandler(callback=AnswerToMessage().back,
                                       pattern=r"cancel_send_message", pass_user_data=True)],

    states={
        MESSAGE_TO_USERS: [MessageHandler(Filters.all, AnswerToMessage().received_message, pass_user_data=True),
                           CallbackQueryHandler(callback=AnswerToMessage().back,
                                                pattern=r"cancel_send_message", pass_user_data=True)],

    },

    fallbacks=[CallbackQueryHandler(callback=AnswerToMessage().send_message_finish,
                                    pattern=r"answer_to_message_finish",
                                    pass_user_data=True),
               CallbackQueryHandler(callback=AnswerToMessage().back,
                                    pattern=r"cancel_send_message",
                                    pass_user_data=True),
               CommandHandler('cancel', AnswerToMessage().back,
                              pass_user_data=True),
               MessageHandler(filters=Filters.command,
                              callback=AnswerToMessage().back,
                              pass_user_data=True)]
)


