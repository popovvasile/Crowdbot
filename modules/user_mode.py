# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, run_async, CallbackQueryHandler
from database import user_mode_table
from modules.helper_funcs.lang_strings.strings import string_dict


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class UserMode(object):
    
    def turn_user_mode_on(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["menu_button"],
                                             callback_data="help_module(user_mode)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

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
                         string_dict(bot)["user_mode_on_finish"],
                         reply_markup=reply_markup)
        logger.info("USER MODE ON for user {} on bot {}:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END

    def turn_user_mode_off(self, bot, update):
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["menu_button"],
                                             callback_data="help_module(user_mode)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

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
                         string_dict(bot)["user_mode_off_finish"],
                         reply_markup=reply_markup)
        logger.info("USER MODE OFF for user {} on bot {}:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END


USER_MODE_ON = CallbackQueryHandler(pattern="turn_user_mode_on",
                                    callback=UserMode().turn_user_mode_on)

USER_MODE_OFF = CallbackQueryHandler(pattern="turn_user_mode_off",
                                     callback=UserMode().turn_user_mode_off)
