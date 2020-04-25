# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import time
from multiprocessing import Process
import requests
from threading import Thread

from bson.objectid import ObjectId
from haikunator import Haikunator
from telegram.error import TelegramError
from telegram.utils.promise import Promise
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler

from helper_funcs.helper import get_help, dismiss_button
from helper_funcs.misc import delete_messages, update_user_fields
from helper_funcs.pagination import Pagination
from logs import logger
from modules.users.users import UserTemplate
from modules.users.message_helper import (
    MessageTemplate, send_not_deleted_message_content, add_to_content,
    send_deleted_message_content, AnswerToMessage, SenderHelper)
from database import users_messages_to_admin_table, users_table, chatbots_table


def messages_menu(update, context):
    delete_messages(update, context, True)
    string_d_str = context.bot.lang_dict
    # Get unread messages count.
    new_messages_count = users_messages_to_admin_table.find(
        {"bot_id": context.bot.id, "is_new": True, "deleted": False}).count()
    messages_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text=string_d_str["send_message_button_2"]
                              + (f" ({new_messages_count})"
                                 if new_messages_count else ""),
                              callback_data="inbox_message")],
        [InlineKeyboardButton(text=string_d_str["send_message_button_1"],
                              callback_data="send_message_to_all_users")],
        [InlineKeyboardButton(text=string_d_str["delete_messages_btn"],
                              callback_data="del_messages_menu")],
        [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                              callback_data="help_module(users)")]
    ])
    context.bot.send_message(chat_id=update.callback_query.message.chat.id,
                             text=context.bot.lang_dict["polls_str_9"],
                             reply_markup=messages_keyboard)
    return ConversationHandler.END


def back_to_messages_menu(update, context):
    delete_messages(update, context, True)
    context.user_data.clear()
    return messages_menu(update, context)


class SendMessageToAdmin(SenderHelper):
    def send_message(self, update, context):
        delete_messages(update, context, True)
        buttons = [[InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="cancel_message_creating")]]
        reply_markup = InlineKeyboardMarkup(buttons)

        user = users_table.find_one({"user_id": update.effective_user.id,
                                     "bot_id": context.bot.id})
        context.user_data["new_message"] = dict()

        if "anonim" in update.callback_query.data:
            if (user.get("anonim_messages_blocked")
                    or user.get("regular_messages_blocked")):
                # TODO STRINGS
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="You have been blocked "
                                              "so u can't send anonim "
                                              "messages anymore")
                update.callback_query.answer("You have been blocked")
                get_help(update, context)
                return ConversationHandler.END

            context.user_data["new_message"]["anonim"] = True
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=context.bot.lang_dict["send_message_from_user_to_admin_anonim_text"],
                    reply_markup=reply_markup))
        else:
            if user.get("regular_messages_blocked"):
                # TODO STRINGS
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="You have been blocked "
                                              "so u can't send "
                                              "messages anymore")
                update.callback_query.answer("You have been blocked")
                get_help(update, context)
                return ConversationHandler.END

            context.user_data["new_message"]["anonim"] = False
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.callback_query.message.chat_id,
                    text=context.bot.lang_dict["send_message_from_user_to_admin_text"],
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.HTML))
        return MESSAGE

    def received_message(self, update, context):
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=context.bot.lang_dict["done_button"],
                callback_data="send_message_finish")],
            [InlineKeyboardButton(
                text=context.bot.lang_dict["cancel_button"],
                callback_data="cancel_message_creating")]
        ])
        return SenderHelper().help_receive(update, context, reply_markup, MESSAGE)

    def send_message_finish(self, update, context):
        # Save new message to database.
        update.callback_query.answer("Message was sent")

        if context.user_data["new_message"].get("anonim"):
            context.user_data["new_message"]["user_full_name"] = (
                "anonim_" + Haikunator().haikunate())
        else:
            context.user_data["new_message"]["user_full_name"] = (
                update.callback_query.from_user.full_name)

        context.user_data["new_message"]["content"] = context.user_data["content"]

        context.user_data["new_message"]["answer_content"] = list()
        context.user_data["new_message"]["is_new"] = True
        context.user_data["new_message"]["deleted"] = False
        context.user_data["new_message"]["user_id"] = update.effective_user.id
        context.user_data["new_message"]["bot_id"] = context.bot.id
        context.user_data["new_message"]["chat_id"] = update.effective_chat.id
        context.user_data["new_message"]["timestamp"] = (
            datetime.datetime.now().replace(microsecond=0))

        users_messages_to_admin_table.insert(context.user_data["new_message"])
        # TODO - async admin notifications
        # Send notification about new message to all admins
        for admin in users_table.find({"bot_id": context.bot.id, "is_admin": True}):
            if admin.get("messages_notification"):
                # Create notification text and send it.
                text = (context.bot.lang_dict["admin_new_message_notification_title"]
                        + MessageTemplate(context.user_data["new_message"],
                                          context).super_short_temp())
                reply_markup = dismiss_button(context)
                try:
                    context.bot.send_message(chat_id=admin["chat_id"],
                                             text=text,
                                             reply_markup=reply_markup,
                                             parse_mode=ParseMode.HTML)
                except:
                    continue

        # Console log
        logger.info("User {} on bot {}:{} sent a message to the admin".format(
            update.effective_user.first_name, context.bot.first_name,
            context.bot.id))
        return self.back(update, context)

    def cancel_message_creating(self, update, context):
        if "user_input" in context.user_data:
            context.user_data["to_delete"].extend(context.user_data["user_input"])
        return self.back(update, context)

    def back(self, update, context):
        delete_messages(update, context, True)
        context.user_data.clear()
        get_help(update, context)
        return ConversationHandler.END


