#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler, run_async
from database import channels_table, polls_table, surveys_table
from telegram.error import TelegramError
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict

# from modules.helper_funcs.auth import initiate_chat_id
# from modules.polls import PollBot

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

channels_str_1 = 'Here u can manage your channels'
channels_str_2 = 'List of your channels'
# Click "Add" to configure your first channel or "Back" for main menu
no_channels = 'You have no channel configured yet. Click "Add channel" to configure your first channel'
wrong_channel_link_format = 'Send me link or username of your channel. ' \
                            'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"'
bot_is_not_admin_of_channel = 'Bot is not admin in this({}) channel. ' \
                              'Add bot as admin to the channel and then back to this menu ' \
                              'and send me link or username of your channel. ' \
                              'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"'
bot_is_not_admin_of_channel_2 = "Bot is not admin in this({}) channel or can't send message to the channel" \
                                "So channel was deleted. Add bot as admin to the channel, " \
                                "let it send message to the channel " \
                                "and then add channel again by Clicking 'Add channel'"
channels_str_4 = "To add channel u need to add this bot as admin to your channel " \
                 "and then back to this menu and send " \
                 "link or username of your channel. " \
                 "Send me link or username of your channel"
allow_bot_send_messages = 'U need to allow bot send messages to the channel. ' \
                          'And than back to this menu and send username of channel'
no_such_channel = 'There are no such channel. '
choose_channel_to_remove = 'Choose channel you want to remove'
channel_has_been_removed = 'Channel({}) has been deleted.'
channel_added_success = 'Now you can send posts to the channel({}) using this commands.'
choose_channel_to_post = 'Choose channel u want to post'
post_message = 'What do u want to do?'
send_post = "What do you want to post on your channel({})?\n"\
            "We will forward your message to channel."
choose_channel_to_send_poll = 'Choose channel u want to send poll'
choose_channel_to_send_survey = 'Choose channel u want to send survey'
try_to_add_already_exist_channel = 'This channel already exists'  # You can Post on channel

__mod_name__ = 'Channels'
# start 'Channels' message
__admin_help__ = channels_str_1
# and keyboard for start message
__admin_keyboard__ = [InlineKeyboardButton('My Channels', callback_data='my_channels'),
                      InlineKeyboardButton('Add channel', callback_data='add_channel'),
                      InlineKeyboardButton('Remove channel', callback_data='remove_channel'),
                      InlineKeyboardButton('Post on channel', callback_data='post_on_channel')]

# TODO: When we need to use @run_async decorator?
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

#     CHOOSE_TO_SEND_POLL, CHOOSE_POLL_TO_SEND,\
#     CHOOSE_CHANNEL_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(12)


def delete_messages(bot, user_data, update):
    # print(update.effective_message.message_id)
    # if update.callback_query:
    #     print(update.callback_query.data)
    # else:
    #     print(update.message.text)
    bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
    if 'to_delete' in user_data:
        for msg in user_data['to_delete']:
            try:
                if msg.message_id != update.effective_message.message_id:
                    bot.delete_message(update.effective_chat.id, msg.message_id)
            except TelegramError:
                # print('except in delete_message---> {}, {}'.format(e, msg_id))
                continue
        user_data['to_delete'] = list()
    else:
        user_data['to_delete'] = list()


# check that bot is admin and can send messages to the channel
def check_channel(bot, channel_username):
    try:
        admins = bot.get_chat_administrators(channel_username)
    except TelegramError as e:
        # print(e)
        # if bot is not admin in the channel
        if str(e).startswith("Supergroup members are unavailable"):
            return bot_is_not_admin_of_channel.format(channel_username)
        elif str(e).startswith("There is no administrators in the private chat"):
            return str(e) + "\n" + wrong_channel_link_format
        # if channel link is wrong
        else:
            return wrong_channel_link_format
    # Check that bot is able to send messages to the channel
    for admin in admins:
        # bot is admin
        if admin.user.is_bot and admin.user.id == bot.id:
            # bot can post messages to the channel
            if admin.can_post_messages:
                return True
            else:
                return allow_bot_send_messages


