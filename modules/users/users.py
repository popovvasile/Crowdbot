# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging

from bson.objectid import ObjectId
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ParseMode)
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from database import (users_table, donations_table,
                      users_messages_to_admin_table)
from helper_funcs.helper import get_help
from helper_funcs.pagination import Pagination
from helper_funcs.misc import (delete_messages, lang_timestamp, get_obj,
                               user_mention)
from modules.statistic.donation_statistic import DonationStatistic
from modules.users.message_helper import (
    send_message_template, add_to_content, send_deleted_message_content,
    send_not_deleted_message_content)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


# TODO users that have blocked the bot can't be shown as the url mention
#      and must be deleted. Count of unsubscribers.
#      Check if the user active(Bot.send_chat_action) - if not remove it

class UsersHandler(object):
    def users(self, update, context):
        delete_messages(update, context, True)
        # Set current page integer in user_data.
        if update.callback_query.data.startswith("users_list_pagination"):
            context.user_data["page"] = int(
                update.callback_query.data.replace("users_list_pagination_",
                                                   ""))
        # If one of the filters buttons clicked -
        # set new filters for query and new menu buttons
        if (update.callback_query.data == 'users_layout'
                or update.callback_query.data == "show_all"):
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "is_admin": False}
            context.user_data["filters_buttons"] = [[
                InlineKeyboardButton(
                    text=context.bot.lang_dict["show_banned_btn"],
                    callback_data="show_banned"),
                InlineKeyboardButton(
                    text=context.bot.lang_dict["show_unbanned_btn"],
                    callback_data="show_unbanned")
            ]]

        elif update.callback_query.data == "show_banned":
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "is_admin": False,
                                           # "regular_messages_blocked": True
                                           "blocked": True}
            context.user_data["filters_buttons"] = [[
                InlineKeyboardButton(
                    text=context.bot.lang_dict["show_all_users_btn"],
                    callback_data="show_all"),
                InlineKeyboardButton(
                    text=context.bot.lang_dict["show_unbanned_btn"],
                    callback_data="show_unbanned")
            ]]

        elif update.callback_query.data == "show_unbanned":
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "is_admin": False,
                                           # "regular_messages_blocked": False
                                           "blocked": False}
            context.user_data["filters_buttons"] = [[
                InlineKeyboardButton(
                    text=context.bot.lang_dict["show_all_users_btn"],
                    callback_data="show_all"),
                InlineKeyboardButton(
                    text=context.bot.lang_dict["show_banned_btn"],
                    callback_data="show_banned")]]
        if not context.user_data.get("page"):
            context.user_data["page"] = 1

        # Send page with users.
        self.send_users_layout(update, context)
        # return USERS
        return ConversationHandler.END

    def send_users_layout(self, update, context):
        # Get users with filters from user_data.
        users = users_table.find(
            context.user_data["filter"]).sort([["_id", -1]])
        # Send title for user list.
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict[
                    "banned_users_title"
                    if context.user_data["filter"].get("blocked") is True
                    else "not_banned_users_title"
                    if context.user_data["filter"].get("blocked") is False
                    else "users_layout_title"].format(users.count()),
                parse_mode=ParseMode.HTML))

        main_buttons = (context.user_data["filters_buttons"]
                        + [[InlineKeyboardButton(
                                text=context.bot.lang_dict["back_button"],
                                callback_data="back_to_module_users")]])
        # If no users just send back button.
        if users.count() == 0:
            # update.callback_query.answer(
            #     context.bot.lang_dict["no_users_str"])
            # return self.back_from_users_list(update, context)
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["no_users_str"],
                    reply_markup=InlineKeyboardMarkup(main_buttons)
                ))
        else:
            # Send pagination keyboard.
            pagination = Pagination(users, page=context.user_data["page"])
            # Loop over users on given page and send users templates.
            for user in pagination.content:
                # Check that there are at least one message from user.
                message = users_messages_to_admin_table.find_one(
                    {"bot_id": context.bot.id,
                     "user_id": user["user_id"],
                     "anonim": False})
                # Creating keyboard for user.
                user_buttons = [[]]
                # TODO STRINGS
                if user["blocked"]:
                    user_buttons[0].append(InlineKeyboardButton(
                        text="Unblock",
                        callback_data=f"unblock_user_{user['user_id']}"))
                else:
                    user_buttons[0].append(InlineKeyboardButton(
                        text="Block",
                        callback_data=f"block_user_{user['user_id']}"))

                    if user["regular_messages_blocked"]:
                        user_buttons[0].append(InlineKeyboardButton(
                            text=context.bot.lang_dict[
                                "unblock_messages_button"],
                            callback_data=f"unblock_messages_"
                                          f"{user['user_id']}"))
                    else:
                        user_buttons[0].append(InlineKeyboardButton(
                            text=context.bot.lang_dict["block_messages_button"],
                            callback_data=f"block_messages_{user['user_id']}"))

                if message:
                    user_buttons[0].append(InlineKeyboardButton(
                        text="Messages",
                        callback_data=f"user_messages_{user['user_id']}"))
                # Send template with keyboard.
                UserTemplate(user).send(
                    update, context,
                    reply_markup=InlineKeyboardMarkup(user_buttons))
            # Send pagination navigation keyboard.
            pagination.send_keyboard(
                update, context,
                page_prefix="users_list_pagination",
                buttons=main_buttons)

    def back_to_users(self, update, context):
        """
        All backs to user list must be done through this method
        """
        delete_messages(update, context, True)
        try:
            page = context.user_data["page"]
            filter_ = context.user_data["filter"]
            filters_buttons = context.user_data["filters_buttons"]

            context.user_data.clear()
            context.user_data["page"] = page
            context.user_data["filter"] = filter_
            context.user_data["filters_buttons"] = filters_buttons
            return self.users(update, context)
        except KeyError:
            context.user_data.clear()
            return get_help(update, context)