class SendMessageToUsers(object):
    def send_message(self, update, context):
        delete_messages(update, context, True)
        buttons = list()
        buttons.append([InlineKeyboardButton(
                            text=context.bot.lang_dict["back_button"],
                            callback_data="cancel_creating_message")])
        reply_markup = InlineKeyboardMarkup(buttons)

        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["send_message_to_users_text"],
                reply_markup=reply_markup))
        return MESSAGE_TO_USERS

    def received_message(self, update, context):
        # TODO REFACTOR - use one content_dict structure for the whole project
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                  callback_data="send_message_finish")],
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                  callback_data="cancel_creating_message")]
        ])
        return SenderHelper().help_receive(update, context, reply_markup, MESSAGE_TO_USERS)

    def send_message_finish(self, update, context):
        """Old Version"""
        # users = users_table.find({"bot_id": context.bot.id,
        #                           "blocked": False,
        #                           "unsubscribed": False})
        # for user in users:
        #     update_user_fields(context, user)
        #     if (user["chat_id"] != update.callback_query.message.chat_id and
        #             not user["unsubscribed"]):
        #             try:
        #                 send_not_deleted_message_content(
        #                     context,
        #                     chat_id=user["chat_id"],
        #                     content=context.user_data["content"],
        #                     update=update)
        #             except:
        #                 continue

        """Processing Version"""
        # new_process = Process(target=SendMessageToUsers().mailing,
        #                       args=(update, context))
        # new_process.start()
        # new_process.join()

        """Threading Version"""
        Thread(target=SendMessageToUsers.mailing,
               args=(update, context, context.user_data["content"])).start()

        logger.info("Admin {} on bot {}:{} sent message to all users".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id))
        return back_to_messages_menu(update, context)

    @staticmethod
    def mailing(update, context, content):
        users = users_table.find({"bot_id": context.bot.id,
                                  "blocked": False,
                                  "unsubscribed": False})
        chat_bot = chatbots_table.find_one({"bot_id": context.bot.id})   # or {}
        for user in users:
            update_user_fields(context, user)
            if (  # user["chat_id"] != update.callback_query.message.chat_id and
                    not user["unsubscribed"]):
                """MQBot methods for sending content"""
                # telegram.error.RetryAfter: Flood control exceeded. Retry in 9 seconds
                # telegram.error.TimedOut: Timed out
                # telegram.vendor.ptb_urllib3.urllib3.exceptions.ReadTimeoutError:
                # socket.timeout: The read operation timed out

                # send_not_deleted_message_content(
                #     context,
                #     chat_id=user["chat_id"],
                #     content=content,
                #     update=update)

                """Requests for sending content"""
                # TODO try except
                for content_dict in content:
                    if "text" in content_dict:
                        requests.get(
                            "https://api.telegram.org/bot{}/sendMessage".format(chat_bot["token"]),
                            params={"chat_id": user["chat_id"],
                                    "text": content_dict["text"]})

                    if "audio_file" in content_dict:
                        requests.get(
                            "https://api.telegram.org/bot{}/sendAudio".format(chat_bot["token"]),
                            params={"chat_id": user["chat_id"],
                                    "audio": content_dict["audio_file"]})

                    if "voice_file" in content_dict:
                        requests.get(
                            "https://api.telegram.org/bot{}/sendVoice".format(chat_bot["token"]),
                            params={"chat_id": user["chat_id"],
                                    "voice": content_dict["voice_file"]})

                    if "video_file" in content_dict:
                        requests.get(
                            "https://api.telegram.org/bot{}/sendVideo".format(chat_bot["token"]),
                            params={"chat_id": user["chat_id"],
                                    "video": content_dict["video_file"]})

                    if "video_note_file" in content_dict:
                        requests.get(
                            "https://api.telegram.org/bot{}/sendVideoNote".format(
                                chat_bot["token"]),
                            params={"chat_id": user["chat_id"],
                                    "video_note": content_dict["video_note_file"]})

                    if "document_file" in content_dict:
                        if (".png" in content_dict["document_file"] or
                                ".jpg" in content_dict["document_file"]):
                            requests.get(
                                "https://api.telegram.org/bot{}/sendPhoto".format(
                                    chat_bot["token"]),
                                params={"chat_id": user["chat_id"],
                                        "photo": content_dict["document_file"]})
                        else:
                            requests.get(
                                "https://api.telegram.org/bot{}/sendDocument".format(
                                    chat_bot["token"]),
                                params={"chat_id": user["chat_id"],
                                        "document": content_dict["document_file"]})

                    if "photo_file" in content_dict:
                        requests.get(
                            "https://api.telegram.org/bot{}/sendPhoto".format(chat_bot["token"]),
                            params={"chat_id": user["chat_id"],
                                    "photo": content_dict["photo_file"]})

                    if "animation_file" in content_dict:
                        requests.get(
                            "https://api.telegram.org/bot{}/sendAnimation".format(
                                chat_bot["token"]),
                            params={"chat_id": user["chat_id"],
                                    "animation": content_dict["animation_file"]})

                    if "sticker_file" in content_dict:
                        requests.get(
                            "https://api.telegram.org/bot{}/sendSticker".format(
                                chat_bot["token"]),
                            params={"chat_id": user["chat_id"],
                                    "sticker": content_dict["sticker_file"]})

                    if "poll_file" in content_dict:
                        poll = content_dict["poll_file"]
                        context.bot.forward_message(chat_id=user["chat_id"],
                                                    # the poll should not be deleted
                                                    from_chat_id=update.effective_chat.id,
                                                    message_id=poll.message_id)

        return True

    def cancel_creating_message(self, update, context):
        if context.user_data.get("user_input"):
            context.user_data["to_delete"].extend(context.user_data["user_input"])
        return back_to_messages_menu(update, context)

    def back(self, update, context):
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)
        get_help(update, context)
        return ConversationHandler.END


