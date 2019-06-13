import os
import uuid

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler, RegexHandler)
import logging
from database import custom_buttons_table, chatbots_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help

# from modules.helper_funcs.restart_program import restart_program
from modules.helper_funcs.en_strings import create_button, delete_button, edit_button_button, edit_menu_text, \
    add_menu_buttons_help, back_button, add_menu_buttons_str_1, back_text, great_text, add_menu_buttons_str_2, \
    add_menu_buttons_str_3, done_button, add_menu_buttons_str_4, add_menu_buttons_str_5, add_menu_buttons_str_6, \
    add_menu_buttons_str_7, add_menu_buttons_str_8, add_menu_buttons_str_9, create_button_button, manage_button_str_2, \
    add_menu_buttons_str_10, menu_button, add_menu_module_button

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TYPING_BUTTON, TYPING_DESCRIPTION, DESCRIPTION_FINISH = range(3)
TYPING_TO_DELETE_BUTTON = 17
__mod_name__ = add_menu_module_button

# __admin_keyboard__ = [["/create_button"], ["/delete_button"]]
__admin_keyboard__ = [InlineKeyboardButton(text=create_button, callback_data="create_button"),
                      InlineKeyboardButton(text=delete_button, callback_data="delete_button"),
                      InlineKeyboardButton(text=edit_button_button, callback_data="edit_button"),
                      InlineKeyboardButton(text=edit_menu_text, callback_data="edit_bot_description")]

__admin_help__ = add_menu_buttons_help


