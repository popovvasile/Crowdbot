import os
import uuid

from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import CommandHandler, MessageHandler, Filters, \
    ConversationHandler, CallbackQueryHandler
import logging
from database import custom_buttons_table, chatbots_table
from modules.helper_funcs.helper import get_help

# from modules.helper_funcs.restart_program import restart_program

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)
CHOOSE_BUTTON = 1
EDIT_FINISH = 1


class ButtonEdit(object):
    def __init__(self):
        reply_buttons = [[InlineKeyboardButton(text="Back", callback_data="cancel_edit_button")]]
        self.reply_markup = InlineKeyboardMarkup(
            reply_buttons)

    def start(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        all_buttons = custom_buttons_table.find({"bot_id": bot.id})
        if all_buttons:
            bot.send_message(chat_id=update.callback_query.message.chat_id,
                             text="Please choose the button that you want to edit (or click /cancel)",
                             reply_markup=ReplyKeyboardMarkup(
                                 [[button_name["button"]] for button_name in all_buttons])
                             )
            return CHOOSE_BUTTON
        else:
            bot.send_message(chat_id=update.callback_query.message.chat_id,  # TODO send as in polls
                             text="You have no custom buttons to edit. Please create a button first",
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton("Create button", callback_data="create_button"),
                                   InlineKeyboardButton("Back", callback_data="help_back")]]
                             ))
            return ConversationHandler.END

    def choose_button(self, bot, update):
        photo_directory = "files/{bot_id}/photo".format(bot_id=bot.id)
        audio_directory = "files/{bot_id}/audio".format(bot_id=bot.id)
        document_directory = "files/{bot_id}/document".format(bot_id=bot.id)
        video_directory = "files/{bot_id}/video".format(bot_id=bot.id)
        try:
            button_info = custom_buttons_table.find_one(
                {"bot_id": bot.id, "button": update.message.text}
            )
            if "descriptions" in button_info:
                for descr in button_info["descriptions"]:
                    update.message.reply_text(
                        text=descr,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text="EDIT",
                                                 callback_data="btn_edit_{}___{}".format(descr,
                                                                                       update.message.text))]])
                    )
            if "audio_files" in button_info:
                for filename in button_info["audio_files"]:
                    with open(audio_directory + "/" + filename, 'rb') as file:
                        update.message.reply_audio(
                            file,
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton(text="EDIT",
                                                     callback_data="btn_edit_{}___{}".format(
                                                         filename, update.message.text))]])
                        )
            if "video_files" in button_info:
                for filename in button_info["video_files"]:
                    with open(video_directory + "/" + filename, 'rb') as file:
                        update.message.reply_video(
                            file,
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton(text="EDIT",
                                                     callback_data="btn_edit_{}___{}".format(
                                                         filename, update.message.text))]])
                        )
            if "document_files" in button_info:
                for filename in button_info["document_files"]:
                    with open(document_directory + "/" + filename, 'rb') as file:
                        update.message.reply_document(
                            file,
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton(text="EDIT",
                                                     callback_data="btn_edit_{}___{}".format(
                                                         filename, update.message.text))]])
                        )
            if "photo_files" in button_info:
                for filename in button_info["photo_files"]:
                    with open(photo_directory + "/" + filename, 'rb') as file:
                        update.message.reply_photo(
                            file,
                            reply_markup=InlineKeyboardMarkup([[
                                InlineKeyboardButton(text="EDIT",
                                                     callback_data="btn_edit_{}___{}".format(
                                                         filename, update.message.text))]])
                        )
        except BadRequest as excp:
            if excp.message == "Message is not modified":
                pass
            elif excp.message == "Query_id_invalid":
                pass
            elif excp.message == "Message can't be deleted":
                pass
            else:
                LOGGER.exception("Exception in edit buttons")
        bot.send_message(chat_id=update.message.chat_id,
                         text="Please choose the part that you want to replace",
                         reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id=update.message.chat_id,
                         text="Or click Back to cancel",
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text="Back", callback_data="help_back")]])
                         )
        return ConversationHandler.END

    def edit_button(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("btn_edit_", "").split("___")  # here is the problem
        user_data["content_id"] = content_data[0]
        user_data["button"] = content_data[1]
        bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text="Send me the new content to update the old one",
                         reply_markup=self.reply_markup)
        return EDIT_FINISH

    def edit_button_finish(self, bot, update, user_data):
        photo_directory = "files/{bot_id}/photo".format(bot_id=bot.id)
        audio_directory = "files/{bot_id}/audio".format(bot_id=bot.id)
        document_directory = "files/{bot_id}/document".format(bot_id=bot.id)
        video_directory = "files/{bot_id}/video".format(bot_id=bot.id)
        # Remove the old file or text
        button_info = custom_buttons_table.find_one(
            {"bot_id": bot.id, "button": user_data["button"]}
        )
        user_data["button_info"] = button_info
        if "audio_" in user_data["content_id"]:
            button_info["audio_files"].remove(user_data["content_id"])
            os.remove(audio_directory + "/" + user_data["content_id"])

        elif "video_" in user_data["content_id"]:
            button_info["video_files"].remove(user_data["content_id"])
            os.remove(video_directory + "/" + user_data["content_id"])

        elif "document_" in user_data["content_id"]:
            button_info["document_files"].remove(user_data["content_id"])
            os.remove(document_directory + "/" + user_data["content_id"])

        elif "photo_" in user_data["content_id"]:
            button_info["photo_files"].remove(user_data["content_id"])
            os.remove(photo_directory + "/" + user_data["content_id"])

        else:
            button_info["descriptions"].remove(user_data["content_id"])

        if update.message.text:
            if "descriptions" not in button_info:
                button_info["descriptions"] = []
            button_info["descriptions"].append(update.message.text)

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file()
            filename = 'photo_{}.jpg'.format(str(uuid.uuid4())[:10])
            custom_path = photo_directory + "/" + filename
            photo_file.download(custom_path=custom_path)
            if "photo_files" not in button_info:
                button_info["photo_files"] = []
            button_info["photo_files"].append(filename)

        elif update.message.audio:
            if "audio_files" not in button_info:
                button_info["audio_files"] = []
            audio_file = update.message.audio.get_file()
            filename = 'audio_{}.mp3'.format(str(uuid.uuid4())[:10])
            custom_path = audio_directory + "/" + filename
            audio_file.download(custom_path=custom_path)
            button_info["audio_files"].append(filename)

        elif update.message.voice:
            if "audio_files" not in button_info:
                button_info["audio_files"] = []
            voice_file = update.message.voice.get_file()
            filename = 'voice_{}.mp3'.format(str(uuid.uuid4())[:10])
            custom_path = audio_directory + "/" + filename
            voice_file.download(custom_path=custom_path)
            button_info["audio_files"].append(filename)

        elif update.message.document:

            document_file = update.message.document.get_file()
            filename = 'document_{}'.format(str(uuid.uuid4())[:10])
            custom_path = document_directory + "/" + filename
            document_file.download(custom_path=custom_path)
            button_info["document_files"].append(filename)

        elif update.message.video:
            if "video_files" not in button_info:
                button_info["video_files"] = []
            video_file = update.message.video.get_file()
            filename = 'video_{}.mp4'.format(str(uuid.uuid4())[:10])
            custom_path = video_directory + "/" + filename

            video_file.download(custom_path=custom_path)
            button_info["video_files"].append(filename)

        elif update.message.video_note:
            if "video_files" not in button_info:
                button_info["video_files"] = []
            video_note_file = update.message.audio.get_file()
            filename = 'video_note_{}.mp4'.format(str(uuid.uuid4())[:10])
            custom_path = video_directory + "/" + filename
            video_note_file.download(filename, custom_path=custom_path)
            button_info["video_files"].append(filename)

        custom_buttons_table.replace_one(
            {"bot_id": bot.id, "button": user_data["button"]},
            button_info
        )
        buttons = [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
        bot.send_message(chat_id=update.message.chat_id,
                         text="Great! Your content has been changed!",
                         reply_markup=InlineKeyboardMarkup(buttons))
        logger.info("Admin {} on bot {}:{} did  the following edit button: {}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["button"]))
        user_data.clear()
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        user_data.clear()
        bot.send_message(update.callback_query.message.chat.id,
                         "Button creation was stopped", reply_markup=ReplyKeyboardRemove()
                         )
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    def cancel(self, bot, update):
        bot.delete_message(chat_id=update.message.chat_id,
                           message_id=update.message.message_id)
        bot.send_message(update.message.chat.id,
                         "Command is cancelled", reply_markup=ReplyKeyboardRemove()
                         )

        get_help(bot, update)
        return ConversationHandler.END

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        LOGGER.warning('Update "%s" caused error "%s"', update, error)


# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
BUTTON_EDIT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ButtonEdit().start,
                                       pattern=r"edit_button")],

    states={
        CHOOSE_BUTTON: [MessageHandler(Filters.text, ButtonEdit().choose_button),
                        CallbackQueryHandler(callback=ButtonEdit().back,
                                             pattern=r"cancel_edit_button", pass_user_data=True),
                        ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"cancel_edit_button", pass_user_data=True),
        CommandHandler('cancel', ButtonEdit().cancel),
        MessageHandler(filters=Filters.command, callback=ButtonEdit().cancel)
    ]
)

BUTTON_EDIT_FINISH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ButtonEdit().edit_button,
                                       pattern=r"btn_edit_", pass_user_data=True)],

    states={

        EDIT_FINISH: [MessageHandler(Filters.all, ButtonEdit().edit_button_finish, pass_user_data=True),
                      CallbackQueryHandler(callback=ButtonEdit().back,
                                           pattern=r"cancel_edit_button", pass_user_data=True),
                      ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"cancel_edit_button", pass_user_data=True),
        CommandHandler('cancel', ButtonEdit().cancel),
        MessageHandler(filters=Filters.command, callback=ButtonEdit().cancel)
    ]
)
