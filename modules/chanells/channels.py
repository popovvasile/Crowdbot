#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler
from database import channels_table
from telegram.error import TelegramError
from helper_funcs.helper import get_help
from helper_funcs.lang_strings.strings import string_dict
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
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

# database schema
channel_table_scheme = {
    'bot_id': int,
    'channel_name': str,
    'chat_id': int
}

MY_CHANNELS, MANAGE_CHANNEL, ADD_CHANNEL, \
CHOOSE_TO_REMOVE, REMOVE_CHANNEL, \
CHOOSE_TO_SEND_POST, POST_TO_CHANNEL, MESSAGE_TO_USERS = range(8)
CHOOSE_TO_SEND_POLL, CHOOSE_POLL_TO_SEND = range(2)
CHOOSE_CHANNEL_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(2)


#     CHOOSE_TO_SEND_POLL, CHOOSE_POLL_TO_SEND,\
#     CHOOSE_CHANNEL_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(12)


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


# check that bot is admin and can send messages to the channel
def check_channel(context, channel_username):
    try:
        admins = context.bot.get_chat_administrators(channel_username)
    except TelegramError as e:
        # print(e)
        # if bot is not admin in the channel
        if str(e).startswith("Supergroup members are unavailable"):
            return string_dict(context)["bot_is_not_admin_of_channel"].format(channel_username)
        elif str(e).startswith("There is no administrators in the private chat"):
            return str(e) + "\n" + string_dict(context)["wrong_channel_link_format"]
        # if channel link is wrong
        else:
            return string_dict(context)["wrong_channel_link_format"]
    # Check that bot is able to send messages to the channel
    for admin in admins:
        # bot is admin
        if admin.user.is_bot and admin.user.id == context.bot.id:
            # bot can post messages to the channel
            if admin.can_post_messages:
                return True
            else:
                return string_dict(context)["allow_bot_send_messages"]


def channel_menu(update, context):
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    no_channel_keyboard = InlineKeyboardMarkup(
    [[InlineKeyboardButton(string_dict(context)["my_channels"], callback_data='my_channels')],
         [InlineKeyboardButton(string_dict(context)["add_channel"], callback_data='add_channel')],
        [InlineKeyboardButton(string_dict(context)["back_button"],
                              callback_data="help_module(channels)")]]
            )
    context.bot.send_message(update.callback_query.message.chat.id,
                     string_dict(context)["channels"], reply_markup=no_channel_keyboard)
    return ConversationHandler.END