class AddCommands(object):
    def __init__(self):
        reply_buttons = [[InlineKeyboardButton(text=back_button, callback_data="cancel_add_button")]]
        self.reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        finish_buttons = [[InlineKeyboardButton(text=back_button, callback_data="cancel_delete_button")]]
        self.finish_markup = InlineKeyboardMarkup(
            finish_buttons)

    def start(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        reply_keyboard = [chatbots_table.find_one({"bot_id": bot.id})["buttons"]]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        bot.send_message(update.callback_query.message.chat.id,
                         add_menu_buttons_str_1,
                         reply_markup=markup)
        bot.send_message(update.callback_query.message.chat.id,
                         back_text, reply_markup=self.reply_markup)
        return TYPING_BUTTON

    def button_handler(self, bot, update, user_data):
        # TODO create a chatbot specially for OG

        chat_id, txt = initiate_chat_id(update)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": bot.id,
            "button": txt})
        if button_list_of_dicts.count() == 0:

            user_data['button'] = txt
            update.message.reply_text(great_text, reply_markup=ReplyKeyboardRemove())
            update.message.reply_text(add_menu_buttons_str_2,
                                      reply_markup=self.reply_markup)
            return TYPING_DESCRIPTION
        else:
            update.message.reply_text(add_menu_buttons_str_3,
                                      reply_markup=self.reply_markup)

            return TYPING_BUTTON

    def description_handler(self, bot, update, user_data):
        photo_directory = "files/{bot_id}/photo".format(bot_id=bot.id)
        audio_directory = "files/{bot_id}/audio".format(bot_id=bot.id)
        document_directory = "files/{bot_id}/document".format(bot_id=bot.id)
        video_directory = "files/{bot_id}/video".format(bot_id=bot.id)

        if not os.path.exists(photo_directory):
            os.makedirs(photo_directory)
        if not os.path.exists(audio_directory):
            os.makedirs(audio_directory)
        if not os.path.exists(document_directory):
            os.makedirs(document_directory)
        if not os.path.exists(video_directory):
            os.makedirs(video_directory)

        if update.callback_query:
            if update.message.callback_query.data == done_button:
                self.description_finish(bot, update, user_data)
                return ConversationHandler.END
        if update.message.text:
            if "descriptions" not in user_data:
                user_data["descriptions"] = [update.message.text]
            elif user_data["descriptions"] is not None:
                user_data["descriptions"].append(update.message.text)
            else:
                user_data["descriptions"] = list()

        if update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            if "photo_files" not in user_data:
                user_data["photo_files"] = [photo_file]
            elif user_data["photo_files"] is not None:
                user_data["photo_files"] = user_data["photo_files"] + [photo_file]
            else:
                user_data["photo_files"] = list()

        if update.message.audio:

            audio_file = update.message.audio.get_file().file_id
            if "audio_files" not in user_data:
                user_data["audio_files"] = [audio_file]
            elif user_data["audio_files"] is not None:
                user_data["audio_files"] = user_data["audio_files"] + [audio_file]
            else:
                user_data["audio_files"] = list()

        if update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            if "audio_files" not in user_data:
                user_data["audio_files"] = [voice_file]
            elif user_data["audio_files"] is not None:
                user_data["audio_files"] = user_data["audio_files"] + [voice_file]
            else:
                user_data["audio_files"] = list()

        if update.message.document:
            document_file = update.message.document.get_file().file_id
            if "document_files" not in user_data:
                user_data["document_files"] = [document_file]
            elif user_data["document_files"] is not None:
                user_data["document_files"] = user_data["document_files"] + [document_file]
            else:
                user_data["document_files"] = list()

        if update.message.video:
            video_file = update.message.video.get_file().file_id
            if "video_files" not in user_data:
                user_data["video_files"] = [video_file]
            elif user_data["video_files"] is not None:
                user_data["video_files"] = user_data["video_files"] + [video_file]
            else:
                user_data["video_files"] = list()

        if update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            if "video_files" not in user_data:
                user_data["video_files"] = [video_note_file]
            elif user_data["video_files"] is not None:
                user_data["video_files"] = user_data["video_files"] + [video_note_file]
            else:
                user_data["video_files"] = list()
        done_buttons = [[InlineKeyboardButton(text=done_button, callback_data="DONE")]]
        done_reply_markup = InlineKeyboardMarkup(
            done_buttons)
        update.message.reply_text(add_menu_buttons_str_4,
                                  reply_markup=done_reply_markup)
        update.message.reply_text(back_text, reply_markup=self.reply_markup)
        return TYPING_DESCRIPTION

    def description_finish(self, bot, update, user_data):
        print(user_data)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        user_id = update.effective_user.id
        user_data.update({"button": user_data['button'],
                          "button_lower": user_data['button'].replace(" ", "").lower(),
                          "admin_id": user_id,
                          "bot_id": bot.id,
                          })
        custom_buttons_table.save(user_data)

        bot.send_message(update.callback_query.message.chat.id,
                         add_menu_buttons_str_5.format(user_data["button"]))
        get_help(bot, update)
        logger.info("Admin {} on bot {}:{} added a new button:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["button"]))
        user_data.clear()

        return ConversationHandler.END

    def delete_button(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": bot.id})
        if button_list_of_dicts.count() != 0:
            button_list = [button['button'] for button in button_list_of_dicts]
            reply_keyboard = [button_list]
            bot.send_message(update.callback_query.message.chat.id,
                             add_menu_buttons_str_6,  # TODO remove this message later
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            bot.send_message(update.callback_query.message.chat.id,
                             back_text, reply_markup=self.finish_markup)

            return TYPING_TO_DELETE_BUTTON
        else:
            bot.send_message(update.callback_query.message.chat.id,
                             add_menu_buttons_str_7)
            get_help(bot, update)

            return ConversationHandler.END

    def delete_button_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        custom_buttons_table.delete_one({
            "button": txt,
            "bot_id": bot.id
        })
        update.message.reply_text(
            add_menu_buttons_str_8.format(txt), reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id=update.message.chat_id,  # TODO send as in polls
                         text=add_menu_buttons_str_10,
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(create_button_button, callback_data="create_button"),
                               InlineKeyboardButton(menu_button, callback_data="help_back")]]
                         ))
        logger.info("Admin {} on bot {}:{} deleted the button:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, txt))
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.send_message(update.callback_query.message.chat.id,
                         add_menu_buttons_str_9, reply_markup=ReplyKeyboardRemove()
                         )
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
        return ConversationHandler.END

    def cancel(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        bot.send_message(update.callback_query.message.chat.id,
                         "Command is cancelled", reply_markup=ReplyKeyboardRemove()
                         )

        get_help(bot, update)
        return ConversationHandler.END

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)


# Get the dispatcher to register handlers


# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
BUTTON_ADD_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddCommands().start,
                                       pattern=r"create_button")],

    states={
        TYPING_BUTTON: [
            MessageHandler(Filters.text,
                           AddCommands().button_handler, pass_user_data=True)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.all,
                                            AddCommands().description_handler, pass_user_data=True),
                             CallbackQueryHandler(callback=AddCommands().back,
                                                  pattern=r"cancel_add_button", pass_user_data=True)],
        DESCRIPTION_FINISH: [MessageHandler(Filters.text,
                                            AddCommands().description_finish, pass_user_data=True),
                             CallbackQueryHandler(callback=AddCommands().back,
                                                  pattern=r"cancel_add_button", pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=AddCommands().description_finish, pattern=r"DONE", pass_user_data=True),

        CallbackQueryHandler(callback=AddCommands().back,
                             pattern=r"cancel_add_button", pass_user_data=True),
        CommandHandler('cancel', AddCommands().cancel),
        MessageHandler(filters=Filters.command, callback=AddCommands().cancel)
    ]
)
DELETE_BUTTON_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=AddCommands().delete_button,
                             pattern=r"delete_button")
    ],

    states={
        TYPING_TO_DELETE_BUTTON: [MessageHandler(Filters.text,
                                                 AddCommands().delete_button_finish)],
    },

    fallbacks=[CallbackQueryHandler(callback=AddCommands().cancel,
                                    pattern=r"cancel_delete_button"),
               CommandHandler('cancel', AddCommands().cancel),
               MessageHandler(filters=Filters.command, callback=AddCommands().cancel)
               ]
)

