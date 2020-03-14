# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging

from bson.objectid import ObjectId
from telegram.error import BadRequest, Unauthorized, TelegramError
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from helper_funcs.helper import get_help, back_to_modules
from helper_funcs.pagination import Pagination
from helper_funcs.misc import (delete_messages, lang_timestamp, get_obj, user_mention,
                               update_user_fields)
from modules.statistic.donation_statistic import DonationStatistic
from modules.users.message_helper import (MessageTemplate, send_deleted_message_content,
                                          AnswerToMessage, send_not_deleted_message_content,
                                          add_to_content)
from database import users_table, donations_table, users_messages_to_admin_table


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# STRINGS
# open_btn_str = "Open"
# no_user_str = "There are no such user"
# search_user_str = "Send username or name"
# name_or_username_wrong_length = "Name is so long\nSend username or name"
# it_may_take_time = "⌛️ The search may take some time."
# user_not_found = "There are no such user\nSend another username or name"


class UsersHandler(object):
    def users(self, update, context):
        delete_messages(update, context, True)
        # Set current page integer in user_data.
        if update.callback_query.data.startswith("users_list_pagination"):
            context.user_data["page"] = int(
                update.callback_query.data.replace("users_list_pagination_", ""))
        # If one of the filters buttons clicked -
        # set new filters for query and new menu buttons
        if (update.callback_query.data == 'users_layout'
                or update.callback_query.data == "show_all"):
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "is_admin": False,
                                           "unsubscribed": False}
            context.user_data["filters_buttons"] = [
                [InlineKeyboardButton(context.bot.lang_dict["show_banned_btn"],
                                      callback_data="show_banned")],
                [InlineKeyboardButton(context.bot.lang_dict["show_unbanned_btn"],
                                      callback_data="show_unbanned")]]

        elif update.callback_query.data == "show_banned":
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "is_admin": False,
                                           # "regular_messages_blocked": True
                                           "blocked": True,
                                           "unsubscribed": False}
            context.user_data["filters_buttons"] = [
                [InlineKeyboardButton(context.bot.lang_dict["show_all_users_btn"],
                                      callback_data="show_all")],
                [InlineKeyboardButton(context.bot.lang_dict["show_unbanned_btn"],
                                      callback_data="show_unbanned")]]

        elif update.callback_query.data == "show_unbanned":
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "is_admin": False,
                                           # "regular_messages_blocked": False
                                           "blocked": False,
                                           "unsubscribed": False}
            context.user_data["filters_buttons"] = [
                [InlineKeyboardButton(context.bot.lang_dict["show_all_users_btn"],
                                      callback_data="show_all")],
                [InlineKeyboardButton(text=context.bot.lang_dict["show_banned_btn"],
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
        if context.user_data["filter"].get("blocked") is True:
            title_str = "banned_users_title"
        elif context.user_data["filter"].get("blocked") is False:
            title_str = "not_banned_users_title"
        else:
            title_str = "users_layout_title"
        context.user_data['to_delete'].append(
            context.bot.send_message(update.callback_query.message.chat_id,
                                     text=context.bot.lang_dict[title_str].format(users.count()),
                                     parse_mode=ParseMode.HTML))
        # Keyboard with user list filters buttons
        main_buttons = (context.user_data["filters_buttons"]
                        + [[InlineKeyboardButton(context.bot.lang_dict["search_btn"],
                                                 callback_data="search_user")],
                            [InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                                  callback_data="back_to_module_users")]])
        # If no users just send back button.
        if users.count() == 0:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         text=context.bot.lang_dict["no_users_str"],
                                         reply_markup=InlineKeyboardMarkup(main_buttons)))
        else:
            # Create Pagination instance for showing page content and pages
            pagination = Pagination(users, page=context.user_data["page"])
            # Loop over users on given page and send users templates.
            for user in pagination.content:
                # Update user names and check if the user block the bot
                update_user_fields(context, user)
                # Send template with keyboard.
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton(context.bot.lang_dict["open_btn_str"],
                                          callback_data=f"open_user/{user['_id']}")]
                ])
                UserTemplate(user).send(update, context, reply_markup=reply_markup)
            # Send pagination navigation keyboard.
            pagination.send_keyboard(update, context,
                                     page_prefix="users_list_pagination",
                                     buttons=main_buttons)

    def open_user(self, update, context):
        delete_messages(update, context, True)
        if update.callback_query.data.startswith("open_user"):
            user_id = ObjectId(update.callback_query.data.split("/")[1])
            context.user_data["user"] = users_table.find_one({"_id": user_id})
        if not context.user_data["user"]:
            update.callback_query.answer(context.bot.lang_dict["no_user_str"])
            return self.back_to_users(update, context)
        extra_buttons = [[InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                               callback_data="back_to_users_list")]]
        reply_markup = self.user_markup(context, context.user_data["user"], extra_buttons)
        UserTemplate(context.user_data["user"]).send(update, context, reply_markup=reply_markup)
        return ConversationHandler.END

    def user_markup(self, context, user, extra_buttons=None):
        # Check that there are at least one message from user.
        # message = users_messages_to_admin_table.find_one(
        #     {"bot_id": context.bot.id,
        #      "user_id": user["user_id"],
        #      "anonim": False,
        #      "deleted": False})
        # Creating keyboard for user.
        user_buttons = []
        # TODO STRINGS
        if not user["unsubscribed"]:
            user_buttons.append(
                # todo change name callback
                [InlineKeyboardButton(context.bot.lang_dict["send_msg_to_user"],
                                      callback_data=f"send_message_to_user/{user['chat_id']}")])
            if user["blocked"]:
                user_buttons.append(
                    [InlineKeyboardButton(context.bot.lang_dict["unblock_user"],
                                          callback_data=f"unblock_user_{user['_id']}")])
            else:
                user_buttons.append(
                    [InlineKeyboardButton(context.bot.lang_dict["block_user"],
                                          callback_data=f"block_user_{user['_id']}")])

                if user["regular_messages_blocked"]:
                    user_buttons.append(
                        [InlineKeyboardButton(context.bot.lang_dict["unblock_messages_button"],
                                              callback_data=f"unblock_messages_{user['_id']}")])
                else:
                    user_buttons.append(
                        [InlineKeyboardButton(context.bot.lang_dict["block_messages_button"],
                                              callback_data=f"block_messages_{user['_id']}")])
            # if message:
            user_buttons.append(
                [InlineKeyboardButton(context.bot.lang_dict["user_messages"],
                                      callback_data=f"user_messages_{user['user_id']}")])
        if extra_buttons:
            user_buttons.extend(extra_buttons)
        return InlineKeyboardMarkup(user_buttons)

    def search_user(self, update, context):
        delete_messages(update, context, True)
        users = users_table.find({"bot_id": context.bot.id,
                                  "unsubscribed": False,
                                  "is_admin": False})
        if users.count():
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    context.bot.lang_dict["back_button"],
                    callback_data="back_to_users_list")]
            ])
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         text=context.bot.lang_dict["search_user_str"],
                                         reply_markup=reply_markup))
            return START_SEARCH_USER
        else:
            update.callback_query.answer(context.bot.lang_dict["no_users_str"])
            return self.back_to_users(update, context)

    def do_search(self, update, context):
        delete_messages(update, context, True)
        reply_buttons = [[InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                               callback_data="back_to_users_list")]]
        reply_markup = InlineKeyboardMarkup(reply_buttons)
        pattern = update.message.text
        if pattern.startswith("@"):
            pattern = pattern[1:]

        # Max full name length
        if len(pattern) > 128:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    text=context.bot.lang_dict["name_or_username_wrong_length"],
                    reply_markup=reply_markup))
            return START_SEARCH_USER
        else:
            # Get all users
            users = users_table.find({"bot_id": context.bot.id,
                                      "unsubscribed": False,
                                      "is_admin": False})

            # If no users just send back button.
            if not users.count():
                context.user_data["to_delete"].append(
                    context.bot.send_message(update.effective_chat.id,
                                             text=context.bot.lang_dict["no_users_str"],
                                             reply_markup=reply_markup))
            else:
                # Ask to "wait" notification
                notification_msg = context.bot.send_message(
                    update.effective_chat.id,
                    context.bot.lang_dict["it_may_take_time"],
                    reply_markup=reply_markup)
                result = list()
                # Loop over all users and find matches.
                for user in users:
                    # Update user names and check if the user block the bot
                    update_user_fields(context, user)
                    # Check username and full name for the pattern
                    if (not user["unsubscribed"]
                            and (pattern in user["username"]
                                 or pattern in user["full_name"])):
                        result.append(user)
                # Delete "wait" notification
                try:
                    notification_msg.delete()
                except TelegramError:
                    pass
                if result:
                    # Send title for user list.
                    context.user_data['to_delete'].append(
                        context.bot.send_message(
                            update.effective_chat.id,
                            text=context.bot.lang_dict["users_layout_title"].format(
                                users.count()),
                            parse_mode=ParseMode.HTML))
                    context.user_data["found_users"] = result
                    return self.send_found_users(update, context)
                else:
                    context.user_data["to_delete"].append(
                        context.bot.send_message(
                            update.effective_chat.id,
                            context.bot.lang_dict["user_not_found"],
                            reply_markup=reply_markup))
                    return START_SEARCH_USER

    def send_found_users(self, update, context):
        delete_messages(update, context, True)
        # Set current page integer in user_data.
        if (update.callback_query
                and update.callback_query.data.startswith("user_search_pagination")):
            context.user_data["page"] = int(
                update.callback_query.data.replace("user_search_pagination_", ""))
        if not context.user_data.get("page"):
            context.user_data["page"] = 1

        # Create Pagination instance for showing page content and pages
        pagination = Pagination(context.user_data["found_users"],
                                page=context.user_data["page"])
        # Loop over users on given page and send users templates.
        for user in pagination.content:
            # Send template with keyboard.
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(context.bot.lang_dict["open_btn_str"],
                                      callback_data=f"open_user/{user['_id']}")]
            ])
            UserTemplate(user).send(update, context, reply_markup=reply_markup)
        reply_buttons = [[InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                               callback_data="back_to_users_list")]]
        # Send pagination navigation keyboard.
        pagination.send_keyboard(update, context,
                                 page_prefix="user_search_pagination",
                                 buttons=reply_buttons)
        return FOUND_USERS

    def clear_and_reset_user_data(self, context):
        """Clear data and reset keys that users list use"""
        page = context.user_data["page"]
        filter_ = context.user_data["filter"]
        filters_buttons = context.user_data["filters_buttons"]
        context.user_data.clear()
        context.user_data["page"] = page
        context.user_data["filter"] = filter_
        context.user_data["filters_buttons"] = filters_buttons

    def back_to_users(self, update, context):
        """All backs to user list must be done through this method"""
        delete_messages(update, context, True)
        try:
            self.clear_and_reset_user_data(context)
            return self.users(update, context)
        except KeyError:
            logger.info("Something gone wrong while back to users list")
            context.user_data.clear()
            update.callback_query.data = "back_to_module_users"
            return back_to_modules(update, context)
            # return get_help(update, context)

    def back_to_open_user(self, update, context):
        """All backs to open user must be done through this method"""
        delete_messages(update, context, True)
        try:
            user_id = context.user_data["user"]["_id"]
            self.clear_and_reset_user_data(context)
            context.user_data["user"] = users_table.find_one({"_id": user_id})
            return self.open_user(update, context)
        except KeyError:
            logger.info("Something gone wrong while back to open user")
            context.user_data.clear()
            return get_help(update, context)