# DELETING USING USER_DATA
class Channels(object):
    # ################################## HELP METHODS ###########################################################
    # update channels usernames if channel username has benn changed.
    # call this only when at least one channel exists in db
    def update_channels_usernames(self, context, chat_id):
        for channel in channels_table.find({'bot_id': context.bot.id}):
            # check that boy is admin
            # and check that bot can send messages to channel
            check = check_channel(context, channel['channel_username'])
            if check is not True:
                context.user_data['to_delete'].append(
                    context.bot.send_message(chat_id,
                                     string_dict(context)["bot_is_not_admin_of_channel_2"]
                                     .format(channel['channel_username'])))
                channels_table.delete_one({'bot_id': context.bot.id, 'chat_id': channel['chat_id']})
                continue
            # bot.get_chat() works with delay ?
            current_username = context.bot.get_chat(channel['chat_id']).username
            if channel['channel_username'] != current_username:
                channels_table.update_one({'bot_id': context.bot.id, 'channel_username': channel['channel_username']},
                                          {'$set': {'channel_username': '@{}'.format(current_username)}})
        return channels_table.find({'bot_id': context.bot.id})

    # to make keyboard with channels
    def make_channels_layout(self, update, context, state, text: str):
        no_channel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(context)["add_button"],
                                                                          callback_data='add_channel')],
                                                    [InlineKeyboardButton(string_dict(context)["back_button"],
                                                                          callback_data="help_module(channels)")]])

        # bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
        delete_messages(update, context)
        if channels_table.find({'bot_id': context.bot.id}).count() == 0:
            context.user_data['to_delete'].append(
                context.bot.send_message(
                    update.effective_chat.id, string_dict(context)["no_channels"],
                    reply_markup=no_channel_keyboard))
            return ConversationHandler.END
        else:
            channels = self.update_channels_usernames(context, update.effective_chat.id)
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
            [InlineKeyboardButton(string_dict(context)["cancel_button"],
                                  callback_data='help_back')]])
        delete_messages(update, context)
        context.user_data['to_delete'].append(
            context.bot.send_message(update.message.chat_id,
                                     string_dict(context)["wrong_channel_link_format"]
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
                    string_dict(context)["try_to_add_already_exist_channel"])
        else:
            return self.send_wrong_format_message(update, context, check)

    ################################################################

    # 'My Channels' button
    def my_channels(self, update, context):
        return self.make_channels_layout(update, context, MY_CHANNELS, string_dict(context)["channels_str_2"])

    # when user click on channel name in 'My channels' menu
    def channel(self, update, context):
        one_channel_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(context)["send_donation_to_channel"],
                                                        callback_data='send_donation_to_channel_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(context)["send_survey_to_channel"],
                                                        callback_data="send_survey_to_channel_{}".format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(context)["send_poll_to_channel"],
                                                        callback_data="send_poll_to_channel_{}".format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(context)["send_post_to_channel"],
                                                        callback_data='channel_write_post_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(context)["remove_button"],
                                                        callback_data='remove_channel_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(context)["back_button"],
                                                        callback_data="help_module(channels)")]])
        context.bot.send_message(update.message.chat_id, string_dict(context)["channels_menu"],
                                 reply_markup=one_channel_keyboard)
        return ConversationHandler.END

    # call this when user have choose channel for remove
    def finish_remove(self, update, context):
        channel_username = update.callback_query.data.replace("remove_channel_", "")
        channel = channels_table.find_one({'bot_id': context.bot.id, 'channel_username': channel_username})
        if channel:
            delete_messages(update, context)
            channels_table.delete_one({'bot_id': context.bot.id, 'channel_username': channel_username})
            context.user_data['to_delete'].append(
                context.bot.send_message(update.effective_chat.id, string_dict(context)["channel_has_been_removed"]
                                 .format(channel_username),
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                     text=string_dict(context)["back_button"],
                                     callback_data="help_module(channels)")]])
                                 ))
            return ConversationHandler.END
        else:
            return self.make_channels_layout(update, context, CHOOSE_TO_REMOVE,
                                             string_dict(context)["no_such_channel"]
                                             + string_dict(context)["choose_channel_to_remove"])

    # 'Add Channels' button
    def add_channel(self, update, context):
        cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(context)["cancel_button"],
                                                                      callback_data='help_back')]])
        delete_messages(update, context)
        context.user_data['to_delete'].append(
            context.bot.send_message(update.callback_query.message.chat_id, string_dict(context)["channels_str_4"],
                             reply_markup=cancel_keyboard))
        return ADD_CHANNEL

    # call this when message with channel link arrive
    def confirm_add(self, update, context):

        channel_username = self.register_channel(update, context)
        if type(channel_username) is str:
            post_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(context)["send_post_to_channel"],
                                                                        callback_data="channel_write_post_{}".format(
                                                                            channel_username))],
                                                  [InlineKeyboardButton(string_dict(context)["send_poll_to_channel"],
                                                                        callback_data="send_poll_to_channel_{}".format(
                                                                            channel_username))],
                                                  [InlineKeyboardButton(string_dict(context)["send_survey_to_channel"],
                                                                        callback_data="send_survey_to_channel_{}".format(
                                                                            channel_username))],
                                                  [InlineKeyboardButton(string_dict(context)["back_button"],
                                                                        callback_data="help_module(channels)")]])
            delete_messages(update, context)
            context.user_data['to_delete'].append(
                context.bot.send_message(update.message.chat_id, string_dict(context)["channel_added_success"]
                                 .format(update.message.text),
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
        delete_messages(update, context)
        get_help(update, context)
        return ConversationHandler.END


class SendPost(object):
    def send_message(self, update, context):
        # bot.delete_message(chat_id=update.callback_query.message.chat_id,
        #                    message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(context)["back_button"], callback_data="help_back")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        channel_username = update.callback_query.data.replace("channel_write_post", "")
        channel = channels_table.find_one({'bot_id': context.bot.id,
                                           'channel_username': channel_username})
        print(update.callback_query.data)
        # if channel:
        delete_messages(update, context)
        print()
        context.user_data['channel'] = update.callback_query.data.replace("channel_write_post_", "")
        context.user_data['to_delete'].append(
            context.bot.send_message(update.callback_query.message.chat.id,
                             string_dict(context)["send_post"].format(channel_username),
                             reply_markup=reply_markup))
        return MESSAGE_TO_USERS
        # else:
        #     return Channels().make_channels_layout(update, context, CHOOSE_TO_SEND_POST,
        #                                            string_dict(bot)["choose_channel_to_post"], user_data)

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
            [[InlineKeyboardButton(text=string_dict(context)["done_button"], callback_data="send_post_finish")],
             [InlineKeyboardButton(text="Cancel", callback_data="help_back")]]
        )
        context.user_data['to_delete'].append(
            context.bot.send_message(update.message.chat_id,
                             string_dict(context)["send_message_4"],
                             reply_markup=final_reply_markup))
        return MESSAGE_TO_USERS

    def send_post_finish(self, update, context):
        for content_dict in context.user_data["content"]:
            if "text" in content_dict:
                context.bot.send_message(context.user_data['channel'],
                                 content_dict["text"])
            if "audio_file" in content_dict:
                context.bot.send_audio(context.user_data['channel'], content_dict["audio_file"])
            if "video_file" in content_dict:
                context.bot.send_video(context.user_data['channel'], content_dict["video_file"])
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    context.bot.send_photo(context.user_data['channel'], content_dict["document_file"])
                else:
                    context.bot.send_document(context.user_data['channel'], content_dict["document_file"])
            if "photo_file" in content_dict:
                context.bot.send_photo(context.user_data['channel'], content_dict["photo_file"])

        delete_messages(update, context)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(context)["back_button"],
                                             callback_data="help_module(channels)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.user_data['to_delete'].append(
            context.bot.send_message(update.callback_query.message.chat_id,
                             string_dict(context)["send_message_5"],
                             reply_markup=final_reply_markup))
        logger.info("Admin {} on bot {}:{} sent a post to the channel".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id))
        context.user_data.clear()
        return ConversationHandler.END

    def help_back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(context)["back_button"],
                                             callback_data="help_module(channels)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.send_message(update.callback_query.message.chat_id,
                         string_dict(context)["send_message_9"],
                         reply_markup=final_reply_markup)
        context.user_data.clear()
        return ConversationHandler.END

    def error(self, update, context, error):
        """Log Errors caused by Updates."""
        context.bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
        return ConversationHandler.END

    def back(self, update, context):
        delete_messages(update, context)
        get_help(update, context)
        return ConversationHandler.END

