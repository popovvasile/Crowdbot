#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
import logging
from database import custom_buttons_table, chatbots_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.main_runnner_helper import get_help

from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.misc import delete_messages

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TYPING_BUTTON, TYPING_DESCRIPTION, DESCRIPTION_FINISH = range(3)
TYPING_TO_DELETE_BUTTON = 17
TYPING_LINK, TYPING_BUTTON_FINISH = range(2)


class AddButtons(object):

    def start(self, bot, update):
        reply_buttons = [[InlineKeyboardButton(text=string_dict(bot)["link_button_str"],
                                               callback_data="create_link_button")],
                         [InlineKeyboardButton(text=string_dict(bot)["simple_button_str"],
                                               callback_data="create_simple_button")],
                         [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                               callback_data="help_module(menu_buttons)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text=string_dict(bot)["choose_button_type_text"],
                         reply_markup=reply_markup)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        return ConversationHandler.END


class AddCommands(object):

    def start(self, bot, update, user_data):
        user_data["to_delete"] = []
        reply_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                               callback_data="help_module(menu_buttons)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        buttons = chatbots_table.find_one({"bot_id": bot.id})["buttons"]
        if buttons is not None and buttons != []:
            markup = ReplyKeyboardMarkup([buttons], one_time_keyboard=True)
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(bot)["add_menu_buttons_str_1"],
                                                           reply_markup=markup))
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(bot)["back_text"], reply_markup=reply_markup))
            return TYPING_BUTTON
        else:
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(bot)["add_menu_buttons_str_1_1"]))
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(bot)["back_text"], reply_markup=reply_markup))
            return TYPING_BUTTON

    def button_handler(self, bot, update, user_data):
        user_data["to_delete"].append(update.message)
        reply_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                               callback_data="help_module(menu_buttons)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        chat_id, txt = initiate_chat_id(update)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": bot.id,
            "button": txt})
        if button_list_of_dicts.count() == 0:

            user_data['button'] = txt
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["great_text"],
                                                                    reply_markup=ReplyKeyboardRemove()))
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_menu_buttons_str_2"],
                                                                    reply_markup=reply_markup))
            return TYPING_DESCRIPTION
        else:
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_menu_buttons_str_3"],
                                                                    reply_markup=reply_markup))

            return TYPING_BUTTON

    def description_handler(self, bot, update, user_data):
        user_data["to_delete"].append(update.message)
        reply_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                               callback_data="help_module(menu_buttons)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        if "content" not in user_data:
            user_data["content"] = []
        general_list = user_data["content"]
        if update.callback_query:
            if update.message.callback_query.data == string_dict(bot)["done_button"]:
                self.description_finish(bot, update, user_data)
                return ConversationHandler.END
        if update.message.text:
            general_list.append({"text": update.message.text})

        if update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            general_list.append({"photo_file": photo_file})

        if update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            print(audio_file)
            general_list.append({"audio_file": audio_file})

        if update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            general_list.append({"voice_file": voice_file})

        if update.message.document:
            document_file = update.message.document.get_file().file_id
            general_list.append({"document_file": document_file})

        if update.message.video:
            video_file = update.message.video.get_file().file_id
            general_list.append({"video_file": video_file})

        if update.message.video_note:
            video_note_file = update.message.video_note.get_file().file_id
            general_list.append({"video_note_file": video_note_file})
        if update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            general_list.append({"animation_file": animation_file})
        if update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            general_list.append({"sticker_file": sticker_file})
        user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["back_text"],
                                                                reply_markup=reply_markup))
        done_buttons = [[InlineKeyboardButton(text=string_dict(bot)["done_button"], callback_data="DONE")]]
        done_reply_markup = InlineKeyboardMarkup(
            done_buttons)
        user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_menu_buttons_str_4"],
                                                                reply_markup=done_reply_markup))
        user_data["content"] = general_list
        return TYPING_DESCRIPTION

    def description_finish(self, bot, update, user_data):
        print(user_data)
        delete_messages(bot, update, user_data)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        user_id = update.effective_user.id
        user_data.update({"button": user_data['button'],
                          "button_lower": user_data['button'].replace(" ", "").lower(),
                          "admin_id": user_id,
                          "bot_id": bot.id,
                          "link_button": False,
                          })
        user_data.pop('to_delete', None)
        custom_buttons_table.save(user_data)
        reply_buttons = [
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(menu_buttons)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["add_menu_buttons_str_5"].format(user_data["button"]),
                         reply_markup=reply_markup)
        logger.info("Admin {} on bot {}:{} added a new button:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["button"]))
        user_data.clear()
        return ConversationHandler.END

    def delete_button(self, bot, update):
        finish_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(menu_buttons)")]]
        finish_markup = InlineKeyboardMarkup(
            finish_buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": bot.id})
        if button_list_of_dicts.count() != 0:
            button_list = [button['button'] for button in button_list_of_dicts]
            reply_keyboard = [button_list]

            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["add_menu_buttons_str_6"],
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["back_text"], reply_markup=finish_markup)
            return TYPING_TO_DELETE_BUTTON
        else:
            reply_buttons = [[InlineKeyboardButton(text=string_dict(bot)["create_button"],
                                                   callback_data="create_button"),
                              InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                   callback_data="help_module(menu_buttons)")
                              ]]
            reply_markup = InlineKeyboardMarkup(
                reply_buttons)
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["add_menu_buttons_str_7"], reply_markup=reply_markup)

            return ConversationHandler.END

    def delete_button_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        custom_buttons_table.delete_one({
            "button": txt,
            "bot_id": bot.id
        })
        update.message.reply_text(
            string_dict(bot)["add_menu_buttons_str_8"].format(txt), reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id=update.message.chat_id,  # TODO send as in polls
                         text=string_dict(bot)["add_menu_buttons_str_10"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(string_dict(bot)["create_button_button"],
                                                    callback_data="create_button"),
                               InlineKeyboardButton(string_dict(bot)["back_button"],
                                                    callback_data="help_module(menu_buttons)")]]
                         ))
        logger.info("Admin {} on bot {}:{} deleted the button:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, txt))
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["add_menu_buttons_str_9"], reply_markup=ReplyKeyboardRemove()
                         )
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
        return ConversationHandler.END