class UserBlockHandler(object):
    def block_messaging_confirmation(self, update, context):
        delete_messages(update, context, True)
        context.user_data["_id"] = ObjectId(
            update.callback_query.data.replace("block_messages_", ""))
        user = users_table.find_one({"_id": context.user_data["_id"]})
        if not user:
            update.callback_query.answer(context.bot.lang_dict["no_user_str"])
            return UsersHandler().back_to_users(update, context)
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["block_messages_button"],
                                  callback_data="block_messaging_confirm_true"),
             InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                  callback_data=f"back_to_open_user")]])
        UserTemplate(user).send(update, context,
                                text=context.bot.lang_dict["confirm_block_messages"],
                                reply_markup=markup)
        return ConversationHandler.END

    def block_messaging_finish(self, update, context):
        users_table.update_one({"_id": context.user_data["_id"]},
                               {"$set": {"regular_messages_blocked": True,
                                         "anonim_messages_blocked": True}})
        update.callback_query.answer(context.bot.lang_dict["messages_blocked_blink"])
        return UsersHandler().back_to_open_user(update, context)

    def unblock_messaging_finish(self, update, context):
        _id = ObjectId(update.callback_query.data.replace("unblock_messages_", ""))
        users_table.update_one({"_id": _id},
                               {"$set": {"regular_messages_blocked": False,
                                         "anonim_messages_blocked": False}})
        update.callback_query.answer(context.bot.lang_dict["messages_unblocked"])
        return UsersHandler().back_to_open_user(update, context)

    def ban_confirmation(self, update, context):
        delete_messages(update, context, True)
        context.user_data["_id"] = ObjectId(update.callback_query.data.replace("block_user_", ""))
        user = users_table.find_one({"_id": context.user_data["_id"]})
        if not user:
            update.callback_query.answer(context.bot.lang_dict["no_user_str"])
            return UsersHandler().back_to_users(update, context)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["block_user"],
                                  callback_data="block_user_confirm_true"),
             InlineKeyboardButton(context.bot.lang_dict["back_button"],
                                  callback_data=f"back_to_open_user")]
        ])
        UserTemplate(user).send(update, context,
                                text=context.bot.lang_dict["ban_confirm"],
                                reply_markup=reply_markup)
        return ConversationHandler.END

    def ban_finish(self, update, context):
        users_table.update_one({"_id": context.user_data["_id"]},
                               {"$set": {"blocked": True}})
        update.callback_query.answer(context.bot.lang_dict["user_banned_blink"])
        return UsersHandler().back_to_open_user(update, context)

    def unbun_finish(self, update, context):
        _id = ObjectId(update.callback_query.data.replace("unblock_user_", ""))
        users_table.update_one({"_id": _id},
                               {"$set": {"blocked": False}})
        update.callback_query.answer(context.bot.lang_dict["user_unbanned_blink"])
        return UsersHandler().back_to_open_user(update, context)