class UserBlockHandler(object):
    def block_messaging_confirmation(self, update, context):
        delete_messages(update, context, True)
        context.user_data["user_id"] = int(
            update.callback_query.data.replace("block_messages_", ""))

        user = users_table.find_one({"user_id": context.user_data["user_id"],
                                     "bot_id": context.bot.id})

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=context.bot.lang_dict["block_messages_button"],
                callback_data="block_messaging_confirm_true"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["back_button"],
                 callback_data="back_to_users_list")]])
        # TODO STRINGS
        UserTemplate(user).send(
            update, context,
            text="Are you sure that you want to block messages for this user?"
                 "\nUser won't be able to send messages anymore",
            reply_markup=markup)
        return ConversationHandler.END

    def block_messaging_finish(self, update, context):
        users_table.update_one({"bot_id": context.bot.id,
                                "user_id": context.user_data["user_id"]},
                               {"$set": {"regular_messages_blocked": True,
                                         "anonim_messages_blocked": True}})
        # TODO STRINGS
        update.callback_query.answer(
            "User won't be able to send messages anymore")
        return UsersHandler().back_to_users(update, context)

    def unblock_messaging_finish(self, update, context):
        user_id = int(
            update.callback_query.data.replace("unblock_messages_", ""))
        users_table.update_one({"user_id": user_id},
                               {"$set": {"regular_messages_blocked": False,
                                         "anonim_messages_blocked": False}})
        # TODO STRINGS
        update.callback_query.answer("User has been removed from the mute")
        return UsersHandler().back_to_users(update, context)

    def ban_confirmation(self, update, context):
        delete_messages(update, context, True)
        context.user_data["user_id"] = int(
            update.callback_query.data.replace("block_user_", ""))
        user = users_table.find_one({"user_id": context.user_data["user_id"],
                                     "bot_id": context.bot.id})
        # TODO STRINGS
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="Block",
                callback_data="block_user_confirm_true"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["back_button"],
                 callback_data="back_to_users_list")]
        ])
        # TODO STRINGS
        UserTemplate(user).send(
            update, context,
            text="Are you sure that you want ban this user?"
                 "\nUser won't be able use your bot anymore",
            reply_markup=markup)
        return ConversationHandler.END

    def ban_finish(self, update, context):
        users_table.update_one({"bot_id": context.bot.id,
                                "user_id": context.user_data["user_id"]},
                               {"$set": {"blocked": True}})
        # TODO STRINGS
        update.callback_query.answer(
            "User won't be able to use your bot anymore")
        return UsersHandler().back_to_users(update, context)

    def unbun_finish(self, update, context):
        user_id = int(
            update.callback_query.data.replace("unblock_user_", ""))
        users_table.update_one({"user_id": user_id},
                               {"$set": {"blocked": False}})
        # TODO STRINGS
        update.callback_query.answer(
            "User has been removed from the blacklist")
        return UsersHandler().back_to_users(update, context)


