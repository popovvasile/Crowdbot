#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler
from database import groups_table
from telegram.error import TelegramError
from helper_funcs.helper import get_help


# database schema
from logs import logger

group_table_scheme = {
    'bot_id': int,
    'group_name': str,
    'chat_id': int
}

MY_GROUPS, MANAGE_GROUP, ADD_GROUP, \
CHOOSE_TO_REMOVE, REMOVE_GROUP, \
CHOOSE_TO_SEND_POST, POST_TO_GROUP, MESSAGE_TO_USERS = range(8)
CHOOSE_GROUP_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(2)


def delete_messages(update, context):
    try:
        context.bot.delete_message(update.effective_message.chat.id, update.effective_message.message_id)

        if 'to_delete' in context.user_data:
            for msg in context.user_data['to_delete']:
                try:
                    if msg.message_id != update.effective_message.message_id:
                        context.bot.delete_message(update.effective_message.chat.id, msg.message_id)
                except TelegramError:
                    # print('except in delete_message---> {}, {}'.format(e, msg_id))
                    continue
            context.user_data['to_delete'] = list()
        else:
            context.user_data['to_delete'] = list()
    except:
        pass

    # to make keyboard with groups
    ################################################################


def groups_menu(update, context):
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
    groups = groups_table.find({'bot_id': context.bot.id})
    command_list = [[InlineKeyboardButton(x['group_name'],
                                          callback_data="group_{}".format(x['group_id']))]
                    for x in groups] + \
                   [[InlineKeyboardButton(context.bot.lang_dict["add_group"], callback_data='add_group')],
                    [InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                          callback_data="help_module(channels_groups)")]]
    context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["groups"],
                             reply_markup=InlineKeyboardMarkup(command_list))
    return ConversationHandler.END


# DELETING USING USER_DATA
class Groups(object):
    # ################################## HELP METHODS ###########################################################

    def group(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        group_id = update.callback_query.data.replace("group_", "")
        one_group_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(context.bot.lang_dict["send_donation_to_group"],
                                                        callback_data='send_donation_to_group_{}'.format(group_id
                                                                                                         ))],
                                  [InlineKeyboardButton(context.bot.lang_dict["send_survey_to_group"],
                                                        callback_data="send_survey_to_group_{}".format(
                                                            group_id))],
                                  [InlineKeyboardButton(context.bot.lang_dict["send_post_to_group"],
                                                        callback_data='write_post_group_{}'.format(
                                                            group_id))],
                                  [InlineKeyboardButton(context.bot.lang_dict["remove_button_str"],
                                                        callback_data='remove_group_{}'.format(
                                                            group_id))],
                                  [InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                                        callback_data="help_module(channels_groups)")]])
        context.bot.send_message(update.callback_query.message.chat_id, context.bot.lang_dict["groups_menu"],
                                 reply_markup=one_group_keyboard)
        return ConversationHandler.END

    # call this when user have choose group for remove
    def finish_remove(self, update, context):
        if "to_delete" not in context.user_data:
            context.user_data = {"to_delete": []}
        group_id = int(update.callback_query.data.replace("remove_group_", ""))
        group = groups_table.find_one({'bot_id': context.bot.id, 'group_id': group_id})
        if group:
            delete_messages(update, context)
            groups_table.delete_one({'bot_id': context.bot.id, 'group_id': group_id})
            context.user_data['to_delete'].append(
                context.bot.send_message(update.effective_chat.id, context.bot.lang_dict["group_has_been_removed"]
                                         .format(group["group_name"]),
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                             text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(channels_groups)")]])
                                         ))
            return ConversationHandler.END
        else:
            # need to delete this message
            context.user_data['to_delete'].append(
                context.bot.send_message(update.effective_chat.id, "There is no such group",
                                         reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                             text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(channels_groups)")]])
                                         ))

    def back(self, update, context):
        delete_messages(update, context)
        get_help(update, context)
        return ConversationHandler.END