# TODO refactor - do it better
class DeleteMessage(object):
    def delete_messages_menu(self, update, context):
        delete_messages(update, context, True)
        messages = users_messages_to_admin_table.find({"bot_id": context.bot.id,
                                                       "deleted": False})
        delete_buttons = list()
        delete_buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["delete_button_str_all"],
                callback_data="delete_message_all")])
        delete_buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["delete_button_str_last_week"],
                callback_data="delete_message_week")])
        delete_buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["delete_button_str_last_month"],
                callback_data="delete_message_month")])
        delete_buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="messages_menu_back")])
        if messages.count():
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         text=context.bot.lang_dict["delete_messages_menu_str"],
                                         reply_markup=InlineKeyboardMarkup(delete_buttons)))
            return ConversationHandler.END
        else:
            update.callback_query.answer(context.bot.lang_dict["no_messages_blink"])
            return back_to_messages_menu(update, context)

    def delete_message(self, update, context):
        delete_messages(update, context, True)

        messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id, "deleted": False})
        if messages.count():
            message_id = update.callback_query.data.replace("delete_message_", "")
            context.user_data["message_id"] = message_id

            buttons = [[InlineKeyboardButton(
                            text=context.bot.lang_dict["yes"],
                            callback_data="finish_delete_messages/" + message_id)]]
            if any(x in message_id for x in ["all", "week", "month"]):
                buttons[0].append(
                    InlineKeyboardButton(
                        text=context.bot.lang_dict["no"],
                        callback_data="back_to_del_messages_menu"))
            else:
                buttons[0].append(
                    InlineKeyboardButton(
                        text=context.bot.lang_dict["no"],
                        callback_data="back_to_view_inbox_message"))
            reply_markup = InlineKeyboardMarkup(buttons)

            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["delete_messages_double_check"],
                reply_markup=reply_markup)
            # TODO send a keyboard with callback
            #   depending on previous callback data
            return DOUBLE_CHECK

        else:
            update.callback_query.answer("There are no messages yet")
            return back_to_messages_menu(update, context)

    def delete_message_double_check(self, update, context):
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)

        if "all" in context.user_data["message_id"]:
            # delete all messages from the users
            users_messages_to_admin_table.update_many(
                {"bot_id": context.bot.id}, {"$set": {"deleted": True}})

        elif "week" in context.user_data["message_id"]:
            # delete all messages from the users for last week
            time_past = datetime.datetime.now() - datetime.timedelta(days=7)
            users_messages_to_admin_table.update_many(
                {"bot_id": context.bot.id, "timestamp": {'$gt': time_past}},
                {"$set": {"deleted": True}})

        elif "month" in context.user_data["message_id"]:
            # delete all messages from the users for last month
            time_past = datetime.datetime.now() - datetime.timedelta(days=30)
            users_messages_to_admin_table.update_many(
                {"bot_id": context.bot.id, "timestamp": {'$gt': time_past}},
                {"$set": {"deleted": True}})

        else:
            message_id = ObjectId(context.user_data["message_id"])
            users_messages_to_admin_table.update_one(
                {"_id": message_id},
                {"$set": {"deleted": True}})
            update.callback_query.answer(context.bot.lang_dict["success_delete_blink"])
            return SeeMessageToAdmin().back_to_inbox(update, context)

        if not users_messages_to_admin_table.find(
                {"bot_id": context.bot.id, "deleted": False}).count():
            update.callback_query.answer(context.bot.lang_dict["no_messages_blink"])
            return back_to_messages_menu(update, context)
        else:
            return self.back_to_del_messages_menu(update, context)

    def back_to_del_messages_menu(self, update, context):
        delete_messages(update, context, True)
        context.user_data.clear()
        return self.delete_messages_menu(update, context)