class SeeUserMessage(object):
    def see_messages(self, update, context):
        delete_messages(update, context, True)
        # Set current page integer in user_data.
        if update.callback_query.data.startswith("pagination_user_messages"):
            context.user_data["user_messages_page"] = int(
                update.callback_query.data.replace("pagination_user_messages_", ""))
        if not context.user_data.get("user_messages_page"):
            context.user_data["user_messages_page"] = 1
        # Take user_id of from button data and set it in the user_data
        # to show messages between pagination buttons clicks.
        if update.callback_query.data.startswith("user_messages"):
            context.user_data["user_id"] = int(
                update.callback_query.data.replace("user_messages_", ""))
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="back_to_open_user")])

        messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id,
             "user_id": context.user_data["user_id"],
             "anonim": False,
             "deleted": False}).sort([["_id", -1]])
        if not messages.count():
            update.callback_query.answer(context.bot.lang_dict["no_messages_blink"])
            return UsersHandler().back_to_open_user(update, context)
        pagination = Pagination(messages,
                                page=context.user_data["user_messages_page"])
        # Loop over messages on given page and send messages template.
        for message in pagination.content:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(context.bot.lang_dict["view_message_str"],
                                      callback_data=f"view_user_message_{message['_id']}")]
            ])
            # Send message template.
            MessageTemplate(message, context).send(update.effective_chat.id,
                                                   reply_markup=reply_markup)
        # Send pagination navigation keyboard.
        pagination.send_keyboard(
            update, context,
            buttons=buttons,
            page_prefix="pagination_user_messages",
            text=context.bot.lang_dict["message_count_str"].format(messages.count()))
        return ConversationHandler.END

    def view_message(self, update, context):
        delete_messages(update, context, True)
        # If "Open" button clicked - set message object in user data
        if update.callback_query.data.startswith("view_user_message_"):
            message_id = ObjectId(
                update.callback_query.data.replace("view_user_message_", ""))
            context.user_data["message"] = (
                users_messages_to_admin_table.find_one({"_id": message_id}))

            # When message opened first time - mark it like read.
            if context.user_data["message"]["is_new"]:
                users_messages_to_admin_table.update_one(
                    {"_id": message_id}, {"$set": {"is_new": False}})

        # Send user message content
        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=context.bot.lang_dict["user_content_title"],
                                     parse_mode=ParseMode.HTML))
        send_deleted_message_content(
            context,
            chat_id=update.effective_user.id,
            content=context.user_data["message"]["content"])
        # If answer exist show it
        if context.user_data["message"]["answer_content"]:
            context.user_data["to_delete"].append(
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=context.bot.lang_dict["answer_content_title"],
                                         parse_mode=ParseMode.HTML))
            send_deleted_message_content(
                context,
                chat_id=update.effective_user.id,
                content=context.user_data["message"]["answer_content"])
        buttons = []
        if not context.user_data["message"]["answer_content"]:
            buttons.append(
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["answer_button_str"],
                    callback_data=f"answer_to_user_message/"
                                  + str(context.user_data["message"]['_id']))])
        buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["delete_button_str"],
                # TODO NEW CALLBACK
                callback_data="confirm_delete_user_message")])
        buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="back_to_users_messages")])
        """buttons = [
            [InlineKeyboardButton(
                text=context.bot.lang_dict["answer_button_str"],
                callback_data=f"answer_to_user_message/"
                              + str(context.user_data["message"]['_id'])),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["delete_button_str"],
                 # TODO NEW CALLBACK
                 callback_data="confirm_delete_user_message")],
            [InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="back_to_users_messages")]
        ]"""
        # Send message template.
        MessageTemplate(context.user_data["message"], context).send(
            update.effective_chat.id, temp="short",
            reply_markup=InlineKeyboardMarkup(buttons))
        return ConversationHandler.END

    def confirm_delete_message(self, update, context):
        delete_messages(update, context, True)
        buttons = [[
            InlineKeyboardButton(
                text=context.bot.lang_dict["yes"],
                callback_data="finish_delete_user_message"),
            InlineKeyboardButton(
                text=context.bot.lang_dict["no"],
                callback_data="cancel_deletion")
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)

        MessageTemplate(context.user_data["message"], context).send(
            update.effective_chat.id,
            reply_markup=reply_markup,
            text=context.bot.lang_dict["delete_messages_double_check"])
        return DOUBLE_CHECK

    def delete_message_finish(self, update, context):
        users_messages_to_admin_table.update_one(
            {"_id": context.user_data["message"]["_id"]},
            {"$set": {"deleted": True}})

        user_messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id,
             "deleted": False,
             "user_id": context.user_data["user_id"],
             "anonim": False})

        if user_messages.count():
            return self.back_to_users_messages(update, context)
        else:
            update.callback_query.answer(context.bot.lang_dict["no_messages_blink"])
            return UsersHandler().back_to_open_user(update, context)

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
            # todo do better backs()
            user = context.user_data["user"]
        except KeyError:
            context.user_data.clear()
            return get_help(update, context)

        context.user_data.clear()
        context.user_data["page"] = page
        context.user_data["filter"] = filter_
        context.user_data["filters_buttons"] = filters_buttons
        context.user_data["user_id"] = user_id
        context.user_data["user_messages_page"] = user_messages_page
        # todo do better backs()
        context.user_data["user"] = users_table.find_one({"_id": user["_id"]})
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
            # todo do better backs()
            user = context.user_data["user"]
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
        # todo do better backs()
        context.user_data["user"] = users_table.find_one({"_id": user["_id"]})
        return self.view_message(update, context)


