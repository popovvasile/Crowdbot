# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, run_async, CallbackQueryHandler

from database import user_mode_table

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

__mod_name__ = "User view"

__admin_help__ = """
 Click "ON" to turn on the user view and interact with the chatbot as an non-admin user.
  
 Click "OFF" to return to the normal mode
"""


__admin_keyboard__ = [InlineKeyboardButton(text="USER MODE", callback_data="turn_user_mode_on")]


class UserMode(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="MENU", callback_data="help_back")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def turn_user_mode_on(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id,)
        current_user_mode = user_mode_table.find_one({"bot_id": bot.id,
                                                      "user_id": update.effective_user.id})
        if current_user_mode:
            current_user_mode["user_mode"] = True

            user_mode_table.replace_one({"bot_id": bot.id,
                                         "user_id": update.effective_user.id},
                                        current_user_mode)
        else:
            user_mode_table.insert({"bot_id": bot.id,
                                    "user_id": update.effective_user.id,
                                    "user_mode": True})
        bot.send_message(update.callback_query.message.chat.id,
                         "Great! Now you can return to the main menu and"
                         " you'll see it as non-admin users do (except the 'User view button'.",
                         reply_markup=self.reply_markup)
        logger.info("USER MODE ON for user {} on bot {}:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END

    @run_async
    def turn_user_mode_off(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id,)
        current_user_mode = user_mode_table.find_one({"bot_id": bot.id,
                                                      "user_id": update.effective_user.id})
        if current_user_mode:
            current_user_mode["user_mode"] = False

            user_mode_table.replace_one({"bot_id": bot.id,
                                         "user_id": update.effective_user.id},
                                        current_user_mode)
        else:
            user_mode_table.insert({"bot_id": bot.id,
                                    "user_id": update.effective_user.id,
                                    "user_mode": False})
        bot.send_message(update.callback_query.message.chat.id,
                         "User view is turned off! Now you can use the main menu as admin",
                         reply_markup=self.reply_markup)
        logger.info("USER MODE OFF for user {} on bot {}:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END


USER_MODE_ON = CallbackQueryHandler(pattern="turn_user_mode_on",
                                    callback=UserMode().turn_user_mode_on)

USER_MODE_OFF = CallbackQueryHandler(pattern="turn_user_mode_off",
                                     callback=UserMode().turn_user_mode_off)