class SeeMessageToAdmin(object):
    def inbox(self, update, context):
        delete_messages(update, context, True)
        # Set current page integer in user_data.
        if update.callback_query.data.startswith("inbox_pagination_"):
            context.user_data["page"] = int(
                update.callback_query.data.replace("inbox_pagination_", ""))
        # If one of the filters buttons clicked - set new filters for query
        if update.callback_query.data == 'inbox_message':
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "deleted": False,
                                           "is_new": True}

        elif update.callback_query.data == "show_unread_messages":
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "deleted": False,
                                           "is_new": True}

        elif update.callback_query.data == "show_read_messages":
            context.user_data['page'] = 1
            context.user_data["filter"] = {"bot_id": context.bot.id,
                                           "deleted": False,
                                           "is_new": False}

        if not context.user_data.get("page"):
            context.user_data["page"] = 1
        # Send page with messages.
        self.send_messages_layout(update, context)
        return ConversationHandler.END

    def send_messages_layout(self, update, context):
        # Get messages with filters from user_data.
        messages = users_messages_to_admin_table.find(
            context.user_data["filter"]).sort([["_id", -1]])
        # get title string for inbox list.
        if context.user_data["filter"].get("is_new") is True:
            title_str = "unread_messages_title"
        elif context.user_data["filter"].get("is_new") is False:
            title_str = "read_messages_title"
        else:
            title_str = "message_count_str"
        title = context.bot.lang_dict[title_str].format(messages.count())

        # Keyboard with messages list filters buttons
        new_messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id,
             "deleted": False,
             "is_new": True}).sort([["_id", -1]])
        old_messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id,
             "deleted": False,
             "is_new": False}).sort([["_id", -1]])

        main_buttons = [
            [InlineKeyboardButton(
                text=context.bot.lang_dict["show_unread_messages"].format(new_messages.count()),
                callback_data="show_unread_messages"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["show_read_messages"].format(old_messages.count()),
                 callback_data="show_read_messages")],
            [InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="messages_menu_back")]
        ]
        if messages.count():
            # Create Pagination instance for showing page content and pages
            pagination = Pagination(messages, context.user_data["page"])
            for message in pagination.content:
                # Buttons for message.
                message_buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["view_message_str"],
                        callback_data=f"view_message_{message['_id']}")]
                ])
                # Send message template.
                MessageTemplate(message, context).send(
                    update.effective_chat.id, reply_markup=message_buttons)
            # Send pagination navigation keyboard.
            pagination.send_keyboard(
                update, context,
                buttons=main_buttons, page_prefix="inbox_pagination", text=title)
        else:
            # If no messages just send back button.
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["send_message_6"] + title,
                reply_markup=InlineKeyboardMarkup(main_buttons),
                parse_mode=ParseMode.HTML)

    def view_message(self, update, context):
        delete_messages(update, context, True)
        if update.callback_query.data.startswith("view_message"):
            message_id = ObjectId(
                update.callback_query.data.replace("view_message_", ""))
            context.user_data["message"] = (
                users_messages_to_admin_table.find_one({"_id": message_id}))

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
            content=context.user_data["message"]["content"],
            update=update)
        # If answer exist show it
        if context.user_data["message"]["answer_content"]:
            context.user_data["to_delete"].append(
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=context.bot.lang_dict["answer_content_title"],
                                         parse_mode=ParseMode.HTML))
            send_deleted_message_content(
                context,
                chat_id=update.effective_user.id,
                content=context.user_data["message"]["answer_content"],
                update=update)

        buttons = [[]]
        if not context.user_data["message"]["answer_content"]:
            buttons[0].append(InlineKeyboardButton(
                text=context.bot.lang_dict["answer_button_str"],
                callback_data="answer_to_message/"
                              + str(context.user_data["message"]["_id"])))

        buttons[0].append(InlineKeyboardButton(
                 text=context.bot.lang_dict["delete_button_str"],
                 callback_data="delete_message_"
                               + str(context.user_data["message"]["_id"])))

        # Back button.
        buttons.append([InlineKeyboardButton(
            text=context.bot.lang_dict["back_button"],
            callback_data="back_to_inbox")])
        # Send message template.
        MessageTemplate(context.user_data["message"], context).send(
            update.effective_chat.id,
            temp="short",
            reply_markup=InlineKeyboardMarkup(buttons))
        return ConversationHandler.END

    def block_anonim_messaging_confirmation(self, update, context):
        delete_messages(update, context, True)
        context.user_data["user_id"] = int(
            update.callback_query.data.replace("block_anonim_messaging_", ""))

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=context.bot.lang_dict["block_messages_button"],
                callback_data="block_anonim_messaging_confirm_true"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["back_button"],
                 callback_data="back_to_view_inbox_message")]])
        # Send message template.
        MessageTemplate(context.user_data["message"], context).send(
            update.effective_chat.id,
            reply_markup=reply_markup,
            text="Are you sure that you want to block anonim messages "
                 "for this user?\n This User won't be able to send "
                 "anonim messages anymore")
        return ConversationHandler.END

    def block_anonim_messaging_finish(self, update, context):
        users_table.update_one({"bot_id": context.bot.id,
                                "user_id": context.user_data["user_id"]},
                               {"$set": {"anonim_messages_blocked": True}})
        update.callback_query.answer(
            "User won't be able to send anonim messages anymore")
        return self.back_to_view_message(update, context)

    def unblock_anonim_messaging_finish(self, update, context):
        user_id = int(update.callback_query.data.replace(
            "unblock_anonim_messaging_", ""))
        users_table.update_one({"bot_id": context.bot.id, "user_id": user_id},
                               {"$set": {"anonim_messages_blocked": False}})
        update.callback_query.answer("For now user can send anonim messages")
        return self.back_to_view_message(update, context)

    def block_messaging_confirmation(self, update, context):
        delete_messages(update, context, True)
        context.user_data["user_id"] = int(
            update.callback_query.data.replace("from_inbox_block_messages_",
                                               ""))
        user = users_table.find_one({"user_id": context.user_data["user_id"],
                                     "bot_id": context.bot.id})

        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=context.bot.lang_dict["block_messages_button"],
                callback_data="from_inbox_block_messaging_confirm_true"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["back_button"],
                 callback_data="back_to_view_inbox_message")]])
        # TODO STRINGS
        UserTemplate(user).send(
            update, context,
            text="Are you sure that you want to block messages for this user?"
                 "\nUser won't be able to send any messages anymore",
            reply_markup=markup)
        return ConversationHandler.END

    def block_messaging_finish(self, update, context):
        delete_messages(update, context, True)
        users_table.update_one({"bot_id": context.bot.id,
                                "user_id": context.user_data["user_id"]},
                               {"$set": {"regular_messages_blocked": True,
                                         "anonim_messages_blocked": True}})
        # TODO STRINGS
        update.callback_query.answer(
            "User won't be able to send messages anymore")
        return self.back_to_view_message(update, context)

    def unblock_messaging_finish(self, update, context):
        user_id = int(update.callback_query.data.replace(
            "from_inbox_unblock_messages_", ""))
        users_table.update_one({"bot_id": context.bot.id, "user_id": user_id},
                               {"$set": {"regular_messages_blocked": False,
                                         "anonim_messages_blocked": False}})
        # TODO STRINGS
        update.callback_query.answer("User has been removed from the mute")
        return self.back_to_view_message(update, context)

    def back_to_view_message(self, update, context):
        """
        All backs to the opened user message must be done through this method
        """
        delete_messages(update, context, True)
        try:
            message = context.user_data["message"]
            inbox_filter = context.user_data["filter"]
            page = context.user_data.get("page", 1)
        except KeyError:
            context.user_data.clear()
            return get_help(update, context)

        context.user_data.clear()
        message = users_messages_to_admin_table.find_one({"_id": message["_id"]})
        context.user_data["filter"] = inbox_filter
        context.user_data["page"] = page
        if message:
            context.user_data["message"] = message
            return self.view_message(update, context)
        else:
            return SeeMessageToAdmin().back_to_inbox(update, context)

    def back_to_inbox(self, update, context):
        """
        All backs to the messages list(inbox) must be done through this method
        """
        delete_messages(update, context, True)
        try:
            page = context.user_data.get("page", 1)
            inbox_filter = context.user_data["filter"]
        except KeyError:
            context.user_data.clear()
            return get_help(update, context)

        context.user_data.clear()
        context.user_data["page"] = page
        context.user_data["filter"] = inbox_filter
        return self.inbox(update, context)


