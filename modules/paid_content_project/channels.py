#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

from telegram.error import TelegramError
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton,
                      ReplyKeyboardMarkup)
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          MessageHandler, Filters, RegexHandler)

from database import channels_table
from helper_funcs.helper import get_help
from helper_funcs.misc import delete_messages


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO:
#       before every send check that bot admin and can send message
#       problem with delete messages - DELETE ALL MESSAGES BEFORE CURRENT
#       back to Channels menu
#       if there are only one channel don't ask to choose channel
#       Markdown support in write a post
#       When create new poll or survey -> send button is confused
#       HOW TO DELETE ALL RANDOM MESSAGES SEND BY USER
#       IF USER DELETE BOT FROM CHANNEL


MY_CHANNELS, MANAGE_CHANNEL, ADD_CHANNEL, \
    CHOOSE_TO_REMOVE, remove_paid_channel, \
    CHOOSE_TO_SEND_POST, POST_TO_CHANNEL, MESSAGE_TO_USERS = range(8)
CHOOSE_TO_SEND_POLL, CHOOSE_POLL_TO_SEND = range(2)
CHOOSE_CHANNEL_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(2)


#     CHOOSE_TO_SEND_POLL, CHOOSE_POLL_TO_SEND,\
#     CHOOSE_CHANNEL_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(12)


# check that bot is admin and can send messages to the channel
def check_channel(context, channel_username):
    try:
        admins = context.bot.get_chat_administrators(channel_username)
    except TelegramError as e:
        # print(e)
        # if bot is not admin in the channel
        if str(e).startswith("Supergroup members are unavailable"):
            return context.bot.lang_dict[
                "bot_is_not_admin_of_channel"].format(channel_username)

        elif str(e).startswith(
                "There is no administrators in the private chat"):
            return (str(e) + "\n"
                    + context.bot.lang_dict["wrong_channel_link_format"])
        # if channel link is wrong
        else:
            return context.bot.lang_dict["wrong_channel_link_format"]
    # Check that bot is able to send messages to the channel
    for admin in admins:
        # bot is admin
        if admin.user.is_bot and admin.user.id == context.bot.id:
            # bot can post messages to the channel
            if admin.can_post_messages:
                return True
            else:
                return context.bot.lang_dict["allow_bot_send_messages"]


def channel_menu(update, context):
    context.bot.delete_message(
        chat_id=update.callback_query.message.chat_id,
        message_id=update.callback_query.message.message_id)
    channels = Channels().update_channels_usernames(context,
                                                    update.effective_chat.id)
    command_list = [[InlineKeyboardButton(x['channel_username'],
                                          callback_data="paid_channel_{}".format(x['channel_username']))]
                    for x in channels] + \
                                            \
                   [[InlineKeyboardButton(context.bot.lang_dict["add_channel"], callback_data='add_channel')],
                    [InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                          callback_data="help_module(channels_groups)")]]

    no_channel_keyboard = InlineKeyboardMarkup(command_list)
    context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["channels"],
                             reply_markup=no_channel_keyboard)
    return ConversationHandler.END


