#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import CommandHandler, MessageHandler, Filters, \
    ConversationHandler, CallbackQueryHandler
import logging
from database import custom_buttons_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)
CHOOSE_BUTTON = 1
EDIT_FINISH = 1


class ButtonEdit(object):
    def start(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        all_buttons = custom_buttons_table.find({"bot_id": bot.id})
        if all_buttons:
            bot.send_message(chat_id=update.callback_query.message.chat_id,
                             text=string_dict(bot)["manage_button_str_1"],
                             reply_markup=ReplyKeyboardMarkup(
                                 [[button_name["button"]] for button_name in all_buttons])
                             )
            return CHOOSE_BUTTON
        else:
            bot.send_message(chat_id=update.callback_query.message.chat_id,  # TODO send as in polls
                             text=string_dict(bot)["manage_button_str_2"],
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(string_dict(bot)["create_button_button"],
                                                        callback_data="create_button"),
                                   InlineKeyboardButton(string_dict(bot)["back_button"],
                                                        callback_data="help_back")]]
                             ))
            return ConversationHandler.END

    def choose_button(self, bot, update):

        try:
            button_info = custom_buttons_table.find_one(
                {"bot_id": bot.id, "button": update.message.text}
            )
            if "descriptions" in button_info:
                for descr in button_info["descriptions"]:
                    update.message.reply_text(
                        text=descr,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_button"],
                                                 callback_data="b_{}___{}".format(descr[:10],
                                                                                         update.message.text))]])
                    )
            if "audio_files" in button_info:
                for filename in button_info["audio_files"]:
                    update.message.reply_audio(
                        filename,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     filename[:10], update.message.text))]])
                    )
            if "video_files" in button_info:
                for filename in button_info["video_files"]:
                    update.message.reply_video(
                        filename,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     filename[:10], update.message.text))]])
                    )
            if "document_files" in button_info:
                for filename in button_info["document_files"]:
                    update.message.reply_document(
                        filename,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     filename[:10], update.message.text))]])
                    )
            if "photo_files" in button_info:
                for filename in button_info["photo_files"]:
                    print(filename)
                    update.message.reply_photo(
                        filename,
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     filename[:10], update.message.text))]])
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
                         text=string_dict(bot)["manage_button_str_3"],
                         reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id=update.message.chat_id,
                         text=string_dict(bot)["back_text"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]])
                         )
        return ConversationHandler.END

    def edit_button(self, bot, update, user_data):
        reply_buttons = [
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="cancel_edit_button")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("b_", "").split("___")  # here is the problem
        user_data["content_id"] = content_data[0]
        user_data["button"] = content_data[1]
        bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text=string_dict(bot)["manage_button_str_4"],
                         reply_markup=reply_markup)
        return EDIT_FINISH

    def edit_button_finish(self, bot, update, user_data):
        # Remove the old file or text
        button_info = custom_buttons_table.find_one(
            {"bot_id": bot.id, "button": user_data["button"]}
        )
        user_data["button_info"] = button_info
        for key, value in user_data["button_info"].items():
            if "_files" in key:
                for content in button_info[key]:
                    if user_data["content_id"] in content:
                        button_info[key].remove(content)

        if update.message.text:
            if "descriptions" not in button_info:
                button_info["descriptions"] = []
            button_info["descriptions"].append(update.message.text)

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            if "photo_files" not in button_info:
                button_info["photo_files"] = []
            button_info["photo_files"].append(photo_file)

        elif update.message.audio:
            if "audio_files" not in button_info:
                button_info["audio_files"] = []
            audio_file = update.message.audio.get_file().file_id
            button_info["audio_files"].append(audio_file)

        elif update.message.voice:
            if "audio_files" not in button_info:
                button_info["audio_files"] = []
            voice_file = update.message.voice.get_file().file_id
            button_info["audio_files"].append(voice_file)

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            button_info["document_files"].append(document_file)

        elif update.message.video:
            if "video_files" not in button_info:
                button_info["video_files"] = []
            video_file = update.message.video.get_file().file_id
            button_info["video_files"].append(video_file)

        elif update.message.video_note:
            if "video_files" not in button_info:
                button_info["video_files"] = []
            video_note_file = update.message.audio.get_file().file_id
            button_info["video_files"].append(video_note_file)

        custom_buttons_table.replace_one(
            {"bot_id": bot.id, "button": user_data["button"]},
            button_info
        )
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]]
        bot.send_message(chat_id=update.message.chat_id,
                         text=string_dict(bot)["manage_button_str_5"],
                         reply_markup=InlineKeyboardMarkup(buttons))
        logger.info("Admin {} on bot {}:{} did  the following edit button: {}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["button"]))
        user_data.clear()
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["manage_button_str_6"], reply_markup=ReplyKeyboardRemove()
                         )
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
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
        CallbackQueryHandler(callback=ButtonEdit().back, pattern=r"error_back"),
        CommandHandler('cancel', ButtonEdit().cancel),
        MessageHandler(filters=Filters.command, callback=ButtonEdit().cancel)
    ]
)

BUTTON_EDIT_FINISH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ButtonEdit().edit_button,
                                       pattern=r"b_", pass_user_data=True)],

    states={

        EDIT_FINISH: [MessageHandler(Filters.all, ButtonEdit().edit_button_finish, pass_user_data=True),
                      CallbackQueryHandler(callback=ButtonEdit().back,
                                           pattern=r"cancel_edit_button", pass_user_data=True),
                      ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"cancel_edit_button", pass_user_data=True),
        CallbackQueryHandler(callback=ButtonEdit().back, pattern=r"error_back"),
        CommandHandler('cancel', ButtonEdit().cancel),
        MessageHandler(filters=Filters.command, callback=ButtonEdit().cancel),

    ]
)
