import os

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
import logging
from database import custom_buttons_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.restart_program import restart_program

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TYPING_BUTTON, TYPING_DESCRIPTION, DESCRIPTION_FINISH = range(3)
TYPING_TO_DELETE_BUTTON = 1
__mod_name__ = "Custom buttons"

__admin_keyboard__ = [["/create_button"], ["/delete_button"]]

__admin_help__ = """
 - /create_button - to create a custom button for your bot
 - /delete_button -  delete a button with a specific name\n

"""


class AddCommands(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_add_button")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)
        finish_buttons = list()
        finish_buttons.append([InlineKeyboardButton(text="Back", callback_data="help_back")])
        self.finish_reply_markup = InlineKeyboardMarkup(
            buttons)

    def start(self, bot, update):
        reply_keyboard = [['About', 'Contacts'],
                          ['Rules', 'Useful links']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            "Please type your new button, for example 'Contacts' or 'Rules'. Please note that"
            "you can't modify the buttons available by default ", reply_keyboard=markup)
        update.message.reply_text("To quit, click 'Back'", reply_markup=self.reply_markup)
        return TYPING_BUTTON

    def button_handler(self, bot, update, user_data):
        # TODO commands /command must be inline buttons, not one-time keyboard
        # TODO delete files as well
        # TODO create a chatbot specially for OG
        chat_id, txt = initiate_chat_id(update)
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": bot.id,
            "button": txt})
        if button_list_of_dicts.count() == 0:

            user_data['button'] = txt
            update.message.reply_text('Excellent! Now, please send me a text, an image, a video'
                                      ' or a document to display for your new button',
                                      reply_markup=self.reply_markup)
            return TYPING_DESCRIPTION
        else:
            update.message.reply_text('You already have a button with the same name. Please choose another name',
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

        if update.message.text:
            if update.message.text == "DONE":
                self.description_finish(bot, update, user_data)
            elif "descriptions" not in user_data:
                user_data["descriptions"] = [update.message.text]
            elif user_data["descriptions"] is not None:
                user_data["descriptions"].append(update.message.text)
            else:
                user_data["descriptions"] = list()

        if update.message.photo:
            filename = 'photo_{}_button_{}.jpg'.format(str(bot.id),
                                                       str(user_data['button']))
            photo_file = update.message.photo[-1].get_file(file_name=filename)
            custom_path = photo_directory + "/" + filename
            photo_file.download(custom_path=custom_path)
            if "photo_files" not in user_data:
                user_data["photo_files"] = [custom_path]
            elif user_data["photo_files"] is not None:
                user_data["photo_files"] = user_data["photo_files"].append(custom_path)
            else:
                user_data["photo_files"] = list()

        if update.message.audio:
            filename = 'audio_{}_button_{}.mp3'.format(str(bot.id),
                                                       str(user_data['button']))
            audio_file = update.message.audio.get_file(file_name=filename)
            custom_path = audio_directory + "/" + filename
            audio_file.download(custom_path=custom_path)
            if "audio_files" not in user_data:
                user_data["audio_files"] = [custom_path]
            elif user_data["audio_files"] is not None:
                user_data["audio_files"] = user_data["audio_files"].append(custom_path)
            else:
                user_data["audio_files"] = list()

        if update.message.voice:
            filename = 'voice_{}_button_{}.mp3'.format(str(bot.id),
                                                       str(user_data['button']))
            voice_file = update.message.voice.get_file(file_name=filename)
            custom_path = audio_directory + "/" + filename
            voice_file.download(custom_path=custom_path)
            if "audio_files" not in user_data:
                user_data["audio_files"] = [custom_path]
            elif user_data["audio_files"] is not None:
                user_data["audio_files"] = user_data["audio_files"].append(custom_path)
            else:
                user_data["audio_files"] = list()

        if update.message.document:
            filename = 'document_{}_button_{}.pdf'.format(str(bot.id),
                                                          str(user_data['button']))
            document_file = update.message.document.get_file(file_name=filename)
            custom_path = document_directory + "/" + filename
            document_file.download(custom_path=custom_path)
            if "document_files" not in user_data:
                user_data["document_files"] = [custom_path]
            elif user_data["document_files"] is not None:
                user_data["document_files"] = user_data["document_files"].append(custom_path)
            else:
                user_data["document_files"] = list()

        if update.message.video:
            filename = 'video_{}_button_{}.mp4'.format(str(bot.id),
                                                       str(user_data['button']))
            video_file = update.message.video.get_file(file_name=filename)
            custom_path = video_directory + "/" + filename

            video_file.download(custom_path=custom_path)

            if "video_files" not in user_data:
                user_data["video_files"] = [custom_path]
            elif user_data["video_files"] is not None:
                user_data["video_files"] = user_data["video_files"] \
                    .append(custom_path)
            else:
                user_data["video_files"] = list()

        if update.message.video_note:
            filename = 'video_note_{}_button_{}.mp4'.format(str(bot.id),
                                                            str(user_data['button']))
            video_note_file = update.message.audio.get_file()
            custom_path = video_directory + "/" + filename
            video_note_file.download(filename, custom_path=custom_path)

            if "video_files" not in user_data:
                user_data["video_files"] = [custom_path]
            elif user_data["video_files"] is not None:
                user_data["video_files"] = user_data["video_files"] \
                    .append(custom_path)
            else:
                user_data["video_files"] = list()

        update.message.reply_text('Great! You can add one more file or text to display.\n'
                                  'If you think that this is enough, click DONE',
                                  reply_markup=ReplyKeyboardMarkup([["DONE"]]))
        update.message.reply_text("Click Back to cancel", reply_markup=self.reply_markup)
        return TYPING_DESCRIPTION

    def description_finish(self, bot, update, user_data):
        user_id = update.message.from_user.id
        user_data.update({"button": user_data['button'],
                          "button_lower": user_data['button'].replace(" ", "").lower(),
                          "admin_id": user_id,
                          "bot_id": bot.id,
                          })
        custom_buttons_table.save(user_data)

        update.message.reply_text(
            'Thank you! Now your button will be accessible by typing or clicking the button \n'
            '{} in menu'.format(user_data["button"]), reply_markup=self.finish_reply_markup)
        restart_program(bot, update)

        return ConversationHandler.END

    def delete_button(self, bot, update):
        button_list_of_dicts = custom_buttons_table.find({
            "bot_id": bot.id})
        if button_list_of_dicts.count() != 0:
            button_list = [button['button'] for button in button_list_of_dicts]
            reply_keyboard = [button_list]
            update.message.reply_text(
                "Please choose the button that button that you want to delete",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            update.message.reply_text("To quit, click 'Back'", reply_markup=self.reply_markup)

            return TYPING_TO_DELETE_BUTTON
        else:
            reply_keyboard = [["/create_button"]]
            update.message.reply_text(
                "You have no buttons created yet. Please create your first button by clicking /create_button command",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            update.message.reply_text("Click Back  for menu", reply_markup=self.reply_markup)

            return ConversationHandler.END

    def delete_button_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        custom_buttons_table.delete_one({
            "button": txt,
            "bot_id": bot.id
        })
        update.message.reply_text(
            'Thank you! We deleted the button {}'.format(txt), reply_markup=self.finish_reply_markup)
        restart_program(bot, update)

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

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)


# Get the dispatcher to register handlers


# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
BUTTON_ADD_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('create_button', AddCommands().start),
                  CallbackQueryHandler(callback=AddCommands().back, pattern=r"cancel_add_button")],

    states={
        TYPING_BUTTON: [
            MessageHandler(Filters.text,
                           AddCommands().button_handler, pass_user_data=True)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.all,
                                            AddCommands().description_handler, pass_user_data=True),
                             CallbackQueryHandler(callback=AddCommands().back, pattern=r"cancel_add_button")],
        DESCRIPTION_FINISH: [MessageHandler(Filters.all,
                                            AddCommands().description_finish, pass_user_data=True),
                             CallbackQueryHandler(callback=AddCommands().back, pattern=r"cancel_add_button")],

    },

    fallbacks=[
        CallbackQueryHandler(callback=AddCommands().back, pattern=r"cancel_add_button"),
        CommandHandler("done", callback=AddCommands().description_finish, pass_user_data=True),
        CommandHandler('cancel', AddCommands().cancel),
        MessageHandler(filters=Filters.command, callback=AddCommands().cancel)
    ]
)
DELETE_BUTTON_HANDLER = ConversationHandler(
    entry_points=[CommandHandler("delete_button", AddCommands().delete_button),
                  CallbackQueryHandler(callback=AddCommands().back, pattern=r"cancel_add_button")],

    states={
        TYPING_TO_DELETE_BUTTON: [MessageHandler(Filters.text,
                                                 AddCommands().delete_button_finish),
                                  CallbackQueryHandler(callback=AddCommands().back, pattern=r"cancel_add_button")],
    },

    fallbacks=[CallbackQueryHandler(callback=AddCommands().back, pattern=r"cancel_add_button"),
               CommandHandler('cancel', AddCommands().cancel),
               MessageHandler(filters=Filters.command, callback=AddCommands().cancel)
               ]
)