class SendMessageToUser(object):
    """Sending messages to user"""
    def send_message(self, update, context):
        delete_messages(update, context, True)
        context.user_data["chat_id"] = int(
            update.callback_query.data.split("/")[1])

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                  callback_data="back_to_open_user")]
        ])
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=context.bot.lang_dict["send_message_3"],
            reply_markup=reply_markup)
        return MESSAGE_TO_USER

    def received_message(self, update, context):
        add_to_content(update, context)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                  callback_data="send_message_finish")],
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                  callback_data="back_to_open_user")]
        ])
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=context.bot.lang_dict["send_message_4"],
                                 reply_markup=reply_markup)
        return MESSAGE_TO_USER

    def send_message_finish(self, update, context):
        try:
            send_not_deleted_message_content(
                context,
                # TODO NO CHAT_ID HERE
                chat_id=context.user_data["chat_id"],
                content=context.user_data["content"])
        except:
            update.callback_query.answer(context.bot.lang_dict["smth_gone_wrong_blink"])
            return UsersHandler().back_to_open_user(update, context)
        logger.info("Admin {} on bot {}:{} sent a message to the user".format(
            update.effective_user.first_name,
            context.bot.first_name, context.bot.id))
        # TODO STRINGS
        update.callback_query.answer("Message sent")
        return UsersHandler().back_to_open_user(update, context)


