#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler, run_async
from database import channels_table
from telegram.error import TelegramError
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict
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


def delete_messages(bot, user_data, update):
    try:
        bot.delete_message(update.effective_message.chat.id, update.effective_message.message_id)

        if 'to_delete' in user_data:
            for msg in user_data['to_delete']:
                try:
                    if msg.message_id != update.effective_message.message_id:
                        bot.delete_message(update.effective_message.chat.id, msg.message_id)
                except TelegramError:
                    # print('except in delete_message---> {}, {}'.format(e, msg_id))
                    continue
            user_data['to_delete'] = list()
        else:
            user_data['to_delete'] = list()
    except:
        pass


# check that bot is admin and can send messages to the channel
def check_channel(bot, channel_username):
    try:
        admins = bot.get_chat_administrators(channel_username)
    except TelegramError as e:
        # print(e)
        # if bot is not admin in the channel
        if str(e).startswith("Supergroup members are unavailable"):
            return string_dict(bot)["bot_is_not_admin_of_channel"].format(channel_username)
        elif str(e).startswith("There is no administrators in the private chat"):
            return str(e) + "\n" + string_dict(bot)["wrong_channel_link_format"]
        # if channel link is wrong
        else:
            return string_dict(bot)["wrong_channel_link_format"]
    # Check that bot is able to send messages to the channel
    for admin in admins:
        # bot is admin
        if admin.user.is_bot and admin.user.id == bot.id:
            # bot can post messages to the channel
            if admin.can_post_messages:
                return True
            else:
                return string_dict(bot)["allow_bot_send_messages"]