class SubscriberOpenMessage(object):
    # TODO STRINGS
    def open(self, update, context):
        delete_messages(update, context)
        message_id = ObjectId(update.callback_query.data.split("/")[1])
        message = users_messages_to_admin_table.find_one({"_id": message_id})
        if "open_delete" not in context.user_data:
            context.user_data["open_delete"] = list()
        # Send user message content
        context.user_data["open_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=context.bot.lang_dict["your_message_title"],
                                     parse_mode=ParseMode.HTML))
        send_deleted_message_content(context,
                                     chat_id=update.effective_user.id,
                                     content=message["content"],
                                     delete_key_name="open_delete",
                                     update=update)
        # Send admin answer content.
        # User can open message only if the answer exist
        context.user_data["open_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=context.bot.lang_dict["answer_title"],
                                     parse_mode=ParseMode.HTML))
        send_deleted_message_content(context,
                                     chat_id=update.effective_user.id,
                                     content=message["answer_content"],
                                     delete_key_name="open_delete",
                                     update=update)
        # Back button
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=context.bot.lang_dict["hide_btn"],
                callback_data="hide_answer")]])
        context.user_data["open_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=context.bot.lang_dict["back_text"],
                                     reply_markup=reply_markup))
        return ConversationHandler.END

    def hide_answer(self, update, context):
        for msg in context.user_data.get('open_delete', list()):
            if type(msg) is Promise:
                msg = msg.result()
            if not msg:
                continue
            try:
                context.bot.delete_message(update.effective_chat.id,
                                           msg.message_id)
            except TelegramError:
                continue
        return ConversationHandler.END


