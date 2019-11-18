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


# DELETING USING USER_DATA
class Groups(object):
    # ################################## HELP METHODS ###########################################################

    # to make keyboard with groups
    ################################################################

    # 'My Groups' button
    def my_groups(self, bot, update, user_data):
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
            groups = groups_table.find({'bot_id': bot.id})
            command_list = [[x['group_name']] for x in groups] + [['Back']]
            # need to delete this message
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, "Pick a group",
                                 reply_markup=ReplyKeyboardMarkup(command_list, one_time_keyboard=True)))
            return MY_GROUPS

    # when user click on group name in 'My groups' menu

    def group(self, bot, update):
        if update.message.text == "Back":
            get_help(bot, update)
            return ConversationHandler.END
        group_id = groups_table.find_one({"group_name": update.message.text})["group_id"]
        one_group_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(string_dict(bot)["send_donation_to_group"],
                                                        callback_data='send_donation_to_group_{}'.format(group_id
                                                                                                         ))],
                                  [InlineKeyboardButton(string_dict(bot)["send_survey_to_group"],
                                                        callback_data="send_survey_to_group_{}".format(
                                                            group_id))],
                                  [InlineKeyboardButton(string_dict(bot)["send_poll_to_group"],
                                                        callback_data="send_poll_to_group_{}".format(
                                                            group_id))],
                                  [InlineKeyboardButton(string_dict(bot)["send_post_to_group"],
                                                        callback_data='group_write_post_{}'.format(
                                                            group_id))],
                                  [InlineKeyboardButton(string_dict(bot)["remove_button"],
                                                        callback_data='remove_group_{}'.format(
                                                            group_id))],
                                  [InlineKeyboardButton(string_dict(bot)["back_button"],
                                                        callback_data="help_module(groups)")]])
        bot.send_message(update.message.chat_id, string_dict(bot)["groups_menu"],
                         reply_markup=one_group_keyboard)
        return ConversationHandler.END

    # call this when user have choose group for remove
    def finish_remove(self, bot, update, user_data):
        if "to_delete" not in user_data:
            user_data = {"to_delete": []}
        group_id = int(update.callback_query.data.replace("remove_group_", ""))
        group = groups_table.find_one({'bot_id': bot.id, 'group_id': group_id})
        if group:
            delete_messages(bot, user_data, update)
            groups_table.delete_one({'bot_id': bot.id, 'group_id': group_id})
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, string_dict(bot)["group_has_been_removed"]
                                 .format(group["group_name"]),
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                     text=string_dict(bot)["back_button"],
                                     callback_data="help_module(groups)")]])
                                 ))
            return ConversationHandler.END
        else:
            # need to delete this message
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, "There is no such group",
                                 reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                                     text=string_dict(bot)["back_button"],
                                     callback_data="help_module(groups)")]])
                                 ))

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
        group_id = update.callback_query.data.replace("group_write_post", "")
        delete_messages(bot, user_data, update)
        user_data['group'] = update.callback_query.data.replace("group_write_post_", "")
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["send_post"].format(group_id),
                             reply_markup=reply_markup))
        return MESSAGE_TO_USERS
        # else:
        #     return Groups().make_groups_layout(bot, update, CHOOSE_TO_SEND_POST,
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


class AddGroup(object):
    def add_group(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(groups)")]
        )
        reply_markup = InlineKeyboardMarkup(
            buttons)

        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["add_group_str"],
                         reply_markup=reply_markup)
        return ConversationHandler.END


ADD_GROUP_HANLDER=CallbackQueryHandler(callback=AddGroup.add_group, pattern="add_group")

MY_GROUPS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=Groups().my_groups, pattern=r"my_groups", pass_user_data=True)],
    states={
        MY_GROUPS: [MessageHandler(Filters.all, Groups().group)]
    },
    fallbacks=[CallbackQueryHandler(callback=Groups().back, pattern=r"help_back", pass_user_data=True),
               CallbackQueryHandler(callback=Groups().back, pattern=r'help_module', pass_user_data=True),
               RegexHandler('^Back$', Groups().back, pass_user_data=True),
               ]
)

REMOVE_GROUP_HANDLER = CallbackQueryHandler(Groups().finish_remove,
                                            pattern=r"remove_group", pass_user_data=True)
# POST_ON_GROUP_HANDLER = CallbackQueryHandler(Groups().post_on_group,
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