# DELETING USING USER_DATA
class Channels(object):
    # ################################## HELP METHODS ########################
    # update channels usernames if channel username has benn changed.
    # call this only when at least one channel exists in db
    def update_channels_usernames(self, context, chat_id):
        for channel in channels_table.find({'bot_id': context.bot.id}):
            # check that boy is admin
            # and check that bot can send messages to channel
            check = check_channel(context, channel['channel_username'])
            if check is not True:
                context.user_data['to_delete'].append(
                    context.bot.send_message(
                        chat_id,
                        context.bot.lang_dict["bot_is_not_admin_of_channel_2"]
                        .format(channel['channel_username'])))
                channels_table.delete_one({'bot_id': context.bot.id,
                                           'chat_id': channel['chat_id']})
                continue
            # bot.get_chat() works with delay ?
            current_username = context.bot.get_chat(channel['chat_id']).username
            if channel['channel_username'] != current_username:
                channels_table.update_one({'bot_id': context.bot.id, 'channel_username': channel['channel_username']},
                                          {'$set': {'channel_username': '@{}'.format(current_username)}})
        return channels_table.find({'bot_id': context.bot.id})

    # to make keyboard with channels
    def make_channels_layout(self, update, context, state, text: str):
        no_channel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                context.bot.lang_dict["add_button"],
                callback_data='add_channel')],
            [InlineKeyboardButton(
                context.bot.lang_dict["back_button"],
                callback_data="help_module(channels_groups)")]])

        # bot.delete_message(update.effective_chat.id,
        #                    update.effective_message.message_id)
        delete_messages(update, context, True)
        if channels_table.find({'bot_id': context.bot.id}).count() == 0:
            context.user_data['to_delete'].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    context.bot.lang_dict["no_channels"],
                    reply_markup=no_channel_keyboard))
            return ConversationHandler.END
        else:
            channels = self.update_channels_usernames(
                context, update.effective_chat.id)
            command_list = [[x['channel_username']] for x in channels] + [['Back']]
            # need to delete this message
            context.user_data['to_delete'].append(
                context.bot.send_message(
                    update.effective_chat.id, text,
                    reply_markup=ReplyKeyboardMarkup(
                        command_list, one_time_keyboard=True)))
            return state

    def send_wrong_format_message(self, update, context, text: str = None):
        cancel_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["cancel_button"],
                                  callback_data='help_back')]])
        delete_messages(update, context, True)
        context.user_data['to_delete'].append(
            context.bot.send_message(update.message.chat_id,
                                     context.bot.lang_dict["wrong_channel_link_format"]
                                     if text is None else text,
                                     reply_markup=cancel_keyboard))
        return ADD_CHANNEL

    # check that channel username is correct
    def register_channel(self, update, context):
        link = update.message.text
        # VALIDATE USER MESSAGE
        if len(link.split(" ")) != 1 or len(link) > 45:
            return self.send_wrong_format_message(update, context)
        if link.startswith(("https://t.me/", "t.me/")):
            split_message = link.split('t.me/')
            if len(split_message) == 2:
                if len(split_message[1]) > 32:
                    return self.send_wrong_format_message(update, context)
                channel_username = "@{}".format(split_message[1])
            # wrong format of channel link
            else:
                return self.send_wrong_format_message(update, context)
        elif link.startswith("@"):
            channel_username = link
        else:
            channel_username = "@{}".format(link)

        check = check_channel(context, channel_username)
        if check is True:
            if not channels_table.find_one({'bot_id': context.bot.id,
                                            'channel_username': channel_username}):
                channel_chat_id = context.bot.get_chat(channel_username).id
                channels_table.insert_one({'bot_id': context.bot.id,
                                           'channel_username': channel_username,
                                           'chat_id': channel_chat_id})
                return channel_username
            else:
                return self.send_wrong_format_message(
                    update, context,
                    context.bot.lang_dict["try_to_add_already_exist_channel"])
        else:
            return self.send_wrong_format_message(update, context, check)

    ################################################################

    def channel(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        channel_username = update.callback_query.data.replace("paid_channel_", "")
        one_channel_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(context.bot.lang_dict["send_donation_to_channel"],
                                                        callback_data='send_donation_to_channel_{}'.format(
                                                            channel_username))],
                                  [InlineKeyboardButton(context.bot.lang_dict["send_survey_to_channel"],
                                                        callback_data="send_survey_to_channel_{}".format(
                                                            channel_username))],
                                  [InlineKeyboardButton(context.bot.lang_dict["send_poll_to_channel"],
                                                        callback_data="send_poll_to_channel_{}".format(
                                                            channel_username))],
                                  [InlineKeyboardButton(context.bot.lang_dict["send_post_to_channel"],
                                                        callback_data='write_post_channel_{}'.format(
                                                            channel_username))],
                                  [InlineKeyboardButton(context.bot.lang_dict["remove_button"],
                                                        callback_data='remove_channel_{}'.format(
                                                            channel_username))],
                                  [InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                                        callback_data="help_module(channels_groups)")]])
        context.bot.send_message(update.callback_query.message.chat_id, context.bot.lang_dict["channels_menu"],
                                 reply_markup=one_channel_keyboard)
        return ConversationHandler.END

    # call this when user have choose channel for remove
    def finish_remove(self, update, context):
        channel_username = update.callback_query.data.replace("remove_channel_", "")
        channel = channels_table.find_one({'bot_id': context.bot.id, 'channel_username': channel_username})
        if channel:
            delete_messages(update, context, True)
            channels_table.delete_one({'bot_id': context.bot.id, 'channel_username': channel_username})
            context.user_data['to_delete'].append(
                context.bot.send_message(update.effective_chat.id,
                                         context.bot.lang_dict["channel_has_been_removed"].format(channel_username),
                                         reply_markup=InlineKeyboardMarkup([
                                             [InlineKeyboardButton(
                                                 text=context.bot.lang_dict["back_button"],
                                                 callback_data="help_module(channels_groups)")]])))
            return ConversationHandler.END
        else:
            return self.make_channels_layout(update, context, CHOOSE_TO_REMOVE,
                                             context.bot.lang_dict["no_such_channel"]
                                             + context.bot.lang_dict["choose_channel_to_remove"])

    # 'Add Channels' button
    def add_channel(self, update, context):
        cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(context.bot.lang_dict["cancel_button"],
                                                                      callback_data='help_back')]])
        delete_messages(update, context, True)
        context.user_data['to_delete'].append(
            context.bot.send_message(update.callback_query.message.chat_id, context.bot.lang_dict["channels_str_4"],
                                     reply_markup=cancel_keyboard))
        return ADD_CHANNEL

    # call this when message with channel link arrive
    def confirm_add(self, update, context):

        channel_username = self.register_channel(update, context)
        if type(channel_username) is str:
            post_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(context.bot.lang_dict["send_post_to_channel"],
                                                                        callback_data="write_post_channel_{}".format(
                                                                            channel_username))],
                                                  [InlineKeyboardButton(context.bot.lang_dict["send_poll_to_channel"],
                                                                        callback_data="send_poll_to_channel_{}".format(
                                                                            channel_username))],
                                                  [InlineKeyboardButton(context.bot.lang_dict["send_survey_to_channel"],
                                                                        callback_data="send_survey_to_channel_{}"
                                                                        .format(channel_username))],
                                                  [InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                                                        callback_data="help_module(channels_groups)")]])
            delete_messages(update, context, True)
            context.user_data['to_delete'].append(
                context.bot.send_message(update.message.chat_id,
                                         context.bot.lang_dict["channel_added_success"].format(update.message.text),
                                         reply_markup=post_keyboard))
            return ConversationHandler.END
        else:
            return ADD_CHANNEL

    @staticmethod
    def error(update, context, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)
        # need to return ConversationHandler.END here?

    def back(self, update, context):
        delete_messages(update, context, True)
        get_help(update, context)
        return ConversationHandler.END



