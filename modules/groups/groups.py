#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler
from database import groups_table
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
#       if there are only one group don't ask to choose group
#       Markdown support in write a post
#       When create new poll or survey -> send button is confused
#       HOW TO DELETE ALL RANDOM MESSAGES SEND BY USER
#       IF USER DELETE BOT FROM GROUP

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


# check that bot is admin and can send messages to the group
def check_group(bot, group_username):
    try:
        admins = bot.get_chat_administrators(group_username)
    except TelegramError as e:
        # print(e)
        # if bot is not admin in the group
        if str(e).startswith("Supergroup members are unavailable"):
            return string_dict(bot)["bot_is_not_admin_of_group"].format(group_username)
        elif str(e).startswith("There is no administrators in the private chat"):
            return str(e) + "\n" + string_dict(bot)["wrong_group_link_format"]
        # if group link is wrong
        else:
            return string_dict(bot)["wrong_group_link_format"]
    # Check that bot is able to send messages to the group
    for admin in admins:
        # bot is admin
        if admin.user.is_bot and admin.user.id == bot.id:
            # bot can post messages to the group
            if admin.can_post_messages:
                return True
            else:
                return string_dict(bot)["allow_bot_send_messages"]


# DELETING USING USER_DATA
class Channels(object):
    # ################################## HELP METHODS ###########################################################
    # update groups usernames if group username has benn changed.
    # call this only when at least one group exists in db
    def update_groups_usernames(self, bot, user_data, chat_id):
        for group in groups_table.find({'bot_id': bot.id}):
            # check that boy is admin
            # and check that bot can send messages to group
            check = check_group(bot, group['group_username'])
            if check is not True:
                user_data['to_delete'].append(
                    bot.send_message(chat_id,
                                     string_dict(bot)["bot_is_not_admin_of_group_2"]
                                     .format(group['group_username'])))
                groups_table.delete_one({'bot_id': bot.id, 'chat_id': group['chat_id']})
                continue
            # bot.get_chat() works with delay ?
            current_username = bot.get_chat(group['chat_id']).username
            if group['group_username'] != current_username:
                groups_table.update_one({'bot_id': bot.id, 'group_username': group['group_username']},
                                          {'$set': {'group_username': '@{}'.format(current_username)}})
        return groups_table.find({'bot_id': bot.id})

    # to make keyboard with groups
    def make_groups_layout(self, bot, update, state, text: str, user_data):
        no_group_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["add_button"],
                                                                          callback_data='add_group')],
                                                    [InlineKeyboardButton(string_dict(bot)["back_button"],
                                                                          callback_data="help_module(groups)")]])

        # bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
        delete_messages(bot, user_data, update)
        if groups_table.find({'bot_id': bot.id}).count() == 0:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, string_dict(bot)["no_groups"],
                                 reply_markup=no_group_keyboard))
            return ConversationHandler.END
        else:
            groups = self.update_groups_usernames(bot, user_data, update.effective_chat.id)
            command_list = [[x['group_username']] for x in groups] + [['Back']]
            # need to delete this message
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, text,
                                 reply_markup=ReplyKeyboardMarkup(command_list, one_time_keyboard=True)))
            return state

    def send_wrong_format_message(self, bot, update, user_data, text: str = None):
        cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["cancel_button"],
                                                                      callback_data='help_back')]])
        delete_messages(bot, user_data, update)
        user_data['to_delete'].append(
            bot.send_message(update.message.chat_id, string_dict(bot)["wrong_group_link_format"]
            if text is None else text,
                             reply_markup=cancel_keyboard))
        return ADD_GROUP

    # check that group username is correct
    def register_group(self, bot, update, user_data):
        link = update.message.text
        # VALIDATE USER MESSAGE
        if len(link.split(" ")) != 1 or len(link) > 45:
            return self.send_wrong_format_message(bot, update, user_data)
        if link.startswith(("https://t.me/", "t.me/")):
            split_message = link.split('t.me/')
            if len(split_message) == 2:
                if len(split_message[1]) > 32:
                    return self.send_wrong_format_message(bot, update, user_data)
                group_username = "@{}".format(split_message[1])
            # wrong format of group link
            else:
                return self.send_wrong_format_message(bot, update, user_data)
        elif link.startswith("@"):
            group_username = link
        else:
            group_username = "@{}".format(link)

        check = check_group(bot, group_username)
        if check is True:
            if not groups_table.find_one({'bot_id': bot.id, 'group_username': group_username}):
                group_chat_id = bot.get_chat(group_username).id
                groups_table.insert_one({'bot_id': bot.id,
                                           'group_username': group_username,
                                           'chat_id': group_chat_id})
                return group_username
            else:
                return self.send_wrong_format_message(bot, update, user_data,
                                                      string_dict(bot)["try_to_add_already_exist_group"])
        else:
            return self.send_wrong_format_message(bot, update, user_data, check)

    ################################################################

    # 'My Channels' button
    def my_groups(self, bot, update, user_data):
        return self.make_groups_layout(bot, update, MY_GROUPS, string_dict(bot)["groups_str_2"],
                                         user_data)

    # when user click on group name in 'My groups' menu
    def group(self, bot, update):
        one_group_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["send_donation_to_group"],
                                                        callback_data='send_donation_to_group_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["send_survey_to_group"],
                                                        callback_data="send_survey_to_group_{}".format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["send_poll_to_group"],
                                                        callback_data="send_poll_to_group_{}".format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["send_post_to_group"],
                                                        callback_data='group_write_post_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["remove_button"],
                                                        callback_data='remove_group_{}'.format(
                                                            update.message.text))],
                                  [InlineKeyboardButton(string_dict(bot)["back_button"],
                                                        callback_data="help_module(groups)")]])
        bot.send_message(update.message.chat_id, string_dict(bot)["groups_menu"],
                         reply_markup=one_group_keyboard)
        return ConversationHandler.END

    # call this when user have choose group for remove
    def finish_remove(self, bot, update, user_data):
        group_username = update.callback_query.data.replace("remove_group_", "")
        group = groups_table.find_one({'bot_id': bot.id, 'group_username': group_username})
        if group:
            delete_messages(bot, user_data, update)
            groups_table.delete_one({'bot_id': bot.id, 'group_username': group_username})
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, string_dict(bot)["group_has_been_removed"]
                                 .format(group_username),
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                     text=string_dict(bot)["back_button"],
                                     callback_data="help_module(groups)")]])
                                 ))
            return ConversationHandler.END
        else:
            return self.make_groups_layout(bot, update, CHOOSE_TO_REMOVE,
                                             string_dict(bot)["no_such_group"]
                                             + string_dict(bot)["choose_group_to_remove"], user_data)

    # 'Add Channels' button
    def add_group(self, bot, update, user_data):
        cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["cancel_button"],
                                                                      callback_data='help_back')]])
        delete_messages(bot, user_data, update)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id, string_dict(bot)["groups_str_4"],
                             reply_markup=cancel_keyboard))
        return ADD_GROUP

    # call this when message with group link arrive
    def confirm_add(self, bot, update, user_data):

        group_username = self.register_group(bot, update, user_data)
        if type(group_username) is str:
            post_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["send_post_to_group"],
                                                                        callback_data="group_write_post_{}".format(
                                                                            group_username))],
                                                  [InlineKeyboardButton(string_dict(bot)["send_poll_to_group"],
                                                                        callback_data="send_poll_to_group_{}".format(
                                                                            group_username))],
                                                  [InlineKeyboardButton(string_dict(bot)["send_survey_to_group"],
                                                                        callback_data="send_survey_to_group_{}".format(
                                                                            group_username))],
                                                  [InlineKeyboardButton(string_dict(bot)["back_button"],
                                                                        callback_data="help_module(groups)")]])
            delete_messages(bot, user_data, update)
            user_data['to_delete'].append(
                bot.send_message(update.message.chat_id, string_dict(bot)["group_added_success"]
                                 .format(update.message.text),
                                 reply_markup=post_keyboard))
            return ConversationHandler.END
        else:
            return ADD_GROUP

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
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        group_username = update.callback_query.data.replace("group_write_post", "")
        group = groups_table.find_one({'bot_id': bot.id,
                                           'group_username': group_username})
        print(update.callback_query.data)
        # if group:
        delete_messages(bot, user_data, update)
        print()
        user_data['group'] = update.callback_query.data.replace("group_write_post_", "")
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["send_post"].format(group_username),
                             reply_markup=reply_markup))
        return MESSAGE_TO_USERS
        # else:
        #     return Channels().make_groups_layout(bot, update, CHOOSE_TO_SEND_POST,
        #                                            string_dict(bot)["choose_group_to_post"], user_data)

    def received_message(self, bot, update, user_data):
        if "content" not in user_data:
            user_data["content"] = []
        if update.message.text:
            user_data["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            user_data["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            user_data["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            user_data["content"].append({"audio_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            user_data["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            user_data["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            user_data["content"].append({"video_file": video_note_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=string_dict(bot)["done_button"], callback_data="send_post_finish")],
             [InlineKeyboardButton(text="Cancel", callback_data="help_back")]]
        )
        user_data['to_delete'].append(
            bot.send_message(update.message.chat_id,
                             string_dict(bot)["send_message_4"],
                             reply_markup=final_reply_markup))
        return MESSAGE_TO_USERS

    def send_post_finish(self, bot, update, user_data):
        for content_dict in user_data["content"]:
            if "text" in content_dict:
                bot.send_message(user_data['group'],
                                 content_dict["text"])
            if "audio_file" in content_dict:
                bot.send_audio(user_data['group'], content_dict["audio_file"])
            if "video_file" in content_dict:
                bot.send_video(user_data['group'], content_dict["video_file"])
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    bot.send_photo(user_data['group'], content_dict["document_file"])
                else:
                    bot.send_document(user_data['group'], content_dict["document_file"])
            if "photo_file" in content_dict:
                bot.send_photo(user_data['group'], content_dict["photo_file"])

        delete_messages(bot, user_data, update)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(groups)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             string_dict(bot)["send_message_5"],
                             reply_markup=final_reply_markup))
        logger.info("Admin {} on bot {}:{} sent a post to the group".format(
            update.effective_user.first_name, bot.first_name, bot.id))
        user_data.clear()
        return ConversationHandler.END

    def help_back(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                             callback_data="help_module(groups)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_message_9"],
                         reply_markup=final_reply_markup)
        user_data.clear()
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