# DELETING USING USER_DATA
class Channels(object):
    def __init__(self):
        self.post_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Write a post', callback_data='write_post')],
                                                   [InlineKeyboardButton("Send a poll",
                                                                         callback_data='post_poll_to_channel')],
                                                   [InlineKeyboardButton("Send a survey", callback_data='post_survey')],
                                                   [InlineKeyboardButton('Back', callback_data='help_back')]])
        self.no_channel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Add", callback_data='add_channel')],
                                                         [InlineKeyboardButton('Back', callback_data='help_back')]])
        self.cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('Cancel', callback_data='cancel_add')]])
        self.one_channel_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton('Remove', callback_data='channel_remove')],
                                  [InlineKeyboardButton('Send a poll', callback_data='PASS'),
                                   InlineKeyboardButton('Send a survey', callback_data='PASS')],
                                  [InlineKeyboardButton('Write a post', callback_data='channel_write_post')],
                                  [InlineKeyboardButton('Back', callback_data='back')]])

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
                                     bot_is_not_admin_of_channel_2.format(channel['channel_username'])))
                channels_table.delete_one({'bot_id': bot.id, 'chat_id': channel['chat_id']})
                continue
            # bot.get_chat() works with delay ?
            current_username = bot.get_chat(channel['chat_id']).username
            if channel['channel_username'] != current_username:
                channels_table.update_one({'bot_id': bot.id, 'channel_username': channel['channel_username']},
                                          {'$set': {'channel_username': '@{}'.format(current_username)}})
        return channels_table.find({'bot_id': bot.id})

    # Copy from main_runner_helper -> def help_button. when click back button -> return to channels menu
    def make_main_keyboard(self):
        pairs = list(zip(__admin_keyboard__[::2], __admin_keyboard__[1::2]))
        if len(__admin_keyboard__) % 2 == 1:
            pairs.append((__admin_keyboard__[-1],))
        pairs.append(
            [InlineKeyboardButton(text="Back", callback_data="help_back")]
        )
        return InlineKeyboardMarkup(pairs)

    # to make keyboard with channels
    def make_channels_layout(self, bot, update, state, text: str, user_data):
        # bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
        delete_messages(bot, user_data, update)
        if channels_table.find({'bot_id': bot.id}).count() == 0:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, no_channels,
                                 reply_markup=self.no_channel_keyboard))
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
        delete_messages(bot, user_data, update)
        user_data['to_delete'].append(
            bot.send_message(update.message.chat_id, wrong_channel_link_format if text is None else text,
                             reply_markup=self.cancel_keyboard))
        return ADD_CHANNEL

    # check that channel username is correct
    def register_channel(self, bot,  update, user_data):
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
                return self.send_wrong_format_message(bot, update, user_data, try_to_add_already_exist_channel)
        else:
            return self.send_wrong_format_message(bot, update, user_data, check)