class UserTemplate(object):
    def __init__(self, obj: (ObjectId, dict, str)):
        user_obj = get_obj(users_table, obj)
        self._id = user_obj["_id"]
        self.user_id = user_obj["user_id"]
        self.chat_id = user_obj["chat_id"]
        self.username = user_obj["username"]
        self.full_name = user_obj["full_name"]
        self.timestamp = user_obj["timestamp"]
        self.regular_messages_blocked = user_obj["regular_messages_blocked"]
        self.unsubscribed = user_obj["unsubscribed"]

    def send(self, update, context, text="", reply_markup=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template(context) + "\n\n" + text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup))

    # todo add messages count
    def template(self, context):
        # self.update_fields(context)
        if self.username:
            _user_mention = user_mention(self.username, self.full_name)
        else:
            _user_mention = f'<a href="tg://user?id={self.user_id}">{self.full_name}</a>'

        return (context.bot.lang_dict["user_temp"].format(
            _user_mention, lang_timestamp(context, self.timestamp))
            # TODO STRINGS
            + (context.bot.lang_dict["unsub"] if self.unsubscribed else "")
            + "\n" + self.donates_to_string(context))

    def donates_to_string(self, context):
        donates = donations_table.find({"bot_id": context.bot.id,
                                        "user_id": self.user_id})
        return (context.bot.lang_dict["donations_count_str"].format(
            # TODO import fom another module
            DonationStatistic().create_amount(donates))
            if donates.count() else "")

    """def update_fields(self, context):
        # Update user full_name, username
        telegram_user = context.bot.get_chat_member(self.chat_id,
                                                    self.user_id).user
        new_user_fields = dict()
        if telegram_user.username != self.username:
            new_user_fields["username"] = telegram_user.username
            self.username = telegram_user.username

        if telegram_user.full_name != self.full_name:
            new_user_fields["full_name"] = telegram_user.full_name
            self.full_name = telegram_user.full_name

        # if the user has unsubscribed set it as unsubscribed
        try:
            context.bot.send_chat_action(self.chat_id, action="typing")
            if self.unsubscribed:
                new_user_fields["unsubscribed"] = False
                self.unsubscribed = False
        except Unauthorized:
            if not self.unsubscribed:
                new_user_fields["unsubscribed"] = True
                self.unsubscribed = True

        if new_user_fields:
            users_table.update_one({"_id": self._id},
                                   {"$set": new_user_fields})"""


