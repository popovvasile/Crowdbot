#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import logging
from database import custom_buttons_table
from helper_funcs.helper import get_help

from helper_funcs.misc import delete_messages

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)
CHOOSE_BUTTON = 1
EDIT_FINISH = 1


class ButtonEdit(object):
    def start(self, update, context):
        context.user_data["to_delete"] = []
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        all_buttons = custom_buttons_table.find({"bot_id": context.bot.id})
        if all_buttons.count() > 0:
            context.user_data["to_delete"].append(context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                                                           text=context.bot.lang_dict["manage_button_str_1"],
                                                           reply_markup=ReplyKeyboardMarkup(
                                                               [[button_name["button"]] for button_name in all_buttons]
                                                           ),
                                                           parse_mode='Markdown'))
            return CHOOSE_BUTTON
        else:
            context.user_data["to_delete"].append(context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                                                           text=context.bot.lang_dict["manage_button_str_2"],
                                                           reply_markup=InlineKeyboardMarkup(
                                                               [[InlineKeyboardButton(
                                                                   context.bot.lang_dict["create_button_button"],
                                                                   callback_data="create_button"),
                                                                   InlineKeyboardButton(
                                                                       context.bot.lang_dict["back_button"],
                                                                       callback_data="help_module(settings)")]]
                                                           ), parse_mode='Markdown'))
            return ConversationHandler.END

    def choose_button(self, update, context):

        try:
            button_info = custom_buttons_table.find_one(
                {"bot_id": context.bot.id, "button": update.message.text}
            )
            for content in button_info["content"]:
                if "text" in content:
                    context.user_data["to_delete"].append(update.message.reply_text(
                        text=content["text"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(content["text"][:10],
                                                                                  update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["text"][:10],
                                                                                  update.message.text))
                        ]]),
                        parse_mode='Markdown'))
                if "audio_file" in content:
                    context.user_data["to_delete"].append(update.message.reply_audio(
                        content["audio_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     content["audio_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["audio_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "voice_file" in content:
                    context.user_data["to_delete"].append(update.message.reply_voice(
                        content["voice_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     content["voice_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["voice_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "video_file" in content:
                    context.user_data["to_delete"].append(update.message.reply_video(
                        content["video_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     content["video_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["video_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "video_note_file" in content:
                    context.user_data["to_delete"].append(update.message.reply_video_note(
                        content["video_note_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     content["video_note_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["video_note_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "document_file" in content:
                    context.user_data["to_delete"].append(update.message.reply_document(
                        content["document_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     content["document_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["document_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "photo_file" in content:
                    context.user_data["to_delete"].append(update.message.reply_photo(
                        content["photo_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     content["photo_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["photo_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "animation_file" in content:
                    context.user_data["to_delete"].append(update.message.reply_animation(
                        content["animation_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     content["animation_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["animation_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "sticker_file" in content:
                    context.user_data["to_delete"].append(update.message.reply_sticker(
                        content["photo_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=context.bot.lang_dict["edit_button"],
                                                 callback_data="b_{}___{}".format(
                                                     content["sticker_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["sticker_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
        except BadRequest as excp:
            if excp.message == "Message is not modified":
                pass
            elif excp.message == "Query_id_invalid":
                pass
            elif excp.message == "Message can't be deleted":
                pass
            else:
                LOGGER.exception("Exception in edit buttons")
        context.user_data["to_delete"].append(context.bot.send_message(
                                                       chat_id=update.message.chat_id,
                                                       text=context.bot.lang_dict["manage_button_str_3"],
                                                       reply_markup=ReplyKeyboardRemove()))
        context.user_data["to_delete"].append(context.bot.send_message( chat_id=update.message.chat_id,
                                                       text=context.bot.lang_dict["add_button_content"],
                                                       reply_markup=InlineKeyboardMarkup(
                                                           [[InlineKeyboardButton(text=context.bot.lang_dict["add_button"],
                                                                                  callback_data="add_content{}".format(
                                                                                      update.message.text))]])))
        context.user_data["to_delete"].append(context.bot.send_message( chat_id=update.message.chat_id,
                                                       text=context.bot.lang_dict["back_text"],
                                                       reply_markup=InlineKeyboardMarkup(
                                                           [[
                                                               InlineKeyboardButton(
                                                                   context.bot.lang_dict["back_button"],
                                                                   callback_data="help_module(settings)")]])))
        return ConversationHandler.END

    def edit_button(self, update, context):
        reply_buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"], callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("b_", "").split("___")  # here is the problem
        context.user_data["content_id"] = content_data[0]
        context.user_data["button"] = content_data[1]
        context.user_data["to_delete"].append(
            context.bot.send_message( chat_id=update.callback_query.message.chat_id,
                             text=context.bot.lang_dict["manage_button_str_4"],
                             reply_markup=reply_markup))
        return EDIT_FINISH

    def edit_button_finish(self, update, context):
        # Remove the old file or text
        button_info = custom_buttons_table.find_one(
            {"bot_id": context.bot.id, "button": context.user_data["button"]}
        )
        content_index = len(button_info["content"])
        for index, content_dict in enumerate(button_info["content"]):
            if any(context.user_data["content_id"] in ext for ext in content_dict.values()):
                content_index = index
                button_info["content"].remove(content_dict)

        if update.message.text:
            button_info["content"].insert(content_index, {"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            button_info["content"].insert(content_index, {"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            button_info["content"].insert(content_index, {"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            button_info["content"].insert(content_index, {"voice_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            button_info["content"].insert(content_index, {"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            button_info["content"].insert(content_index, {"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            button_info["content"].insert(content_index, {"video_note_file": video_note_file})
        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            button_info["content"].insert(content_index, {"sticker_file": sticker_file})
        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            button_info["content"].insert(content_index, {"animation_file": animation_file})
        custom_buttons_table.replace_one(
            {"bot_id": context.bot.id, "button": context.user_data["button"]},
            button_info
        )
        buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(settings)")]]
        context.bot.send_message( chat_id=update.message.chat_id,
                         text=context.bot.lang_dict["manage_button_str_5"],
                         reply_markup=InlineKeyboardMarkup(buttons))
        logger.info("Admin {} on bot {}:{} did  the following edit button: {}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, context.user_data["button"]))
        context.user_data.clear()
        return ConversationHandler.END

    # help_module(settings)
    def back_from_edit_button(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        delete_messages(update, context)
        get_help(update, context)

    def back(self, update, context):
        context.bot.send_message(update.callback_query.message.chat.id,
                         context.bot.lang_dict["manage_button_str_6"], reply_markup=ReplyKeyboardRemove(),
                         parse_mode='Markdown'
                         )
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(update, context)
        context.user_data.clear()
        return ConversationHandler.END

    def cancel(self, update, context):
        context.bot.delete_message(chat_id=update.message.chat_id,
                           message_id=update.message.message_id)
        context.bot.send_message(update.message.chat.id,
                         "Command is cancelled", reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown'
                         )

        get_help(update, context)
        return ConversationHandler.END


class AddButtonContent(object):
    def add_content_button(self, update, context):
        reply_buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"], callback_data="help_module(settings)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("add_content", "")  # here is the problem
        context.user_data["button"] = content_data
        context.bot.send_message( chat_id=update.callback_query.message.chat_id,
                         text=context.bot.lang_dict["manage_button_str_4"],
                         reply_markup=reply_markup)
        return EDIT_FINISH

    def add_content_button_finish(self, update, context):
        button_info = custom_buttons_table.find_one(
            {"bot_id": context.bot.id, "button": context.user_data["button"]}
        )
        if update.message.text:
            button_info["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            button_info["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            button_info["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            button_info["content"].append({"voice_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            button_info["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            button_info["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            button_info["content"].append({"video_note_file": video_note_file})
        elif update.message.animation:
            animation_file = update.message.audio.get_file().file_id
            button_info["content"].append({"animation_file": animation_file})
        elif update.message.sticker:
            sticker_file = update.message.audio.get_file().file_id
            button_info["content"].append({"sticker_file": sticker_file})

        custom_buttons_table.replace_one(
            {"bot_id": context.bot.id, "button": context.user_data["button"]},
            button_info
        )
        buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(settings)")]]
        context.bot.send_message( chat_id=update.message.chat_id,
                         text=context.bot.lang_dict["manage_button_str_5"],
                         reply_markup=InlineKeyboardMarkup(buttons))
        logger.info("Admin {} on bot {}:{} did  the following edit button: {}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, context.user_data["button"]))
        context.user_data.clear()
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.send_message(update.callback_query.message.chat.id,
                         context.bot.lang_dict["manage_button_str_6"], reply_markup=ReplyKeyboardRemove()
                         )
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(update, context)
        context.user_data.clear()
        return ConversationHandler.END

    def cancel(self, update, context):
        context.bot.delete_message(chat_id=update.message.chat_id,
                           message_id=update.message.message_id)
        context.bot.send_message(update.message.chat.id,
                         "Command is cancelled", reply_markup=ReplyKeyboardRemove()
                         )

        get_help(update, context)
        return ConversationHandler.END


class DeleteButtonContent(object):

    def delete_message(self, update, context):
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(settings)")])
        reply_markup = InlineKeyboardMarkup(
            buttons)

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("d_", "").split("___")  # here is the problem
        context.user_data["content_id"] = content_data[0]
        context.user_data["button"] = content_data[1]
        button_info = custom_buttons_table.find_one(
            {"bot_id": context.bot.id, "button": context.user_data["button"]}
        )
        for content_dict in button_info["content"]:
            if any(context.user_data["content_id"] in ext for ext in content_dict.values()):
                button_info["content"].remove(content_dict)
        context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text=context.bot.lang_dict["delete_content"],
                         reply_markup=reply_markup)
        custom_buttons_table.replace_one(
            {"bot_id": context.bot.id, "button": context.user_data["button"]},
            button_info
        )
        return ConversationHandler.END


# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
BUTTON_EDIT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ButtonEdit().start,
                                       pattern=r"edit_button")],

    states={
        CHOOSE_BUTTON: [MessageHandler(Filters.text, ButtonEdit().choose_button),
                        ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"help_module"),
    ]
)

BUTTON_EDIT_FINISH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ButtonEdit().edit_button,
                                       pattern=r"b_")],

    states={

        EDIT_FINISH: [MessageHandler(Filters.all, ButtonEdit().edit_button_finish),
                      CallbackQueryHandler(callback=ButtonEdit().back,
                                           pattern=r"help_module"),
                      ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"help_module")
    ]
)
BUTTON_ADD_FINISH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddButtonContent().add_content_button,
                                       pattern=r"add_content")],

    states={

        EDIT_FINISH: [MessageHandler(Filters.all, AddButtonContent().add_content_button_finish),
                      ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"help_module"),
    ]
)
DELETE_CONTENT_HANDLER = CallbackQueryHandler(pattern="d_",
                                              callback=DeleteButtonContent().delete_message)
back_from_edit_button_handler = CallbackQueryHandler(callback=ButtonEdit().back_from_edit_button,
                                                     pattern="back_from_edit_button")