class SeeUserMessage(object):
    def see_messages(self, update, context):
        delete_messages(update, context, True)
        # Set current page integer in user_data.
        if update.callback_query.data.startswith("pagination_user_messages"):
            context.user_data["user_messages_page"] = int(
                update.callback_query.data.replace(
                    "pagination_user_messages_", ""))
        if not context.user_data.get("user_messages_page"):
            context.user_data["user_messages_page"] = 1
        # Take user_id of from button data
        # and set it in the user_data to show messages
        # between pagination buttons clicks.
        if update.callback_query.data.startswith("user_messages"):
            context.user_data["user_id"] = int(
                update.callback_query.data.replace("user_messages_", ""))
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                  callback_data="back_to_users_list")])
        # There are at least one message checked in previous menu.
        # So don't need to check count again.
        messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id,
             "user_id": context.user_data["user_id"],
             "anonim": False}).sort([["_id", -1]])
        pagination = Pagination(messages,
                                page=context.user_data["user_messages_page"])
        # Loop over messages on given page and send messages template.
        for message in pagination.content:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["view_message_str"],
                    callback_data=f"view_user_message_{message['_id']}")]
            ])
            # Send message template.
            send_message_template(update, context, message, reply_markup)
        # Send pagination navigation keyboard.
        pagination.send_keyboard(
            update, context,
            buttons=buttons, page_prefix="pagination_user_messages",
            text=context.bot.lang_dict["back_text"]
            + context.bot.lang_dict["message_count_str"].format(
                messages.count()))

        return ConversationHandler.END

    def view_message(self, update, context):
        delete_messages(update, context, True)
        # If "Open" button clicked - set message object in user data
        if update.callback_query.data.startswith("view_user_message_"):
            message = users_messages_to_admin_table.find_one({"_id": ObjectId(
                update.callback_query.data.replace("view_user_message_", ""))
            })
            # When message opened first time - mark it like read.
            if message["is_new"]:
                users_messages_to_admin_table.update_one(
                    {"_id": message["_id"]}, {"$set": {"is_new": False}})
            context.user_data["message"] = message
        # send_message_content(update, context, context.user_data["message"])
        send_deleted_message_content(
            context,
            chat_id=update.effective_user.id,
            content=context.user_data["message"]["content"])
        buttons = [
            [InlineKeyboardButton(
                text=context.bot.lang_dict["answer_button_str"],
                callback_data=f"answer_to_user_message_"
                              + str(context.user_data["message"]['_id'])),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["delete_button_str"],
                 # TODO NEW CALLBACK
                 callback_data="delete_user_message_"
                               + str(context.user_data["message"]["_id"]))],
            [InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="back_to_users_messages")]
        ]
        send_message_template(update, context, context.user_data["message"],
                              reply_markup=InlineKeyboardMarkup(buttons))
        return ConversationHandler.END

    def back_to_users_messages(self, update, context):
        """
        All backs to the user messages list must be done through this method
        """
        delete_messages(update, context, True)
        try:
            # Data for showing users list when - back
            page = context.user_data["page"]
            filter_ = context.user_data["filter"]
            filters_buttons = context.user_data["filters_buttons"]
            # Data for showing users messages when - back
            user_id = context.user_data["user_id"]
            user_messages_page = context.user_data["user_messages_page"]
        except KeyError:
            context.user_data.clear()
            return get_help(update, context)

        context.user_data.clear()
        context.user_data["page"] = page
        context.user_data["filter"] = filter_
        context.user_data["filters_buttons"] = filters_buttons
        context.user_data["user_id"] = user_id
        context.user_data["user_messages_page"] = user_messages_page
        return self.see_messages(update, context)

    def back_to_view_message(self, update, context):
        """
        All backs to the opened user message must be done through this method
        """
        delete_messages(update, context, True)
        try:
            # Data for showing users list when - back
            page = context.user_data["page"]
            filter_ = context.user_data["filter"]
            filters_buttons = context.user_data["filters_buttons"]
            # Data for showing users messages when -back
            user_id = context.user_data.get("user_id")
            user_messages_page = context.user_data["user_messages_page"]
            # Data for showing open message when - back
            message = context.user_data["message"]
        except KeyError:
            context.user_data.clear()
            return get_help(update, context)

        context.user_data.clear()
        context.user_data["page"] = page
        context.user_data["filter"] = filter_
        context.user_data["filters_buttons"] = filters_buttons
        context.user_data["user_id"] = user_id
        context.user_data["user_messages_page"] = user_messages_page
        context.user_data["message"] = users_messages_to_admin_table.find_one(
            {"_id": message["_id"]})
        return self.view_message(update, context)


