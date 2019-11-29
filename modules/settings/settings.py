#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
import logging
from database import custom_buttons_table, chatbots_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.helper import get_help

from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.misc import delete_messages

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TYPING_BUTTON, TYPING_DESCRIPTION, DESCRIPTION_FINISH = range(3)
TYPING_TO_DELETE_BUTTON = 17
TYPING_LINK, TYPING_BUTTON_FINISH = range(2)


def buttons_menu(update, context):
    string_d_str = string_dict(context)
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    no_channel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=string_d_str["create_button_button"],
                               callback_data="create_button")],
         [InlineKeyboardButton(text=string_d_str["edit_button_button"],
                               callback_data="edit_button")],
         [InlineKeyboardButton(text=string_d_str["delete_button"],
                               callback_data="delete_button")],
         [InlineKeyboardButton(text=string_d_str["user_mode_module"],
                               callback_data="turn_user_mode_on")],
         [InlineKeyboardButton(text=string_dict(context)["back_button"],
                               callback_data="help_module(settings)")]
         ]
    )
    context.bot.send_message(update.callback_query.message.chat.id,
                     string_dict(context)["buttons"], reply_markup=no_channel_keyboard)
    return ConversationHandler.END


class AddButtons(object):

    def start(self, update, context):
        reply_buttons = [[InlineKeyboardButton(text=string_dict(context)["link_button_str"],
                                               callback_data="create_link_button")],
                         [InlineKeyboardButton(text=string_dict(context)["simple_button_str"],
                                               callback_data="create_simple_button")],
                         [InlineKeyboardButton(text=string_dict(context)["back_button"],
                                               callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text=string_dict(context)["choose_button_type_text"],
                         reply_markup=reply_markup)
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        return ConversationHandler.END


class AddCommands(object):

    def start(self, update, context):
        context.user_data["to_delete"] = []
        reply_buttons = [[InlineKeyboardButton(text=string_dict(context)["back_button"],
                                               callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        buttons = chatbots_table.find_one({"bot_id": context.bot.id})["buttons"]
        if buttons is not None and buttons != []:
            markup = ReplyKeyboardMarkup([buttons], one_time_keyboard=True)
            context.user_data["to_delete"].append(context.bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(context)["add_menu_buttons_str_1"],
                                                           reply_markup=markup))
            context.user_data["to_delete"].append(context.bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(context)["back_text"], reply_markup=reply_markup))
            return TYPING_BUTTON
        else:
            context.user_data["to_delete"].append(context.bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(context)["add_menu_buttons_str_1_1"]))
            context.user_data["to_delete"].append(context.bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(context)["back_text"], reply_markup=reply_markup))
            return TYPING_BUTTON

    def button_handler(self, update, context):
        context.user_data["to_delete"].append(update.message)
        reply_buttons = [[InlineKeyboardButton(text=string_dict(context)["back_button"],
                                               callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        chat_id, txt = initiate_chat_id(update)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": context.bot.id,
            "button": txt})
        if button_list_of_dicts.count() == 0:

            context.user_data['button'] = txt
            context.user_data["to_delete"].append(update.message.reply_text(string_dict(context)["great_text"],
                                                                    reply_markup=ReplyKeyboardRemove()))
            context.user_data["to_delete"].append(update.message.reply_text(string_dict(context)["add_menu_buttons_str_2"],
                                                                    reply_markup=reply_markup))
            return TYPING_DESCRIPTION
        else:
            context.user_data["to_delete"].append(update.message.reply_text(string_dict(context)["add_menu_buttons_str_3"],
                                                                    reply_markup=reply_markup))

            return TYPING_BUTTON

    def description_handler(self, update, context):
        context.user_data["to_delete"].append(update.message)
        reply_buttons = [[InlineKeyboardButton(text=string_dict(context)["back_button"],
                                               callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        if "content" not in context.user_data:
            context.user_data["content"] = []
        general_list = context.user_data["content"]
        if update.callback_query:
            if update.message.callback_query.data == string_dict(context)["done_button"]:
                self.description_finish(update, context)
                return ConversationHandler.END
        if update.message.text:
            general_list.append({"text": update.message.text})

        if update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            general_list.append({"photo_file": photo_file})

        if update.message.audio:
            audio_file = update.message.audio.get_file().file_id
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
        context.user_data["to_delete"].append(update.message.reply_text(string_dict(context)["back_text"],
                                                                reply_markup=reply_markup))
        done_buttons = [[InlineKeyboardButton(text=string_dict(context)["done_button"], callback_data="DONE")]]
        done_reply_markup = InlineKeyboardMarkup(
            done_buttons)
        context.user_data["to_delete"].append(update.message.reply_text(string_dict(context)["add_menu_buttons_str_4"],
                                                                reply_markup=done_reply_markup))
        context.user_data["content"] = general_list
        return TYPING_DESCRIPTION

    def description_finish(self, update, context):
        delete_messages(update, context)

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        user_id = update.effective_user.id
        context.user_data.update({"button": context.user_data['button'],
                          "button_lower": context.user_data['button'].replace(" ", "").lower(),
                          "admin_id": user_id,
                          "bot_id": context.bot.id,
                          "link_button": False,
                          })
        context.user_data.pop('to_delete', None)
        custom_buttons_table.save(context.user_data)
        reply_buttons = [
            [InlineKeyboardButton(text=string_dict(context)["back_button"], callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        context.bot.send_message(update.callback_query.message.chat.id,
                         string_dict(context)["add_menu_buttons_str_5"].format(context.user_data["button"]),
                         reply_markup=reply_markup)
        logger.info("Admin {} on bot {}:{} added a new button:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, context.user_data["button"]))
        context.user_data.clear()
        return ConversationHandler.END

    def delete_button(self, update, context):
        finish_buttons = [[InlineKeyboardButton(text=string_dict(context)["back_button"],
                                                callback_data="help_module(settings)")]]
        finish_markup = InlineKeyboardMarkup(
            finish_buttons)
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": context.bot.id})
        if button_list_of_dicts.count() != 0:
            button_list = [button['button'] for button in button_list_of_dicts]
            reply_keyboard = [button_list]

            context.bot.send_message(update.callback_query.message.chat.id,
                             string_dict(context)["add_menu_buttons_str_6"],
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            context.bot.send_message(update.callback_query.message.chat.id,
                             string_dict(context)["back_text"], reply_markup=finish_markup)
            return TYPING_TO_DELETE_BUTTON
        else:
            reply_buttons = [[InlineKeyboardButton(text=string_dict(context)["create_button"],
                                                   callback_data="create_button"),
                              InlineKeyboardButton(text=string_dict(context)["back_button"],
                                                   callback_data="help_module(settings)")
                              ]]
            reply_markup = InlineKeyboardMarkup(
                reply_buttons)
            context.bot.send_message(update.callback_query.message.chat.id,
                             string_dict(context)["add_menu_buttons_str_7"], reply_markup=reply_markup)

            return ConversationHandler.END

    def delete_button_finish(self, update, context):
        chat_id, txt = initiate_chat_id(update)
        custom_buttons_table.delete_one({
            "button": txt,
            "bot_id": context.bot.id
        })
        update.message.reply_text(
            string_dict(context)["add_menu_buttons_str_8"].format(txt), reply_markup=ReplyKeyboardRemove())
        context.bot.send_message(chat_id=update.message.chat_id,  # TODO send as in polls
                         text=string_dict(context)["add_menu_buttons_str_10"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(string_dict(context)["create_button_button"],
                                                    callback_data="create_button"),
                               InlineKeyboardButton(string_dict(context)["back_button"],
                                                    callback_data="help_module(settings)")]]
                         ))
        logger.info("Admin {} on bot {}:{} deleted the button:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, txt))
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.send_message(update.callback_query.message.chat.id,
                         string_dict(context)["add_menu_buttons_str_9"], reply_markup=ReplyKeyboardRemove()
                         )
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(update, context)
        context.user_data.clear()
        return ConversationHandler.END


class AddLinkButton(object):

    def start(self, update, context):
        context.user_data["to_delete"] = []
        reply_buttons = [[InlineKeyboardButton(text=string_dict(context)["back_button"],
                                               callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        context.user_data["to_delete"].append(context.bot.send_message(update.callback_query.message.chat.id,
                                                       string_dict(context)["add_menu_buttons_str_1_1"]))
        context.user_data["to_delete"].append(context.bot.send_message(update.callback_query.message.chat.id,
                                                       string_dict(context)["back_text"], reply_markup=reply_markup))
        return TYPING_LINK

    def link_handler(self, update, context):
        context.user_data["to_delete"].append(update.message)
        reply_buttons = [[InlineKeyboardButton(text=string_dict(context)["back_button"],
                                               callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        chat_id, txt = initiate_chat_id(update)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": context.bot.id,
            "button": txt})
        if button_list_of_dicts.count() == 0:

            context.user_data['button'] = txt
            context.user_data["to_delete"].append(update.message.reply_text(string_dict(context)["add_menu_buttons_str_2_link"],
                                                                    reply_markup=reply_markup))
            return TYPING_BUTTON_FINISH
        else:
            context.user_data["to_delete"].append(update.message.reply_text(string_dict(context)["add_menu_buttons_str_3"],
                                                                    reply_markup=reply_markup))

            return TYPING_LINK

    def button_finish(self, update, context):
        delete_messages(update, context)
        chat_id, txt = initiate_chat_id(update)
        user_id = update.effective_user.id
        context.user_data.update({"button": context.user_data['button'],
                          "button_lower": context.user_data['button'].replace(" ", "").lower(),
                          "admin_id": user_id,
                          "bot_id": context.bot.id,
                          "link_button": True,
                          "link": txt
                          })
        context.user_data.pop('to_delete', None)
        custom_buttons_table.save(context.user_data)
        reply_buttons = [
            [InlineKeyboardButton(text=string_dict(context)["back_button"], callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        context.bot.send_message(chat_id,
                         string_dict(context)["add_menu_buttons_str_5"].format(context.user_data["button"]),
                         reply_markup=reply_markup)
        logger.info("Admin {} on bot {}:{} added a new button:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, context.user_data["button"]))
        context.user_data.clear()
        return ConversationHandler.END


CREATE_BUTTON_CHOOSE = CallbackQueryHandler(callback=AddButtons().start, pattern="create_button")
BUTTONS_MENU = CallbackQueryHandler(callback=buttons_menu, pattern="buttons")
LINK_BUTTON_ADD_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddLinkButton().start,
                                       pattern=r"create_link_button",
                                       pass_user_data=True)],

    states={
        TYPING_LINK: [MessageHandler(Filters.text, callback=AddLinkButton().link_handler, pass_user_data=True)],
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