TOPIC, SEND_ANONIM, MESSAGE = range(3)
CHOOSE_CATEGORY, MESSAGE_TO_USERS = range(2)
DELETE_MESSAGES_MENU, DOUBLE_CHECK = range(2)


MESSAGES_MENU = CallbackQueryHandler(
    pattern="admin_messages",
    callback=messages_menu)


SEND_MESSAGE_TO_ADMIN_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CallbackQueryHandler(
            pattern="send_message_to_admin",
            callback=SendMessageToAdmin().send_message)],

    states={
        MESSAGE: [
            MessageHandler(
                filters=Filters.all,
                callback=SendMessageToAdmin().received_message)]
    },

    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=SendMessageToAdmin().send_message_finish),
        CallbackQueryHandler(
            pattern="cancel_message_creating",
            callback=SendMessageToAdmin().cancel_message_creating),
        CallbackQueryHandler(
            pattern="help_back",
            callback=SendMessageToUsers().back)]
)


"""OPEN BUTTON FOR SUBSCRIBER WHEN ANSWER READY"""
SHOW_MESSAGE_HANDLER = CallbackQueryHandler(
    pattern=r"subscriber_open_message",
    callback=SubscriberOpenMessage().open)

HIDE_MESSAGE_HANDLER = CallbackQueryHandler(
    pattern=r"hide_answer",
    callback=SubscriberOpenMessage().hide_answer)


