#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, Chat, ChatMember
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler
from database import groups_table
from telegram.error import TelegramError
from helper_funcs.helper import get_help

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

# database schema
group_table_scheme = {
    'bot_id': int,
    'group_name': str,
    'chat_id': int
}

MY_GROUPS, MANAGE_GROUP, ADD_GROUP, \
CHOOSE_TO_REMOVE, REMOVE_GROUP, \
CHOOSE_TO_SEND_POST, POST_TO_GROUP, MESSAGE_TO_USERS = range(8)
CHOOSE_TO_SEND_POLL, CHOOSE_POLL_TO_SEND = range(2)
CHOOSE_GROUP_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(2)


#     CHOOSE_TO_SEND_POLL, CHOOSE_POLL_TO_SEND,\
#     CHOOSE_GROUP_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(12)


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
                                          callback_data="paid_group_{}".format(x['group_id']))]
                    for x in groups] + \
                   [[InlineKeyboardButton(context.bot.lang_dict["add_group"], callback_data='add_group')],
                    [InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                          callback_data="help_module(channels_groups)")]]
    context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["groups"],
                             reply_markup=InlineKeyboardMarkup(command_list))
    return ConversationHandler.END


# DELETING USING USER_DATA
class Groups():
    # ################################## HELP METHODS ###########################################################

    def group(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        group_id = update.callback_query.data.replace("paid_group_", "")
        one_group_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(context.bot.lang_dict["send_donation_to_group"],
                                                        callback_data='send_donation_to_group_{}'.format(group_id
                                                                                                         ))],
                                  [InlineKeyboardButton(context.bot.lang_dict["send_survey_to_group"],
                                                        callback_data="send_survey_to_group_{}".format(
                                                            group_id))],
                                  [InlineKeyboardButton(context.bot.lang_dict["send_poll_to_group"],
                                                        callback_data="send_poll_to_group_{}".format(
                                                            group_id))],
                                  [InlineKeyboardButton(context.bot.lang_dict["send_post_to_group"],
                                                        callback_data='write_post_group_{}'.format(
                                                            group_id))],
                                  [InlineKeyboardButton(context.bot.lang_dict["remove_button"],
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

    @staticmethod
    def error(update, context, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)
        # need to return ConversationHandler.END here?

    def back(self, update, context):
        delete_messages(update, context)
        get_help(update, context)
        return ConversationHandler.END


class AddGroup():
    def add_group(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(channels_groups)")]
        )
        reply_markup = InlineKeyboardMarkup(
            buttons)

        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["add_group_str"],
                                 reply_markup=reply_markup)
        return ConversationHandler.END


# chat.kick_member(user_id)
class MembersManagement():
    def is_user_ban_protected(self, chat: Chat, user_id: int, member: ChatMember = None) -> bool:
        if chat.type == 'private' or chat.all_members_are_administrators:
            return True

        if not member:
            member = chat.get_member(user_id)

        return member.status in ('administrator', 'creator')

ADD_GROUP_HANLDER = CallbackQueryHandler(callback=AddGroup().add_group, pattern="add_group")

GROUPS_MENU = CallbackQueryHandler(callback=groups_menu, pattern="groups")
MY_GROUPS_HANDLER = CallbackQueryHandler(callback=Groups().group, pattern=r"group")

REMOVE_GROUP_HANDLER = CallbackQueryHandler(Groups().finish_remove,
                                            pattern=r"remove_group")