"""def update_user_fields(context, user):
    # Update user full_name, username
    telegram_user = context.bot.get_chat_member(user["chat_id"],
                                                user["user_id"]).user
    new_user_fields = dict()
    if telegram_user.username != user["username"]:
        new_user_fields["username"] = telegram_user.username
        user["username"] = telegram_user.username

    if telegram_user.full_name != user["full_name"]:
        new_user_fields["full_name"] = telegram_user.full_name
        user["full_name"] = telegram_user.full_name

    # if the user has unsubscribed set it as unsubscribed
    try:
        context.bot.send_chat_action(user["chat_id"], action="typing")
        if user["unsubscribed"]:
            new_user_fields["unsubscribed"] = False
            user["unsubscribed"] = False
    except Unauthorized:
        if not user["unsubscribed"]:
            new_user_fields["unsubscribed"] = True
            user["unsubscribed"] = True

    if new_user_fields:
        users_table.update_one({"_id": user["_id"]},
                               {"$set": new_user_fields})"""


MESSAGE_TO_USERS, MESSAGE_TO_USER, DOUBLE_CHECK = range(3)
START_SEARCH_USER, FOUND_USERS = range(2)

USERS_LIST_HANDLER = CallbackQueryHandler(
    pattern="^(users_layout|"
            "show_all|"
            "show_banned|"
            "show_unbanned|"
            "users_list_pagination)",
    callback=UsersHandler().users)

OPEN_USER_HANDLER = CallbackQueryHandler(
    pattern=r"open_user",
    callback=UsersHandler().open_user)

SEARCH_USER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(pattern="search_user",
                             callback=UsersHandler().search_user)],
    states={
        START_SEARCH_USER: [MessageHandler(Filters.text,
                                           callback=UsersHandler().do_search)],

        FOUND_USERS: [CallbackQueryHandler(pattern=r"user_search_pagination",
                                           callback=UsersHandler().send_found_users)]
    },
    fallbacks=[CallbackQueryHandler(pattern="back_to_users_list",
                                    callback=UsersHandler().back_to_users),
               CallbackQueryHandler(pattern=r"open_user",
                                    callback=UsersHandler().open_user)]
)