"""SENDING MESSAGES TO ALL SUBSCRIBERS"""
SEND_MESSAGE_TO_USERS_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CallbackQueryHandler(
            pattern="send_message_to_all_users",
            callback=SendMessageToUsers().send_message)],

    states={

        MESSAGE_TO_USERS: [
            MessageHandler(
                filters=Filters.all,
                callback=SendMessageToUsers().received_message)],
    },

    fallbacks=[

        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=SendMessageToUsers().send_message_finish),
        CallbackQueryHandler(
            pattern="messages_menu_back",
            callback=back_to_messages_menu),
        CallbackQueryHandler(
            pattern="cancel_creating_message",
            callback=SendMessageToUsers().cancel_creating_message)
        ]
)


"""INBOX"""
SEE_MESSAGES_HANDLER = CallbackQueryHandler(
    pattern="^(inbox_message|inbox_pagination|show_unread_messages|show_read_messages)",
    callback=SeeMessageToAdmin().inbox)


"""DELETE 'WEEK' 'MONTH' 'ALL' MESSAGES"""
DELETE_MESSAGES_MENU_HANDLER = CallbackQueryHandler(
    pattern="del_messages_menu",
    callback=DeleteMessage().delete_messages_menu)

DELETE_MESSAGES_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CallbackQueryHandler(
            pattern="delete_message",
            callback=DeleteMessage().delete_message)
    ],

    states={
        DOUBLE_CHECK: [
            CallbackQueryHandler(
                pattern=r"finish_delete_messages",
                callback=DeleteMessage().delete_message_double_check),
            CallbackQueryHandler(
                pattern="back_to_del_messages_menu",
                callback=DeleteMessage().back_to_del_messages_menu)]},

    fallbacks=[
        CallbackQueryHandler(
            pattern="back_to_inbox",
            callback=SeeMessageToAdmin().back_to_inbox),
        CallbackQueryHandler(
            pattern="messages_menu_back",
            callback=back_to_messages_menu),
        CallbackQueryHandler(
            pattern="back_to_view_inbox_message",
            callback=SeeMessageToAdmin().back_to_view_message)
    ]
)


