# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, run_async, CallbackQueryHandler)
from database import chatbots_table
from ru_modules.helper_funcs.helper import get_help
from ru_modules.helper_funcs.strings import back_button, edit_button_str_1, edit_button_str_2

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
MESSAGE = 1
MESSAGE_TO_USERS = 1


class EditBotDescription(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=back_button, callback_data="cancel_edit_description")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def send_message(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         edit_button_str_1, reply_markup=self.reply_markup)
        return MESSAGE

    @run_async
    def received_message(self, bot, update):
        bot.send_message(update.message.chat_id,
                         edit_button_str_2)

        old_bot = chatbots_table.find_one({"bot_id": bot.id})
        old_bot['welcomeMessage'] = update.message.text
        chatbots_table.update_one({"bot_id": bot.id}, {"$set": old_bot})
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


EDIT_BOT_DESCRIPTION_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="edit_bot_description",
                                       callback=EditBotDescription().send_message),
                  CallbackQueryHandler(callback=EditBotDescription().back,
                                       pattern=r"cancel_edit_description")],

    states={
        MESSAGE: [MessageHandler(Filters.all, EditBotDescription().received_message),
                  CallbackQueryHandler(callback=EditBotDescription().back,
                                       pattern=r"cancel_edit_description")],

    },

    fallbacks=[
               CallbackQueryHandler(callback=EditBotDescription().back,
                                    pattern=r"cancel_edit_description"),
               CommandHandler('cancel', EditBotDescription().error),
               MessageHandler(filters=Filters.command, callback=EditBotDescription().error)]
)