################################################################

    # 'My Channels' button
    def my_channels(self, bot, update, user_data):
        return self.make_channels_layout(bot, update, MY_CHANNELS, channels_str_2, user_data)

    # when user click on channel name in 'My channels' menu
    def channel(self, bot, update, user_data):
        delete_messages(bot, user_data, update)
        channel = channels_table.find_one({'bot_id': bot.id, 'channel_username': update.message.text})
        if channel:
            user_data['channel'] = channel['channel_username']
            user_data['to_delete'].append(
                bot.send_message(update.message.chat_id, channel['channel_username'],
                                 reply_markup=self.one_channel_keyboard))
            return MANAGE_CHANNEL
        else:
            return self.make_channels_layout(bot, update, MY_CHANNELS, channels_str_2, user_data)

    # 'Remove channel' button
    def choose_to_remove(self, bot, update, user_data):
        return self.make_channels_layout(bot, update, CHOOSE_TO_REMOVE, choose_channel_to_remove, user_data)

    # call this when user have choose channel for remove
    def finish_remove(self, bot, update, user_data):
        delete_messages(bot, user_data, update)
        channel_username = user_data['channel'] if update.callback_query else update.message.text
        channel = channels_table.find_one({'bot_id': bot.id, 'channel_username': channel_username})
        if channel:
            channels_table.delete_one({'bot_id': bot.id, 'channel_username': channel_username})
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, channel_has_been_removed.format(channel_username),
                                 reply_markup=self.make_main_keyboard()))
            return ConversationHandler.END
        else:
            return self.make_channels_layout(bot, update, CHOOSE_TO_REMOVE,
                                             no_such_channel + choose_channel_to_remove, user_data)

    # 'Add Channels' button
    def add_channel(self, bot, update, user_data):
        delete_messages(bot, user_data, update)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id, channels_str_4,
                             reply_markup=self.cancel_keyboard))
        return ADD_CHANNEL

    # call this when message with channel link arrive
    def confirm_add(self, bot, update, user_data):
        have_added = self.register_channel(bot, update, user_data)
        if have_added is True:
            delete_messages(bot, user_data, update)
            user_data['to_delete'].append(
                bot.send_message(update.message.chat_id, channel_added_success.format(update.message.text),
                                 reply_markup=self.post_keyboard))
            return ConversationHandler.END

    # 'Post on channel' button
    def post_on_channel(self, bot, update, user_data):
        delete_messages(bot, user_data, update)

        if channels_table.find({'bot_id': bot.id}).count() == 0:
            user_data['to_delete'].append(
                bot.send_message(update.callback_query.message.chat.id, no_channels,
                                 reply_markup=self.no_channel_keyboard))
            return ConversationHandler.END
        else:
            user_data['to_delete'].append(
                bot.send_message(update.callback_query.message.chat_id, post_message,
                                 reply_markup=self.post_keyboard))
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

    # def cancel(self, bot, update):
    #     bot.delete_message(update.message.chat_id, update.message.message_id)
    #     bot.delete_message(update.message.chat_id, update.message.message_id-1)

        # update.message.reply_text(
        #     "Command is cancelled =("
        # )
    #     get_help(bot, update)
    #     return ConversationHandler.END


# TODO: ask user if he/she sure to send posts to the channel
class SendPost(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_send_post")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    def choose_channel(self, bot, update, user_data):
        return Channels().make_channels_layout(bot, update, CHOOSE_TO_SEND_POST, choose_channel_to_post, user_data)

    @run_async
    def send_message(self, bot, update, user_data):
        # TODO: use of 'update.effective_chat.id' to get id of chat
        channel = channels_table.find_one({'bot_id': bot.id, 'channel_username': update.message.text})
        if channel:
            delete_messages(bot, user_data, update)
            user_data['channel'] = update.message.text
            user_data['to_delete'].append(
                bot.send_message(update.message.chat.id, send_post.format(update.message.text),
                                 reply_markup=self.reply_markup))
            return MESSAGE_TO_USERS
        else:
            return Channels().make_channels_layout(bot, update, CHOOSE_TO_SEND_POST, choose_channel_to_post, user_data)

    @run_async
    def received_message(self, bot, update, user_data):
        delete_messages(bot, user_data, update)
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
            [[InlineKeyboardButton(text="Done", callback_data="send_post_finish")]]
        )
        user_data['to_delete'].append(
            bot.send_message(update.message.chat_id,
                             string_dict(bot)["send_message_4"],
                             reply_markup=final_reply_markup))
        return MESSAGE_TO_USERS

    def send_post_finish(self, bot, update, user_data):
        delete_messages(bot, user_data, update)
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="help_back")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_5"],
                             reply_markup=final_reply_markup))
        logger.info("Admin {} on bot {}:{} sent a post to the channel".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        return ConversationHandler.END

    @run_async
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

    # def cancel(self, bot, update):
    #     update.message.reply_text(
    #         "Command is cancelled =("
    #     )

    #     get_help(bot, update)
    #     return ConversationHandler.END


MY_CHANNELS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().my_channels, pattern=r"my_channels", pass_user_data=True)],
    states={
        MY_CHANNELS: [RegexHandler('^Back$', Channels().back, pass_user_data=True),
                      MessageHandler(Filters.text, Channels().channel, pass_user_data=True)],

        MANAGE_CHANNEL: [CallbackQueryHandler(Channels().back, pattern=r"back", pass_user_data=True),
                         CallbackQueryHandler(Channels().finish_remove, pattern=r"channel_remove", pass_user_data=True),
                         CallbackQueryHandler(Channels())]
    },
    fallbacks=[]
)

ADD_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().add_channel, pattern=r"add_channel", pass_user_data=True)],
    states={
        ADD_CHANNEL: [MessageHandler(Filters.text, callback=Channels().confirm_add, pass_user_data=True),
                      CallbackQueryHandler(callback=Channels().back, pattern=r'cancel_add', pass_user_data=True)]
    },
    fallbacks=[]
)

