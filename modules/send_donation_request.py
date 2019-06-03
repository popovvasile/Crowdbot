# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, run_async, CallbackQueryHandler)
from database import chats_table
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
DONATION_TO_USERS, DONATION_TO_USERS_FINISH = range(2)


class SendDonationToUsers(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_donation")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def send_donation(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         "What do you want to tell your users?\n"
                         "We will forward your message to all your users,\ntogether with a 'Donate' button",
                         reply_markup=self.reply_markup)
        return DONATION_TO_USERS

    @run_async
    def received_donation(self, bot, update):
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
            [[InlineKeyboardButton(text="Done", callback_data="send_donation_finish")]]
        )
        bot.send_message(update.message.chat_id,
                         "Great! Send me a new message or click 'Done'",
                         reply_markup=final_reply_markup)

        return DONATION_TO_USERS

    def send_donation_finish(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Donate", callback_data="pay_donation"),
                        InlineKeyboardButton(text="Back", callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         "Thank you! We've sent your message to your users!",
                         reply_markup=final_reply_markup)
        chats = chats_table.find({"bot_id": bot.id})  # TODO it sends to everybody =/
        for chat in chats:
            if chat["chat_id"] != update.callback_query.message.chat_id:
                bot.send_message(chat["chat_id"],
                                 "Donate!",
                                 reply_markup=final_reply_markup)
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


SEND_DONATION_TO_USERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="send_donation_to_users",
                                       callback=SendDonationToUsers().send_donation),
                  CallbackQueryHandler(callback=SendDonationToUsers().back,
                                       pattern=r"cancel_send_donation")],

    states={
        DONATION_TO_USERS: [MessageHandler(Filters.all, SendDonationToUsers().received_donation),
                            CallbackQueryHandler(callback=SendDonationToUsers().back,
                                                 pattern=r"cancel_send_donation")],

    },

    fallbacks=[CallbackQueryHandler(callback=SendDonationToUsers().send_donation_finish,
                                    pattern=r"send_donation_finish"),
               CallbackQueryHandler(callback=SendDonationToUsers().back,
                                    pattern=r"cancel_send_donation"),
               CommandHandler('cancel', SendDonationToUsers().error),
               MessageHandler(filters=Filters.command, callback=SendDonationToUsers().error)]
)
