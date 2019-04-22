import os

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler, RegexHandler)
import logging
from database import custom_buttons_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help

# from modules.helper_funcs.restart_program import restart_program

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TYPING_BUTTON, TYPING_DESCRIPTION, DESCRIPTION_FINISH = range(3)
TYPING_TO_DELETE_BUTTON = 17
__mod_name__ = "Custom buttons"

# __admin_keyboard__ = [["/create_button"], ["/delete_button"]]
__admin_keyboard__ = [InlineKeyboardButton(text="Create", callback_data="create_button"),
                      InlineKeyboardButton(text="Delete", callback_data="delete_button")]

__admin_help__ = """
Here you can:\n
- Create a custom button for your bot that will display images, files, voice, music or text.\n
- Delete an old button
"""


class AddCommands(object):
    def __init__(self):
        reply_buttons = [[InlineKeyboardButton(text="Back", callback_data="cancel_add_button")]]
        self.reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        finish_buttons = [[InlineKeyboardButton(text="Back", callback_data="cancel_delete_button")]]
        self.finish_markup = InlineKeyboardMarkup(
            finish_buttons)

    def start(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        reply_keyboard = [['About', 'My projects'],
                          ['Contacts', 'Useful links']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        bot.send_message(update.callback_query.message.chat.id,
                         "Type a name for new button or choose one of the examples below. "
                         "Please note that you can't modify the buttons available by default ",
                         reply_markup=markup)
        bot.send_message(update.callback_query.message.chat.id,
                         "To quit, click 'Back'", reply_markup=self.reply_markup)
        return TYPING_BUTTON

    def button_handler(self, bot, update, user_data):
        # TODO create a chatbot specially for OG
        # TODO change bot description
        chat_id, txt = initiate_chat_id(update)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": bot.id,
            "button": txt})
        if button_list_of_dicts.count() == 0:

            user_data['button'] = txt
            update.message.reply_text("Great!", reply_markup=ReplyKeyboardRemove())
            update.message.reply_text('Now, send a text, an image, a video, '
                                      'a document or a music file to display for your new button',
                                      reply_markup=self.reply_markup)
            return TYPING_DESCRIPTION
        else:
            update.message.reply_text('You already have a button with the same name. Choose another name',
                                      reply_markup=self.reply_markup)

            return TYPING_BUTTON

    def description_handler(self, bot, update, user_data):
        photo_directory = "dynamic_files/{bot_id}/photo".format(bot_id=bot.id)
        audio_directory = "dynamic_files/{bot_id}/audio".format(bot_id=bot.id)
        document_directory = "dynamic_files/{bot_id}/document".format(bot_id=bot.id)
        video_directory = "dynamic_files/{bot_id}/video".format(bot_id=bot.id)

        if not os.path.exists(photo_directory):
            os.makedirs(photo_directory)
        if not os.path.exists(audio_directory):
            os.makedirs(audio_directory)
        if not os.path.exists(document_directory):
            os.makedirs(document_directory)
        if not os.path.exists(video_directory):
            os.makedirs(video_directory)

        if update.callback_query:
            if update.message.callback_query.data == "DONE":
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
            filename = 'photo_{}_button_{}_{}.jpg'.format(str(bot.id),
                                                          str(user_data['button']),
                                                          photo_file.file_id)
            custom_path = photo_directory + "/" + filename
            photo_file.download(custom_path=custom_path)
            if "photo_files" not in user_data:
                user_data["photo_files"] = [custom_path]
            elif user_data["photo_files"] is not None:
                user_data["photo_files"] = user_data["photo_files"] + [custom_path]
            else:
                user_data["photo_files"] = list()

        if update.message.audio:

            audio_file = update.message.audio.get_file()
            filename = 'audio_{}_button_{}_{}.mp3'.format(str(bot.id),
                                                          str(user_data['button']),
                                                          audio_file.file_id)
            custom_path = audio_directory + "/" + filename
            audio_file.download(custom_path=custom_path)
            if "audio_files" not in user_data:
                user_data["audio_files"] = [custom_path]
            elif user_data["audio_files"] is not None:
                user_data["audio_files"] = user_data["audio_files"] + [custom_path]
            else:
                user_data["audio_files"] = list()

        if update.message.voice:

            voice_file = update.message.voice.get_file()
            filename = 'voice_{}_{}_button_{}.mp3'.format(voice_file.file_id,
                                                          str(bot.id),
                                                          str(user_data['button']))
            custom_path = audio_directory + "/" + filename
            voice_file.download(custom_path=custom_path)
            if "audio_files" not in user_data:
                user_data["audio_files"] = [custom_path]
            elif user_data["audio_files"] is not None:
                user_data["audio_files"] = user_data["audio_files"] + [custom_path]
            else:
                user_data["audio_files"] = list()

        if update.message.document:

            document_file = update.message.document.get_file()
            filename = 'document_{}_button_{}_{}'.format(str(bot.id),
                                                         str(user_data['button']),
                                                         update.message.document.file_name)
            custom_path = document_directory + "/" + filename
            document_file.download(custom_path=custom_path)
            if "document_files" not in user_data:
                user_data["document_files"] = [custom_path]
            elif user_data["document_files"] is not None:
                user_data["document_files"] = user_data["document_files"] + [custom_path]
            else:
                user_data["document_files"] = list()

        if update.message.video:

            video_file = update.message.video.get_file()
            filename = 'video_{}_{}_button_{}.mp4'.format(video_file.file_id, str(bot.id),
                                                          str(user_data['button']))
            custom_path = video_directory + "/" + filename

            video_file.download(custom_path=custom_path)

            if "video_files" not in user_data:
                user_data["video_files"] = [custom_path]
            elif user_data["video_files"] is not None:
                user_data["video_files"] = user_data["video_files"] + [custom_path]
            else:
                user_data["video_files"] = list()

        if update.message.video_note:
            video_note_file = update.message.audio.get_file()
            filename = 'video_note_{}_{}_button_{}.mp4'.format(video_note_file.file_id,
                                                               str(bot.id),
                                                               str(user_data['button']))
            custom_path = video_directory + "/" + filename
            video_note_file.download(filename, custom_path=custom_path)

            if "video_files" not in user_data:
                user_data["video_files"] = [custom_path]
            elif user_data["video_files"] is not None:
                user_data["video_files"] = user_data["video_files"] + [custom_path]
            else:
                user_data["video_files"] = list()
        done_buttons = [[InlineKeyboardButton(text="DONE", callback_data="DONE")]]
        done_reply_markup = InlineKeyboardMarkup(
            done_buttons)
        update.message.reply_text('Great! You can add one more file or text to display.\n'
                                  'If you think that this is enough, click DONE',
                                  reply_markup=done_reply_markup)
        update.message.reply_text("Click Back to cancel", reply_markup=self.reply_markup)
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
                         'Thank you! The button will be accessible by clicking \n'
                         '{} in menu'.format(user_data["button"]))
        user_data.clear()
        get_help(bot, update)
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

                             "Choose the button that button that you want to delete",  # TODO remove this message later
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            bot.send_message(update.callback_query.message.chat.id,
                             "To quit, click 'Back'", reply_markup=self.finish_markup)

            return TYPING_TO_DELETE_BUTTON
        else:
            bot.send_message(update.callback_query.message.chat.id,
                             """You have no buttons created yet. Create your first button by clicking "Create" """)
            get_help(bot, update)

            return ConversationHandler.END

    def delete_button_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        to_delete_button = custom_buttons_table.find_one({
            "button": txt,
            "bot_id": bot.id
        })
        if "photo_files" in to_delete_button:
            for file in to_delete_button["photo_files"]:
                os.remove(file)
        if "document_files" in to_delete_button:
            for file in to_delete_button["document_files"]:
                os.remove(file)
        if "audio_files" in to_delete_button:
            for file in to_delete_button["audio_files"]:
                os.remove(file)
        if "video_files" in to_delete_button:
            for file in to_delete_button["video_files"]:
                os.remove(file)
        custom_buttons_table.delete_one({
            "button": txt,
            "bot_id": bot.id
        })
        update.message.reply_text(
            'Thank you! We deleted the button {}'.format(txt), reply_markup=ReplyKeyboardRemove())
        get_help(bot, update)
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        user_data.clear()

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
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
                                       pattern=r"create_button"),
                  CallbackQueryHandler(callback=AddCommands().back,
                                       pattern=r"cancel_add_button", pass_user_data=True)],

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