"""OPEN MESSAGE"""
SEE_MESSAGES_FINISH_HANDLER = CallbackQueryHandler(
    pattern="view_message_",
    callback=SeeMessageToAdmin().view_message)


"""ANSWER TO MESSAGE FROM INBOX"""
answer_to_message = AnswerToMessage(
    back_button="back_to_view_inbox_message",
    state=MESSAGE_TO_USERS,
    final_callback=SeeMessageToAdmin().back_to_view_message)

ANSWER_TO_MESSAGE_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[
        CallbackQueryHandler(
            pattern=r"answer_to_message",
            callback=answer_to_message.send_message)],

    states={
        MESSAGE_TO_USERS: [
            MessageHandler(
                filters=Filters.all,
                callback=answer_to_message.received_message)]
    },

    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=answer_to_message.send_message_finish),
        CallbackQueryHandler(
            pattern=r"back_to_view_inbox_message",
            callback=SeeMessageToAdmin().back_to_view_message)]
)


"""BLOCK AND UNBLOCK MESSAGING FOR ANONIM SENDER"""
CONFIRM_BLOCK_ANONIM_MESSAGING = CallbackQueryHandler(
    pattern=r"block_anonim_messaging",
    callback=SeeMessageToAdmin().block_anonim_messaging_confirmation)

FINISH_BLOCK_ANONIM_MESSAGING = CallbackQueryHandler(
    pattern="block_anonim_messaging_confirm_true",
    callback=SeeMessageToAdmin().block_anonim_messaging_finish)

UNBLOCK_ANONIM_MESSAGING = CallbackQueryHandler(
    pattern=r"unblock_anonim_messaging",
    callback=SeeMessageToAdmin(). unblock_anonim_messaging_finish)


"""BLOCK AND UNBLOCK MESSAGING FOR REGULAR SENDER"""
CONFIRM_BLOCK_MESSAGING_FROM_INBOX = CallbackQueryHandler(
    pattern=r"from_inbox_block_messages",
    callback=SeeMessageToAdmin().block_messaging_confirmation)

FINISH_BLOCK_MESSAGING_FROM_INBOX = CallbackQueryHandler(
    pattern="from_inbox_block_messaging_confirm_true",
    callback=SeeMessageToAdmin().block_messaging_finish)

FINISH_UNBLOCK_MESSAGING_FROM_INBOX = CallbackQueryHandler(
    pattern=r"from_inbox_unblock_messages",
    callback=SeeMessageToAdmin().unblock_messaging_finish)


"""BACKS"""
BACK_TO_INBOX_VIEW_MESSAGE = CallbackQueryHandler(
    pattern="back_to_view_inbox_message",
    callback=SeeMessageToAdmin().back_to_view_message)

BACK_TO_INBOX = CallbackQueryHandler(
    pattern="back_to_inbox",
    callback=SeeMessageToAdmin().back_to_inbox)

BACK_TO_MESSAGES_MENU = CallbackQueryHandler(
    pattern="messages_menu_back",
    callback=back_to_messages_menu)