MY_GROUPS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().my_groups, pattern=r"my_groups", pass_user_data=True)],
    states={
        MY_GROUPS: [RegexHandler(r"@", Channels().group)]
    },
    fallbacks=[CallbackQueryHandler(callback=Channels().back, pattern=r"help_back", pass_user_data=True),
               CallbackQueryHandler(callback=Channels().back, pattern=r'help_module', pass_user_data=True),
               RegexHandler('^Back$', Channels().back, pass_user_data=True),
               ]
)

ADD_GROUP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Channels().add_group, pattern=r"add_group", pass_user_data=True)],
    states={
        ADD_GROUP: [MessageHandler(Filters.text, callback=Channels().confirm_add, pass_user_data=True)]
    },
    fallbacks=[CallbackQueryHandler(callback=Channels().back, pattern=r'help_back', pass_user_data=True),
               CallbackQueryHandler(callback=Channels().back, pattern=r'help_module', pass_user_data=True),

               ]
)

REMOVE_GROUP_HANDLER = CallbackQueryHandler(Channels().finish_remove,
                                              pattern=r"remove_group", pass_user_data=True)
# POST_ON_GROUP_HANDLER = CallbackQueryHandler(Channels().post_on_group,
#                                                pattern=r"post_on_group", pass_user_data=True)

SEND_POST_TO_GROUP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendPost().send_message, pattern=r"group_write_post", pass_user_data=True)],
    states={

        MESSAGE_TO_USERS: [MessageHandler(Filters.all, SendPost().received_message, pass_user_data=True)]
    },
    fallbacks=[CallbackQueryHandler(callback=SendPost().send_post_finish,
                                    pattern=r"send_post_finish", pass_user_data=True),
               CallbackQueryHandler(callback=SendPost.help_back, pattern=r'help_back', pass_user_data=True),
               CallbackQueryHandler(callback=SendPost.help_back, pattern=r'help_module', pass_user_data=True),
               ]
)