CHANELLS_MENU = CallbackQueryHandler(callback=channel_menu, pattern=r"channels")

MY_CHANNELS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().my_channels, pattern=r"my_channels", pass_user_data=True)],
    states={
        MY_CHANNELS: [RegexHandler(r"@", Channels().channel)]
    },
    fallbacks=[CallbackQueryHandler(callback=Channels().back, pattern=r"help_back", pass_user_data=True),
               CallbackQueryHandler(callback=Channels().back, pattern=r'help_module', pass_user_data=True),
               RegexHandler('^Back$', Channels().back, pass_user_data=True),
               ]
)

ADD_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().add_channel, pattern=r"add_channel", pass_user_data=True)],
    states={
        ADD_CHANNEL: [MessageHandler(Filters.text, callback=Channels().confirm_add, pass_user_data=True)]
    },
    fallbacks=[CallbackQueryHandler(callback=Channels().back, pattern=r'help_back', pass_user_data=True),
               CallbackQueryHandler(callback=Channels().back, pattern=r'help_module', pass_user_data=True),

               ]
)

REMOVE_CHANNEL_HANDLER = CallbackQueryHandler(Channels().finish_remove,
                                              pattern=r"remove_channel", pass_user_data=True)
# POST_ON_CHANNEL_HANDLER = CallbackQueryHandler(Channels().post_on_channel,
#                                                pattern=r"post_on_channel", pass_user_data=True)

SEND_POST_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendPost().send_message, pattern=r"channel_write_post", pass_user_data=True)],
    states={

        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendPost().received_message, pass_user_data=True)]
    },
    fallbacks=[CallbackQueryHandler(callback=SendPost().send_post_finish,
                                    pattern=r"send_post_finish", pass_user_data=True),
               CallbackQueryHandler(callback=SendPost.help_back, pattern=r'help_back', pass_user_data=True),
               CallbackQueryHandler(callback=SendPost.help_back, pattern=r'help_module', pass_user_data=True),
               ]
)