class SendPost(object):
    def send_message(self, update, context):
        # bot.delete_message(chat_id=update.callback_query.message.chat_id,
        #                    message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_back")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        group_id = update.callback_query.data.replace("write_post_group_", "")
        delete_messages(update, context)
        context.user_data['group'] = group_id
        context.user_data['to_delete'].append(
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["send_post_group"].format(group_id),
                                     reply_markup=reply_markup))
        return MESSAGE_TO_USERS
        # else:
        #     return Groups().make_groups_layout(update, context, CHOOSE_TO_SEND_POST,
        #                                            context.bot.lang_dict["choose_group_to_post"], user_data)

    def received_message(self, update, context):
        if "content" not in context.user_data:
            context.user_data["content"] = []
        if update.message.text:
            context.user_data["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            context.user_data["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            context.user_data["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            context.user_data["content"].append({"audio_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            context.user_data["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            context.user_data["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            context.user_data["content"].append({"video_file": video_note_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["done_button"], callback_data="send_post_finish")],
             [InlineKeyboardButton(text="Cancel", callback_data="help_back")]]
        )
        context.user_data['to_delete'].append(
            context.bot.send_message(update.message.chat_id,
                                     context.bot.lang_dict["send_message_4"],
                                     reply_markup=final_reply_markup))
        return MESSAGE_TO_USERS

    def send_post_finish(self, update, context):
        for content_dict in context.user_data["content"]:
            if "text" in content_dict:
                context.bot.send_message(context.user_data['group'],
                                         content_dict["text"])
            if "audio_file" in content_dict:
                context.bot.send_audio(context.user_data['group'], content_dict["audio_file"])
            if "video_file" in content_dict:
                context.bot.send_video(context.user_data['group'], content_dict["video_file"])
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    context.bot.send_photo(context.user_data['group'], content_dict["document_file"])
                else:
                    context.bot.send_document(context.user_data['group'], content_dict["document_file"])
            if "photo_file" in content_dict:
                context.bot.send_photo(context.user_data['group'], content_dict["photo_file"])

        delete_messages(update, context)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(channels_groups)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.user_data['to_delete'].append(
            context.bot.send_message(update.callback_query.message.chat_id,
                                     context.bot.lang_dict["send_message_5"],
                                     reply_markup=final_reply_markup))
        logger.info("Admin {} on bot {}:{} sent a post to the group".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id))
        context.user_data.clear()
        return ConversationHandler.END

    def help_back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(channels_groups)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.send_message(update.callback_query.message.chat_id,
                                 context.bot.lang_dict["send_message_9"],
                                 reply_markup=final_reply_markup)
        context.user_data.clear()
        return ConversationHandler.END

    def back(self, update, context):
        delete_messages(update, context)
        get_help(update, context)
        return ConversationHandler.END


class AddGroup(object):
    def add_group(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                  callback_data="help_module(channels_groups)")]
        )
        reply_markup = InlineKeyboardMarkup(
            buttons)

        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["add_group_str"],
                                 reply_markup=reply_markup)
        return ConversationHandler.END


ADD_GROUP_HANLDER = CallbackQueryHandler(callback=AddGroup().add_group, pattern="add_group")

GROUPS_MENU = CallbackQueryHandler(callback=groups_menu, pattern="groups")
MY_GROUPS_HANDLER = CallbackQueryHandler(callback=Groups().group, pattern=r"group")

REMOVE_GROUP_HANDLER = CallbackQueryHandler(Groups().finish_remove,
                                            pattern=r"remove_group")


SEND_POST_TO_GROUP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendPost().send_message, pattern=r"write_post_group")],
    states={

        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendPost().received_message)]
    },
    fallbacks=[CallbackQueryHandler(callback=SendPost().send_post_finish,
                                    pattern=r"send_post_finish"),
               CallbackQueryHandler(callback=SendPost.help_back, pattern=r'help_back'),
               CallbackQueryHandler(callback=SendPost.help_back, pattern=r'help_module'),
               ]
)