class AnswerToMessageFromUserList(object):
    def send_message(self, update, context):
        delete_messages(update, context, True)
        buttons = list()
        buttons.append(
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                  callback_data="back_to_view_message")])
        reply_markup = InlineKeyboardMarkup(buttons)
        message = users_messages_to_admin_table.find_one(
            {"_id": ObjectId(update.callback_query.data.replace(
                "answer_to_user_message_", ""))})
        context.user_data["chat_id"] = message["chat_id"]

        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=context.bot.lang_dict["send_message_3"],
            reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    def received_message(self, update, context):
        add_to_content(update, context)
        final_reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                  callback_data="send_message_finish")],
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                  callback_data="back_to_view_message")]
        ])
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=context.bot.lang_dict["send_message_4"],
                                 reply_markup=final_reply_markup)

        return MESSAGE_TO_USERS

    def send_message_finish(self, update, context):
        context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=context.bot.lang_dict["send_message_answer_user"])
        send_not_deleted_message_content(
            context,
            chat_id=context.user_data["chat_id"],
            content=context.user_data["content"])
        """for content_dict in context.user_data["content"]:
            if "text" in content_dict:
                context.bot.send_message(context.user_data["chat_id"],
                                         content_dict["text"])
            if "audio_file" in content_dict:
                context.bot.send_audio(context.user_data["chat_id"],
                                       content_dict["audio_file"])
            if "voice_file" in content_dict:
                context.bot.send_voice(context.user_data["chat_id"],
                                       content_dict["voice_file"])
            if "video_file" in content_dict:
                context.bot.send_video(context.user_data["chat_id"],
                                       content_dict["video_file"])
            if "video_note_file" in content_dict:
                context.bot.send_video_note(context.user_data["chat_id"],
                                            content_dict["video_note_file"])
            if "document_file" in content_dict:
                if (".png" in content_dict["document_file"] or
                        ".jpg" in content_dict["document_file"]):
                    context.bot.send_photo(context.user_data["chat_id"],
                                           content_dict["document_file"])
                else:
                    context.bot.send_document(context.user_data["chat_id"],
                                              content_dict["document_file"])
            if "photo_file" in content_dict:
                context.bot.send_photo(context.user_data["chat_id"],
                                       content_dict["photo_file"])
            if "animation_file" in content_dict:
                context.bot.send_animation(context.user_data["chat_id"],
                                           content_dict["animation_file"])
            if "sticker_file" in content_dict:
                context.bot.send_sticker(context.user_data["chat_id"],
                                         content_dict["sticker_file"])"""

        logger.info("Admin {} on bot {}:{} sent a message to the user".format(
            update.effective_user.first_name,
            context.bot.first_name, context.bot.id))
        update.callback_query.answer("Message sent")
        return SeeUserMessage().back_to_users_messages(update, context)

    def delete_message(self, update, context):
        delete_messages(update, context, True)