# DELETING USING USER_DATA
class Channels(object):
    # ################################## HELP METHODS ###########################################################
    # update channels usernames if channel username has benn changed.
    # call this only when at least one channel exists in db
    def update_channels_usernames(self, bot, user_data, chat_id):
        for channel in channels_table.find({'bot_id': bot.id}):
            # check that boy is admin
            # and check that bot can send messages to channel
            check = check_channel(bot, channel['channel_username'])
            if check is not True:
                user_data['to_delete'].append(
                    bot.send_message(chat_id,
                                     string_dict(bot)["bot_is_not_admin_of_channel_2"]
                                     .format(channel['channel_username'])))
                channels_table.delete_one({'bot_id': bot.id, 'chat_id': channel['chat_id']})
                continue
            # bot.get_chat() works with delay ?
            current_username = bot.get_chat(channel['chat_id']).username
            if channel['channel_username'] != current_username:
                channels_table.update_one({'bot_id': bot.id, 'channel_username': channel['channel_username']},
                                          {'$set': {'channel_username': '@{}'.format(current_username)}})
        return channels_table.find({'bot_id': bot.id})

    # to make keyboard with channels
    def make_channels_layout(self, bot, update, state, text: str, user_data):
        no_channel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["add_button"],
                                                                          callback_data='add_channel')],
                                                    [InlineKeyboardButton(string_dict(bot)["back_button"],
                                                                          callback_data='help_back')]])

        # bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
        delete_messages(bot, user_data, update)
        if channels_table.find({'bot_id': bot.id}).count() == 0:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, string_dict(bot)["no_channels"],
                                 reply_markup=no_channel_keyboard))
            return ConversationHandler.END
        else:
            channels = self.update_channels_usernames(bot, user_data, update.effective_chat.id)
            command_list = [[x['channel_username']] for x in channels] + [['Back']]
            # need to delete this message
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, text,
                                 reply_markup=ReplyKeyboardMarkup(command_list, one_time_keyboard=True)))
            return state

    def send_wrong_format_message(self, bot, update, user_data, text: str = None):
        cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["cancel_button"],
                                                                      callback_data='cancel_add')]])
        delete_messages(bot, user_data, update)
        user_data['to_delete'].append(
            bot.send_message(update.message.chat_id, string_dict(bot)["wrong_channel_link_format"]
            if text is None else text,
                             reply_markup=cancel_keyboard))
        return ADD_CHANNEL

    # check that channel username is correct
    def register_channel(self, bot, update, user_data):
        link = update.message.text
        # VALIDATE USER MESSAGE
        if len(link.split(" ")) != 1 or len(link) > 45:
            return self.send_wrong_format_message(bot, update, user_data)
        if link.startswith(("https://t.me/", "t.me/")):
            split_message = link.split('t.me/')
            if len(split_message) == 2:
                if len(split_message[1]) > 32:
                    return self.send_wrong_format_message(bot, update, user_data)
                channel_username = "@{}".format(split_message[1])
            # wrong format of channel link
            else:
                return self.send_wrong_format_message(bot, update, user_data)
        elif link.startswith("@"):
            channel_username = link
        else:
            channel_username = "@{}".format(link)

        check = check_channel(bot, channel_username)
        if check is True:
            if not channels_table.find_one({'bot_id': bot.id, 'channel_username': channel_username}):
                channel_chat_id = bot.get_chat(channel_username).id
                channels_table.insert_one({'bot_id': bot.id,
                                           'channel_username': channel_username,
                                           'chat_id': channel_chat_id})
                return True
            else:
                return self.send_wrong_format_message(bot, update, user_data,
                                                      string_dict(bot)["try_to_add_already_exist_channel"])
        else:
            return self.send_wrong_format_message(bot, update, user_data, check)

    ################################################################

    # 'My Channels' button
    def my_channels(self, bot, update, user_data):
        return self.make_channels_layout(bot, update, MY_CHANNELS, string_dict(bot)["channels_str_2"],
                                         user_data)

    # when user click on channel name in 'My channels' menu
    def channel(self, bot, update):
        one_channel_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["send_donation_to_channel"],
                                                        callback_data='send_donation_to_channel_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["send_survey_to_channel"],
                                                        callback_data="post_survey_to_channel_{}".format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["send_poll_to_channel"],
                                                        callback_data="post_poll_to_channel_{}".format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["send_post_to_channel"],
                                                        callback_data='channel_write_post_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["remove_button"],
                                                        callback_data='remove_channel_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["back_button"],
                                                        callback_data='help_back')]])
        bot.send_message(update.message.chat_id, string_dict(bot)["channels_menu"],
                         reply_markup=one_channel_keyboard)
        return ConversationHandler.END

    # call this when user have choose channel for remove
    def finish_remove(self, bot, update, user_data):
        channel_username = update.callback_query.data.replace("remove_channel_", "")
        channel = channels_table.find_one({'bot_id': bot.id, 'channel_username': channel_username})
        if channel:
            delete_messages(bot, user_data, update)
            channels_table.delete_one({'bot_id': bot.id, 'channel_username': channel_username})
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, string_dict(bot)["channel_has_been_removed"]
                                 .format(channel_username),
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                     text=string_dict(bot)["back_button"],
                                     callback_data="help_back")]])
                                 ))
            return ConversationHandler.END
        else:
            return self.make_channels_layout(bot, update, CHOOSE_TO_REMOVE,
                                             string_dict(bot)["no_such_channel"]
                                             + string_dict(bot)["choose_channel_to_remove"], user_data)

    # 'Add Channels' button
    def add_channel(self, bot, update, user_data):
        cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["cancel_button"],
                                                                      callback_data='cancel_add')]])
        delete_messages(bot, user_data, update)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id, string_dict(bot)["channels_str_4"],
                             reply_markup=cancel_keyboard))
        return ADD_CHANNEL

    # call this when message with channel link arrive
    def confirm_add(self, bot, update, user_data):
        post_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["send_post_to_channel"],
                                                                    callback_data="channel_write_post_{}".format(
                                                                        update.message.text))],
                                              [InlineKeyboardButton(string_dict(bot)["send_poll_to_channel"],
                                                                    callback_data="post_poll_to_channel_{}".format(
                                                                        update.message.text))],
                                              [InlineKeyboardButton(string_dict(bot)["send_survey_to_channel"],
                                                                    callback_data="post_survey_{}".format(
                                                                        update.message.text))],
                                              [InlineKeyboardButton(string_dict(bot)["back_button"],
                                                                    callback_data='help_back')]])
        have_added = self.register_channel(bot, update, user_data)
        if have_added is True:
            delete_messages(bot, user_data, update)
            user_data['to_delete'].append(
                bot.send_message(update.message.chat_id, string_dict(bot)["channel_added_success"]
                                 .format(update.message.text),
                                 reply_markup=post_keyboard))
            return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)
        # need to return ConversationHandler.END here?

    def back(self, bot, update, user_data):
        delete_messages(bot, user_data, update)
        get_help(bot, update)
        return ConversationHandler.END