CHANELLS_MENU = CallbackQueryHandler(callback=channel_menu, pattern=r"channels")
MY_CHANNELS_HANDLER = CallbackQueryHandler(callback=Channels().channel, pattern=r"channel")

# MY_CHANNELS_HANDLER = ConversationHandler(
#     entry_points=[CallbackQueryHandler(callback=Channels().my_channels, pattern=r"my_channels")],
#     states={
#         MY_CHANNELS: [MessageHandler(Filters.regex(r"@"), Channels().channel)]
#     },
#     fallbacks=[CallbackQueryHandler(callback=Channels().back, pattern=r"help_back"),
#                CallbackQueryHandler(callback=Channels().back, pattern=r'help_module'),
#                MessageHandler(Filters.regex('^Back$'), Channels().back),
#                ]
# )


ADD_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().add_channel, pattern=r"add_channel")],
    states={
        ADD_CHANNEL: [MessageHandler(Filters.text, callback=Channels().confirm_add)]
    },
    fallbacks=[CallbackQueryHandler(callback=Channels().back, pattern=r'help_back'),
               CallbackQueryHandler(callback=Channels().back, pattern=r'help_module'),

               ]
)

REMOVE_CHANNEL_HANDLER = CallbackQueryHandler(Channels().finish_remove,
                                              pattern=r"remove_paid_channel")
