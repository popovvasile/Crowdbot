import os
import uuid

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
import logging
from database import custom_buttons_table, chatbots_table
from modules.helper_funcs.helper import get_help

# from modules.helper_funcs.restart_program import restart_program
from modules.helper_funcs.strings import create_button, delete_button, edit_button_button, edit_menu_text,\
    back_button, done_button, back_text

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TYPING_BUTTON, TYPING_DESCRIPTION, DESCRIPTION_FINISH = range(3)
TYPING_TO_DELETE_BUTTON = 17
__mod_name__ = "Add content to button"

# __admin_keyboard__ = [["/create_button"], ["/delete_button"]]
__admin_keyboard__ = [InlineKeyboardButton(text=create_button, callback_data="create_button"),
                      InlineKeyboardButton(text=delete_button, callback_data="delete_button"),
                      InlineKeyboardButton(text=edit_button_button, callback_data="edit_button"),
                      InlineKeyboardButton(text=edit_menu_text, callback_data="edit_bot_description")]

__admin_help__ = "Add content to button"


class AddCommands(object):
    def __init__(self):
        reply_buttons = [[InlineKeyboardButton(text=back_button, callback_data="cancel_add_button_content")]]
        self.reply_markup = InlineKeyboardMarkup(
            reply_buttons)

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
        return TYPING_DESCRIPTION

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
            photo_file = update.message.photo[-1].get_file()
            filename = 'photo_{}.jpg'.format(str(uuid.uuid4())[:7])
            custom_path = photo_directory + "/" + filename
            photo_file.download(custom_path=custom_path)
            if "photo_files" not in user_data:
                user_data["photo_files"] = [filename]
            elif user_data["photo_files"] is not None:
                user_data["photo_files"] = user_data["photo_files"] + [filename]
            else:
                user_data["photo_files"] = list()

        if update.message.audio:

            audio_file = update.message.audio.get_file()
            filename = 'audio_{}.mp3'.format(str(uuid.uuid4())[:7])
            custom_path = audio_directory + "/" + filename
            audio_file.download(custom_path=custom_path)
            if "audio_files" not in user_data:
                user_data["audio_files"] = [filename]
            elif user_data["audio_files"] is not None:
                user_data["audio_files"] = user_data["audio_files"] + [filename]
            else:
                user_data["audio_files"] = list()

        if update.message.voice:

            voice_file = update.message.voice.get_file()
            filename = 'voice_{}.mp3'.format(str(uuid.uuid4())[:7])
            custom_path = audio_directory + "/" + filename
            voice_file.download(custom_path=custom_path)
            if "audio_files" not in user_data:
                user_data["audio_files"] = [filename]
            elif user_data["audio_files"] is not None:
                user_data["audio_files"] = user_data["audio_files"] + [filename]
            else:
                user_data["audio_files"] = list()

        if update.message.document:

            document_file = update.message.document.get_file()
            filename = 'document_{}_{}'.format(str(uuid.uuid4())[:5], update.message.document.file_name[-5:])
            custom_path = document_directory + "/" + filename
            document_file.download(custom_path=custom_path)
            if "document_files" not in user_data:
                user_data["document_files"] = [filename]
            elif user_data["document_files"] is not None:
                user_data["document_files"] = user_data["document_files"] + [filename]
            else:
                user_data["document_files"] = list()

        if update.message.video:

            video_file = update.message.video.get_file()
            filename = 'video_{}.mp4'.format(str(uuid.uuid4())[:7])
            custom_path = video_directory + "/" + filename

            video_file.download(custom_path=custom_path)

            if "video_files" not in user_data:
                user_data["video_files"] = [filename]
            elif user_data["video_files"] is not None:
                user_data["video_files"] = user_data["video_files"] + [filename]
            else:
                user_data["video_files"] = list()

        if update.message.video_note:
            video_note_file = update.message.audio.get_file()
            filename = 'video_note_{}.mp4'.format(str(uuid.uuid4())[:7])
            custom_path = video_directory + "/" + filename
            video_note_file.download(filename, custom_path=custom_path)

            if "video_files" not in user_data:
                user_data["video_files"] = [filename]
            elif user_data["video_files"] is not None:
                user_data["video_files"] = user_data["video_files"] + [filename]
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
                                       pattern=r"add_button_content")],

    states={
        TYPING_DESCRIPTION: [MessageHandler(Filters.all,
                                            AddCommands().description_handler, pass_user_data=True),
                             CallbackQueryHandler(callback=AddCommands().back,
                                                  pattern=r"cancel_add_button_content", pass_user_data=True)],
        DESCRIPTION_FINISH: [MessageHandler(Filters.text,
                                            AddCommands().description_finish, pass_user_data=True),
                             CallbackQueryHandler(callback=AddCommands().back,
                                                  pattern=r"cancel_add_button_content", pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=AddCommands().description_finish, pattern=r"DONE", pass_user_data=True),

        CallbackQueryHandler(callback=AddCommands().back,
                             pattern=r"cancel_add_button_content", pass_user_data=True),
        CommandHandler('cancel', AddCommands().cancel),
        MessageHandler(filters=Filters.command, callback=AddCommands().cancel)
    ]
)