# todo mb last seen for users. mb users images
class UserTemplate(object):
    def __init__(self, obj: (ObjectId, dict, str)):
        # self.context = context
        user_obj = get_obj(users_table, obj)
        self.user_id = user_obj["user_id"]
        # self.username = user_obj["username"]
        self.full_name = user_obj["full_name"]
        self.timestamp = user_obj["timestamp"]
        self.regular_messages_blocked = user_obj["regular_messages_blocked"]

    def send(self, update, context, text="", reply_markup=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template(context) + "\n\n" + text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup))

    # todo add messages count
    def template(self, context):
        return (context.bot.lang_dict["user_temp"].format(
            user_mention(self.user_id, self.full_name),
            lang_timestamp(context, self.timestamp))
            + "\n" + self.donates_to_string(context))

    def donates_to_string(self, context):
        donates = donations_table.find({"bot_id": context.bot.id,
                                        "user_id": self.user_id})
        return (context.bot.lang_dict["donations_count_str"].format(
            DonationStatistic().create_amount(donates))
            if donates.count() else "")

    def messaging_status(self):
        return ""

    # def messages(self, context):
    #     return users_messages_to_admin_table.find(
    #         {"bot_id": context.bot.id,
    #          "user_id": self.user_id}).sort([["_id", -1]])


MESSAGE_TO_USERS = range(1)

USERS_LIST_HANDLER = CallbackQueryHandler(
    pattern="^(users_layout|"
            "show_all|"
            "show_banned|"
            "show_unbanned|"
            "users_list_pagination)",
    callback=UsersHandler().users)

"""
BLOCK AND UNBLOCK MESSAGING FOR USER
"""
CONFIRM_BLOCK_MESSAGING = CallbackQueryHandler(
    pattern=r"block_messages",
    callback=UserBlockHandler().block_messaging_confirmation)

FINISH_BLOCK_MESSAGING = CallbackQueryHandler(
    pattern="block_messaging_confirm_true",
    callback=UserBlockHandler().block_messaging_finish)

FINISH_UNBLOCK_MESSAGING = CallbackQueryHandler(
    pattern=r"unblock_messages",
    callback=UserBlockHandler().unblock_messaging_finish)

"""
BAN AND UNBUN USERS
"""
CONFIRM_BAN_USER = CallbackQueryHandler(
    pattern=r"block_user",
    callback=UserBlockHandler().ban_confirmation)

FINISH_BAN_USER = CallbackQueryHandler(
    pattern=r"block_user_confirm_true",
    callback=UserBlockHandler().ban_finish)

FINISH_UNBUN_USER = CallbackQueryHandler(
    pattern=r"unblock_user",
    callback=UserBlockHandler().unbun_finish)

"""
USER MESSAGES
"""
USER_MESSAGES_LIST = CallbackQueryHandler(
    pattern="^(user_messages|pagination_user_messages)",
    callback=SeeUserMessage().see_messages)

VIEW_USER_MESSAGE = CallbackQueryHandler(
    pattern=r"view_user_message",
    callback=SeeUserMessage().view_message)

ANSWER_TO_MESSAGE_FROM_USER_LIST_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern=r"answer_to_user_message",
            callback=AnswerToMessageFromUserList().send_message)],

    states={
        MESSAGE_TO_USERS: [
            MessageHandler(
                filters=Filters.all,
                callback=AnswerToMessageFromUserList().received_message)],

    },

    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=AnswerToMessageFromUserList().send_message_finish),
        CallbackQueryHandler(
            pattern=r"back_to_view_message",
            callback=SeeUserMessage().back_to_view_message)]
)

"""
BACKS
"""
BACk_TO_USER_OPEN_MESSAGE = CallbackQueryHandler(
    pattern=r"back_to_users_messages",
    callback=SeeUserMessage().back_to_users_messages)

BACK_TO_USERS_LIST = CallbackQueryHandler(
    pattern=r"back_to_users_list",
    callback=UsersHandler().back_to_users)
