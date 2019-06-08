# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler)
from database import users_messages_to_admin_table, chats_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.strings import send_message_1, send_message_2, send_message_3, send_message_4, send_message_5, \
    send_message_6, send_message_button_1, send_message_button_2, send_message_admin, send_message_user, \
    send_message_module_str, back_text

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1
MESSAGE_TO_USERS = 1


class SendMessageToAdmin(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_message")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def send_message(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         send_message_1, reply_markup=self.reply_markup)
        return MESSAGE

    @run_async
    def received_message(self, bot, update):
        bot.send_message(update.message.chat_id,
                         send_message_2)
        users_messages_to_admin_table.insert({"user_full_name": update.message.from_user.full_name,
                                              "chat_id": update.message.chat_id,
                                              "user_id": update.message.from_user.id,
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
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_message")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def send_message(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         send_message_3,
                         reply_markup=self.reply_markup)
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
                         send_message_4,
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
                         send_message_5,
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


class SeeMessageToAdmin(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="help_back")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def see_messages(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        messages = users_messages_to_admin_table.find({"bot_id": bot.id})

        if messages.count() != 0:
            for message in messages:
                if message["timestamp"] + datetime.timedelta(days=14) > datetime.datetime.now():
                    bot.send_message(update.callback_query.message.chat.id,
                                     "User's name: {}, \n\n"
                                     "Message: {}".format(message["user_full_name"],
                                                          message["message"]))

        else:
            bot.send_message(update.callback_query.message.chat.id,
                             send_message_6)
        bot.send_message(update.callback_query.message.chat.id,
                         back_text, reply_markup=self.reply_markup)


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
               CommandHandler('cancel', SendMessageToAdmin().error),
               MessageHandler(filters=Filters.command, callback=SendMessageToAdmin().error)]
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
               CommandHandler('cancel', SendMessageToUsers().error),
               MessageHandler(filters=Filters.command, callback=SendMessageToUsers().error)]
)

SEE_MESSAGES_HANDLER = CallbackQueryHandler(pattern="inbox_message", callback=SeeMessageToAdmin().see_messages)

__mod_name__ = send_message_module_str
__visitor_help__ = send_message_user

__visitor_keyboard__ = [InlineKeyboardButton(text=send_message_button_1,
                                             callback_data="send_message_to_admin")]

__admin_help__ = send_message_admin

__admin_keyboard__ = [
    InlineKeyboardButton(text=send_message_button_1, callback_data="send_message_to_users"),
    InlineKeyboardButton(text=send_message_button_2, callback_data="inbox_message"),
]