class SendPost(object):
    def send_message(self, bot, update, user_data):
        # bot.delete_message(chat_id=update.callback_query.message.chat_id,
        #                    message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="cancel_send_post")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        channel_username = update.callback_query.data.replace("channel_write_post", "")
        channel = channels_table.find_one({'bot_id': bot.id,
                                           'channel_username': channel_username})
        print(update.callback_query.data)
        # if channel:
        delete_messages(bot, user_data, update)
        user_data['channel'] = update.callback_query.data.replace("channel_write_post_", "")
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["send_post"].format(channel_username),
                             reply_markup=reply_markup))
        return MESSAGE_TO_USERS
        # else:
        #     return Channels().make_channels_layout(bot, update, CHOOSE_TO_SEND_POST,
        #                                            string_dict(bot)["choose_channel_to_post"], user_data)

    def received_message(self, bot, update, user_data):
        if update.message.text:
            bot.send_message(user_data['channel'], update.message.text)

        elif update.message.photo:
            photo_file = update.message.photo[0].get_file().file_id
            bot.send_photo(chat_id=user_data['channel'], photo=photo_file)

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            bot.send_audio(user_data['channel'], audio_file)

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            bot.send_voice(user_data['channel'], voice_file)

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            bot.send_document(user_data['channel'], document_file)

        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            bot.send_sticker(user_data['channel'], sticker_file)

        elif update.message.game:
            sticker_file = update.message.game.get_file().file_id
            bot.send_game(user_data['channel'], sticker_file)

        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            bot.send_animation(user_data['channel'], animation_file)

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            bot.send_video(user_data['channel'], video_file)

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            bot.send_video_note(user_data['channel'], video_note_file)

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=string_dict(bot)["done_button"], callback_data="send_post_finish")]]
        )
        user_data['to_delete'].append(
            bot.send_message(update.message.chat_id,
                             string_dict(bot)["send_message_4"],
                             reply_markup=final_reply_markup))
        return MESSAGE_TO_USERS

    def send_post_finish(self, bot, update, user_data):
        delete_messages(bot, user_data, update)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_5"],
                             reply_markup=final_reply_markup))
        logger.info("Admin {} on bot {}:{} sent a post to the channel".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        delete_messages(bot, user_data, update)
        get_help(bot, update)
        return ConversationHandler.END


MY_CHANNELS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().my_channels, pattern=r"my_channels", pass_user_data=True)],
    states={
        MY_CHANNELS: [RegexHandler(r"@", Channels().channel)]
    },
    fallbacks=[CallbackQueryHandler(callback=Channels().back, pattern=r"cancel_my_channels", pass_user_data=True),
               RegexHandler('^Back$', Channels().back, pass_user_data=True),
               CallbackQueryHandler(callback=SendPost().back, pattern=r"error_back"),
               ]
)

ADD_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().add_channel, pattern=r"add_channel", pass_user_data=True)],
    states={
        ADD_CHANNEL: [MessageHandler(Filters.text, callback=Channels().confirm_add, pass_user_data=True)]
    },
    fallbacks=[CallbackQueryHandler(callback=Channels().back, pattern=r'cancel_add', pass_user_data=True),
               CallbackQueryHandler(callback=SendPost().back, pattern=r"error_back"),
               ]
)

REMOVE_CHANNEL_HANDLER = CallbackQueryHandler(Channels().finish_remove,
                                              pattern=r"remove_channel", pass_user_data=True)
# POST_ON_CHANNEL_HANDLER = CallbackQueryHandler(Channels().post_on_channel,
#                                                pattern=r"post_on_channel", pass_user_data=True)

SEND_POST_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendPost().send_message, pattern=r"channel_write_post", pass_user_data=True)],
    states={

        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendPost().received_message, pass_user_data=True),
                           CallbackQueryHandler(callback=SendPost().back, pattern=r"cancel_send_post",
                                                pass_user_data=True)]
    },
    fallbacks=[CallbackQueryHandler(callback=SendPost().send_post_finish,
                                    pattern=r"send_post_finish", pass_user_data=True),
               CallbackQueryHandler(callback=SendPost().back, pattern=r"error_back"),
               ]
)