class AddLinkButton(object):

    def start(self, bot, update, user_data):
        user_data["to_delete"] = []
        reply_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                               callback_data="help_module(menu_buttons)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                       string_dict(bot)["add_menu_buttons_str_1_1"]))
        user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                       string_dict(bot)["back_text"], reply_markup=reply_markup))
        return TYPING_LINK

    def link_handler(self, bot, update, user_data):
        user_data["to_delete"].append(update.message)
        reply_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                               callback_data="help_module(menu_buttons)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        chat_id, txt = initiate_chat_id(update)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": bot.id,
            "button": txt})
        if button_list_of_dicts.count() == 0:

            user_data['button'] = txt
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_menu_buttons_str_2_link"],
                                                                    reply_markup=reply_markup))
            return TYPING_BUTTON_FINISH
        else:
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_menu_buttons_str_3"],
                                                                    reply_markup=reply_markup))

            return TYPING_LINK

    def button_finish(self, bot, update, user_data):
        print(user_data)
        delete_messages(bot, update, user_data)
        chat_id, txt = initiate_chat_id(update)
        user_id = update.effective_user.id
        user_data.update({"button": user_data['button'],
                          "button_lower": user_data['button'].replace(" ", "").lower(),
                          "admin_id": user_id,
                          "bot_id": bot.id,
                          "link_button": True,
                          "link": txt
                          })
        user_data.pop('to_delete', None)
        custom_buttons_table.save(user_data)
        reply_buttons = [
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(menu_buttons)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        bot.send_message(chat_id,
                         string_dict(bot)["add_menu_buttons_str_5"].format(user_data["button"]),
                         reply_markup=reply_markup)
        logger.info("Admin {} on bot {}:{} added a new button:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["button"]))
        user_data.clear()
        return ConversationHandler.END


CREATE_BUTTON_CHOOSE = CallbackQueryHandler(callback=AddButtons().start, pattern="create_button")

LINK_BUTTON_ADD_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddLinkButton().start,
                                       pattern=r"create_link_button",
                                       pass_user_data=True)],

    states={
            TYPING_LINK: [MessageHandler(Filters.text,callback=AddLinkButton().link_handler, pass_user_data=True)],
            TYPING_BUTTON_FINISH: [MessageHandler(Filters.text,
                                                  callback=AddLinkButton().button_finish, pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=AddCommands().back,
                             pattern=r"help_module", pass_user_data=True),
        CallbackQueryHandler(callback=AddCommands().back,
                             pattern=r"help_back", pass_user_data=True),
    ]
)

BUTTON_ADD_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddCommands().start,
                                       pattern=r"create_simple_button",
                                       pass_user_data=True)],

    states={
        TYPING_BUTTON: [
            MessageHandler(Filters.text,
                           AddCommands().button_handler, pass_user_data=True)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.all,
                                            AddCommands().description_handler, pass_user_data=True)],
        DESCRIPTION_FINISH: [MessageHandler(Filters.text,
                                            AddCommands().description_finish, pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=AddCommands().description_finish, pattern=r"DONE", pass_user_data=True),

        CallbackQueryHandler(callback=AddCommands().back,
                             pattern=r"help_module", pass_user_data=True),
    ]
)
DELETE_BUTTON_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=AddCommands().delete_button,
                             pattern=r"delete_button")
    ],

    states={
        TYPING_TO_DELETE_BUTTON: [MessageHandler(Filters.text,
                                                 AddCommands().delete_button_finish,
                                                 pass_user_data=True)],
    },

    fallbacks=[CallbackQueryHandler(callback=AddCommands().back,
                                    pattern=r"help_module", pass_user_data=True),
               ]
)