"""BLOCK AND UNBLOCK MESSAGING FOR USER"""
CONFIRM_BLOCK_MESSAGING = CallbackQueryHandler(
    pattern=r"block_messages",
    callback=UserBlockHandler().block_messaging_confirmation)

FINISH_BLOCK_MESSAGING = CallbackQueryHandler(
    pattern="block_messaging_confirm_true",
    callback=UserBlockHandler().block_messaging_finish)

FINISH_UNBLOCK_MESSAGING = CallbackQueryHandler(
    pattern=r"unblock_messages",
    callback=UserBlockHandler().unblock_messaging_finish)


"""BAN AND UNBUN USERS"""
CONFIRM_BAN_USER = CallbackQueryHandler(
    pattern=r"block_user",
    callback=UserBlockHandler().ban_confirmation)

FINISH_BAN_USER = CallbackQueryHandler(
    pattern=r"block_user_confirm_true",
    callback=UserBlockHandler().ban_finish)

FINISH_UNBUN_USER = CallbackQueryHandler(
    pattern=r"unblock_user",
    callback=UserBlockHandler().unbun_finish)


"""USER MESSAGES"""
USER_MESSAGES_LIST = CallbackQueryHandler(
    pattern="^(user_messages|pagination_user_messages)",
    callback=SeeUserMessage().see_messages)

VIEW_USER_MESSAGE = CallbackQueryHandler(
    pattern=r"view_user_message",
    callback=SeeUserMessage().view_message)

"""DELETE ONE USER MESSAGE"""
DELETE_USER_MESSAGE_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern="confirm_delete_user_message",
            callback=SeeUserMessage().confirm_delete_message)],

    states={
        DOUBLE_CHECK: [
            CallbackQueryHandler(
                pattern=r"finish_delete_user_message",
                callback=SeeUserMessage().delete_message_finish),
            # CallbackQueryHandler(
            #     pattern="back_to_view_message",
            #     callback=SeeUserMessage().back_to_view_message)
        ]},

    fallbacks=[
        CallbackQueryHandler(
            pattern="cancel_deletion",
            callback=SeeUserMessage().back_to_view_message)
    ]
)

"""ANSWER TO SUBSCRIBER MESSAGE"""
answer_to_message = AnswerToMessage(
    back_button="back_to_view_message",
    state=MESSAGE_TO_USERS,
    final_callback=SeeUserMessage().back_to_view_message)

ANSWER_TO_MESSAGE_FROM_USER_LIST_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern=r"answer_to_user_message",
            callback=answer_to_message.send_message)],
    states={
        MESSAGE_TO_USERS: [
            MessageHandler(
                filters=Filters.all,
                callback=answer_to_message.received_message)],

    },
    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=answer_to_message.send_message_finish),
        CallbackQueryHandler(
            pattern=r"back_to_view_message",
            callback=SeeUserMessage().back_to_view_message)]
)


"""SEND MESSAGE TO USER"""
SEND_MESSAGE_TO_USER_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(
            pattern=r"send_message_to_user",
            callback=SendMessageToUser().send_message)],

    states={
        MESSAGE_TO_USER: [
            MessageHandler(
                filters=Filters.all,
                callback=SendMessageToUser().received_message)]
    },

    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=SendMessageToUser().send_message_finish),
        CallbackQueryHandler(
            pattern=r"back_to_users_list",
            callback=UsersHandler().back_to_users),
        CallbackQueryHandler(
            pattern="back_to_open_user",
            callback=UsersHandler().back_to_open_user)]
)


"""BACKS"""
BACK_TO_USER_MESSAGES_LIST = CallbackQueryHandler(
    pattern=r"back_to_users_messages",
    callback=SeeUserMessage().back_to_users_messages)

BACK_TO_USERS_LIST = CallbackQueryHandler(
    pattern=r"back_to_users_list",
    callback=UsersHandler().back_to_users)

BACK_TO_OPEN_USER = CallbackQueryHandler(
    pattern="back_to_open_user",
    callback=UsersHandler().back_to_open_user)

BACK_TO_OPEN_MESSAGE = CallbackQueryHandler(
    pattern="back_to_view_message",
    callback=SeeUserMessage().back_to_view_message)