REMOVE_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(Channels().choose_to_remove, pattern=r"remove_channel", pass_user_data=True)],
    states={
        CHOOSE_TO_REMOVE: [RegexHandler(r"@", Channels().finish_remove, pass_user_data=True),
                           RegexHandler('^Back$', Channels().back, pass_user_data=True)]
    },
    fallbacks=[]
)

POST_ON_CHANNEL_HANDLER = CallbackQueryHandler(Channels().post_on_channel,
                                               pattern=r"post_on_channel", pass_user_data=True)

SEND_POST_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendPost().choose_channel, pattern=r"write_post", pass_user_data=True)],
    states={
        CHOOSE_TO_SEND_POST: [RegexHandler(r"@", SendPost().send_message, pass_user_data=True),
                              RegexHandler('^Back$', SendPost().back, pass_user_data=True)],

        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendPost().received_message, pass_user_data=True),
                           CallbackQueryHandler(callback=SendPost().back, pattern=r"cancel_send_post",
                                                pass_user_data=True)]
    },
    fallbacks=[CallbackQueryHandler(callback=SendPost().send_post_finish,
                                    pattern=r"send_post_finish", pass_user_data=True)]
)


'''
# Post on channel -> Send a Poll -> no polls. wanna create one?(yes, back) -> 
#         -> creating poll -> poll was created(send on channel, back) -> are u sure to send? -> send to channel


# for sending polls to channels

# TODO: need to refactor
class SendPoll(object):
    def __init__(self):
        create_buttons = [[InlineKeyboardButton(text=create_button, callback_data="create_poll"),
                           InlineKeyboardButton(text=back_button, callback_data="help_back")]]
        self.create_markup = InlineKeyboardMarkup(
            create_buttons)
        self.back_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(text=back_button, callback_data="cancel_send_poll")]])

    def choose_channel(self, bot, update):
        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        if polls_list_of_dicts.count() == 0:
            bot.send_message(update.callback_query.message.chat.id,
                             polls_str_8,
                             reply_markup=self.create_markup)
            return ConversationHandler.END
        else:
            return Channels().make_channels_layout(bot, update, CHOOSE_TO_SEND_POLL, choose_channel_to_send_poll)

    @run_async
    def handle_send_poll(self, bot, update, user_data):
        channel = channels_table.find_one({'bot_id': bot.id, 'channel_username': update.message.text})
        if channel:
            bot.delete_message(update.message.chat_id, update.message.message_id)
            user_data['channel'] = update.message.text
            polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
            if polls_list_of_dicts.count() != 0:
                command_list = [command['title'] for command in polls_list_of_dicts]
                bot.send_message(update.message.chat.id,
                                 polls_str_9, reply_markup=self.back_keyboard)
                reply_keyboard = [command_list]
                bot.send_message(update.message.chat.id,
                                 polls_str_10,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
                return CHOOSE_POLL_TO_SEND
            else:
                bot.send_message(update.message.chat.id,
                                 polls_str_8,
                                 reply_markup=self.create_markup)
                return ConversationHandler.END
        else:
            return Channels().make_channels_layout(bot, update, CHOOSE_TO_SEND_POST, choose_channel_to_send_poll)

    @run_async
    def handle_send_title(self, bot, update, user_data):  # TODO save more poll instances
        chat_id, txt = initiate_chat_id(update)
        # sent = []
        poll_name = txt
        user_data["poll_name_to_send"] = poll_name
        # chats = chats_table.find({"bot_id": bot.id})
        # for chat in chats:
        #     if chat['chat_id'] != chat_id:
        #         if not any(sent_d['id'] == chat['chat_id'] for sent_d in sent):
        #             sent.append(chat['chat_id'])
        poll = polls_table.find_one({'title': poll_name})
        poll['options'] = ast.literal_eval(poll['options'])
        poll['meta'] = ast.literal_eval(poll['meta'])

        bot.send_message(user_data['channel'], PollBot().assemble_message_text(poll),
                         reply_markup=PollBot().assemble_inline_keyboard(poll, True),
                         parse_mode='Markdown'
                         )

        bot.send_message(chat_id, polls_str_12, reply_markup=ReplyKeyboardRemove())

        get_help(bot, update)

        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(bot, update)

        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    # Error handler
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)
        return


# for sending surveys to channels

class SendSurvey(object):
    def __init__(self):
        buttons = [[InlineKeyboardButton(text=back_button, callback_data="cancel_survey")]]
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    def choose_channel(self, bot, update):
        return Channels().make_channels_layout(bot, update, CHOOSE_CHANNEL_TO_SEND_SURVEY,
                                               choose_channel_to_send_survey)

    @run_async
    def handle_send_survey(self, bot, update, user_data):
        channel = channels_table.find_one({'bot_id': bot.id, 'channel_username': update.message.text})
        if channel:
            bot.delete_message(update.message.chat_id, update.message.message_id)
            user_data['channel'] = update.message.text
            surveys_list = surveys_table.find({"bot_id": bot.id})
            if surveys_list.count() != 0:
                bot.send_message(update.message.chat.id,
                                 survey_str_18, reply_markup=self.reply_markup)
                command_list = [survey['title'] for survey in surveys_list]
                reply_keyboard = [command_list]
                bot.send_message(update.message.chat.id,
                                 survey_str_19,
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
                return CHOOSE_SURVEY_TO_SEND
            else:
                admin_keyboard = [InlineKeyboardButton(text=create_button, callback_data="create_survey"),
                                  InlineKeyboardButton(text=back_button, callback_data="help_back")]
                bot.send_message(update.message.chat.id,
                                 survey_str_23,
                                 reply_markup=InlineKeyboardMarkup([admin_keyboard]))
                return ConversationHandler.END
        else:
            return Channels().make_channels_layout(bot, update, CHOOSE_CHANNEL_TO_SEND_SURVEY,
                                                   choose_channel_to_send_survey)

    @run_async
    def handle_send_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["title"] = txt
        survey = surveys_table.find_one({"bot_id": bot.id, 'title': txt})

        sent = []
        # chats = chats_table.find({"bot_id": bot.id})
        # for chat in chats:
        #     # if chat['chat_id'] != chat_id:
        #     if not any(sent_d == chat['chat_id'] for sent_d in sent):
        #         sent.append(chat['chat_id'])
        bot.send_message(chat_id=user_data['channel'], text=survey_str_20,
                         reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton(text=start_button,
                                                            callback_data="survey_{}".format(
                                                                str(txt)
                                                            ))]]
                                 ))

        # if len(sent) == 0:
        #     bot.send_message(chat_id, survey_str_21, reply_markup=ReplyKeyboardRemove())
        # else:
        #     bot.send_message(chat_id=chat_id, text=survey_str_22, reply_markup=ReplyKeyboardRemove())
        get_help(bot, update)
        logger.info("Admin {} on bot {}:{} sent a survey to the users:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, txt))
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(bot, update)
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(update.effective_chat.id,
                           update.effective_message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)


# There are already 'send_poll' pattern handler - mb use it
SEND_POLL_TO_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendPoll().choose_channel, pattern=r"post_poll_to_channel")],
    states={
        CHOOSE_TO_SEND_POLL: [RegexHandler(r"@", SendPoll().handle_send_poll, pass_user_data=True),
                              RegexHandler('^Back$', SendPoll().back, pass_user_data=True)],

        CHOOSE_POLL_TO_SEND: [MessageHandler(Filters.text, SendPoll().handle_send_title, pass_user_data=True),
                              CallbackQueryHandler(callback=SendPoll().back, pattern=r"cancel_send_poll")],
    },
    fallbacks=[]
)

SEND_SURVEY_TO_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendSurvey().choose_channel, pattern=r"post_survey")],
    states={
        CHOOSE_CHANNEL_TO_SEND_SURVEY: [RegexHandler(r"@", SendSurvey().handle_send_survey, pass_user_data=True),
                                        RegexHandler('^Back$', SendSurvey().back, pass_user_data=True)],

        CHOOSE_SURVEY_TO_SEND: [MessageHandler(Filters.text, SendSurvey().handle_send_title, pass_user_data=True),
                                CallbackQueryHandler(callback=SendSurvey().back, pattern=r"cancel_survey")]
    },
    fallbacks=[]
)
'''
