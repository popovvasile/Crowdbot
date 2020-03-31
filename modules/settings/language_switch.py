#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler

from helper_funcs.misc import delete_messages
from logs import logger


class UserMode(object):
    class BotFather(object):
        def set_lang(self, update, context):
            delete_messages(update, context)
            # take lang from inline button and set new user_data
            context.user_data['lang'] = update.callback_query.data.split('/')[1]
            # change user language
            users_table.update_one({'user_id': update.effective_user.id},
                                   {'$set': {'lang': context.user_data['lang']}})
            # send main menu keyboard
            return MainMenu.back_to_main_menu(update, context)

    @staticmethod
    def lang_menu(update, context):
        delete_messages(update, context)
        lang_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=get_str(update, context, 'en'),
                                  callback_data='language/ENG')],
            [InlineKeyboardButton(text=get_str(update, context, 'ru'),
                                  callback_data='language/RUS')]
        ])
        # send language keyboard
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=get_str(update, context, 'language_menu'),
                reply_markup=lang_keyboard))
        return ConversationHandler.END

SET_LANG = CallbackQueryHandler(callback=BotFather().set_lang,
                                pattern=r"language")