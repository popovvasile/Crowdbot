# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging

from bson.objectid import ObjectId
from haikunator import Haikunator
from telegram.error import TelegramError
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (MessageHandler, Filters, ConversationHandler,
                          CallbackQueryHandler, run_async)

from helper_funcs.helper import get_help
from helper_funcs.lang_strings.strings import emoji
from helper_funcs.misc import delete_messages, lang_timestamp, user_mention, update_user_fields
from helper_funcs.pagination import Pagination
from modules.users.users import UserTemplate
from modules.users.message_helper import (
    MessageTemplate, send_not_deleted_message_content, add_to_content,
    send_deleted_message_content, AnswerToMessage)
from database import (users_messages_to_admin_table,
                      user_categories_table, users_table)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

delete_messages_menu_str = "What do you want to do?"
no_messages_blink = "There are no messages"
success_delete_blink = "Message deleted"


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
        [InlineKeyboardButton(text="Delete messages",
                              callback_data="del_messages_menu")],
        # [InlineKeyboardButton(text=string_d_str["send_message_button_5"],
        #                       callback_data="send_message_to_donators")],
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


# class AddMessageCategory(object):
#
#     def add_category(self, update, context):
#         buttons = list()
#         buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                              callback_data="help_module(users)")])
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         bot.send_message(update.callback_query.message.chat_id,
#                          context.bot.lang_dict["send_message_14"], reply_markup=reply_markup)
#
#         return TOPIC
#
#     def add_category_finish(self, update, context):
#         categories_table.update({"category": update.message.text},
#                                 {"$set": {"category": update.message.text}},
#                                 upsert=True)
#         buttons = list()
#         buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                              callback_data="help_module(users)")])
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.send_message(update.message.chat_id,
#                          context.bot.lang_dict["send_message_15"],
#                          reply_markup=reply_markup)
#         return ConversationHandler.END
#
#
# class MessageCategory(object):
#
#     def show_category(self, update, context):
#         buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                          callback_data="help_module(users)"),
#                     InlineKeyboardButton(text=context.bot.lang_dict["add_message_category"],
#                                          callback_data="add_message_category"),
#                     ]]
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         bot.send_message(update.callback_query.message.chat_id,
#                          context.bot.lang_dict["send_message_16"], reply_markup=reply_markup)
#
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         categories = categories_table.find()
#         for category in categories:
#             delete_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["delete_button_str"],
#                                                     callback_data="delete_category_{}"
#                                                     .format(category["category"]))]]
#             delete_markup = InlineKeyboardMarkup(
#                 delete_buttons)
#             bot.send_message(update.callback_query.message.chat_id, category["category"],
#                              reply_markup=delete_markup)
#
#         return ConversationHandler.END
#
#
# class DeleteMessageCategory(object):
#
#     def delete_category(self, update, context):
#         bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                            message_id=update.callback_query.message.message_id)
#         buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                          callback_data="help_module(users)")]]
#         reply_markup = InlineKeyboardMarkup(
#             buttons)
#         categories_table.delete_one({"category": update.callback_query.data.replace("delete_category_", "")})
#
#         bot.send_message(update.callback_query.message.chat_id,
#                          context.bot.lang_dict["send_message_17"], reply_markup=reply_markup)
#
#         return ConversationHandler.END


class SendMessageToAdmin(object):
    def send_message(self, update, context):
        delete_messages(update, context, True)
        buttons = [[InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="help_back")]]
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
                    reply_markup=reply_markup))
        return MESSAGE

    # def send_topic(self, update, context):
    #     bot.send_message(update.message.chat_id,
    #                      random.choice(context.bot.lang_dict["polls_affirmations"]),
    #                      reply_markup=ReplyKeyboardRemove())
    #     user_data["topic"] = update.message.text
    #     buttons = list()
    #     buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
    #                                          callback_data="help_back")])
    #     reply_markup = InlineKeyboardMarkup(
    #         buttons)
    #     bot.send_message(update.message.chat_id,
    #                      context.bot.lang_dict["send_message_1"], reply_markup=reply_markup)
    #
    #     return MESSAGE

    def received_message(self, update, context):
        delete_messages(update, context)
        add_to_content(update, context)
        # TODO STRINGS
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="Done",
                callback_data="send_message_finish")],
            [InlineKeyboardButton(
                text="Cancel",
                callback_data="help_back")]
        ])
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["send_message_4"],
                reply_markup=reply_markup))
        return MESSAGE

    # @run_async
    def send_message_finish(self, update, context):
        # Save new message to database.
        update.callback_query.answer("Message was sent")

        if context.user_data["new_message"].get("anonim"):
            context.user_data["new_message"]["user_full_name"] = (
                "anonim_" + Haikunator().haikunate())
        else:
            context.user_data["new_message"]["user_full_name"] = (
                update.callback_query.from_user.full_name)

        context.user_data["new_message"]["content"] = (
            context.user_data["content"])

        context.user_data["new_message"]["answer_content"] = list()
        context.user_data["new_message"]["is_new"] = True
        context.user_data["new_message"]["deleted"] = False
        context.user_data["new_message"]["user_id"] = update.effective_user.id
        context.user_data["new_message"]["bot_id"] = context.bot.id
        context.user_data["new_message"]["chat_id"] = update.effective_chat.id
        context.user_data["new_message"]["timestamp"] = (
            datetime.datetime.now().replace(microsecond=0))

        users_messages_to_admin_table.insert(context.user_data["new_message"])
        # Send notification about new message to all admins
        for admin in users_table.find({"bot_id": context.bot.id,
                                       "is_admin": True}):
            # Create notification text and send it.
            text = ("<b>New Message</b> "
                    + MessageTemplate(context.user_data["new_message"],
                                      context).super_short_temp())
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["notification_close_btn"],
                    callback_data="dismiss"
                )]
            ])
            context.bot.send_message(chat_id=admin["chat_id"],
                                     text=text,
                                     reply_markup=reply_markup,
                                     parse_mode=ParseMode.HTML)

        # Console log
        logger.info("User {} on bot {}:{} sent a message to the admin".format(
            update.effective_user.first_name, context.bot.first_name,
            context.bot.id))
        return self.back(update, context)

    # def send_message_cancel(self, update, context):
    #     context.bot.delete_message(
    #        chat_id=update.callback_query.message.chat_id,
    #         message_id=update.callback_query.message.message_id)
    #     buttons = list()
    #     buttons.append([InlineKeyboardButton(
    #                         text=context.bot.lang_dict["back_button"],
    #                         callback_data="help_back")])
    #     final_reply_markup = InlineKeyboardMarkup(buttons)
    #     context.bot.send_message(
    #         chat_id=update.callback_query.message.chat_id,
    #         text=context.bot.lang_dict["send_message_9"],
    #         reply_markup=final_reply_markup)
    #     context.user_data.clear()
    #     return ConversationHandler.END

    def back(self, update, context):
        delete_messages(update, context, True)
        context.user_data.clear()
        get_help(update, context)
        return ConversationHandler.END


class SendMessageToUsers(object):
    def send_message(self, update, context):
        buttons = list()
        buttons.append([InlineKeyboardButton(
                            text=context.bot.lang_dict["back_button"],
                            callback_data="messages_menu_back")])
        reply_markup = InlineKeyboardMarkup(buttons)
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)

        categories = user_categories_table.find()
        if categories.count() > 0:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["back_text"],
                reply_markup=reply_markup)
            categories_list = ["All"] + [x["category"] for x in categories]
            category_markup = ReplyKeyboardMarkup([categories_list])

            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["send_message_1_1"],
                reply_markup=category_markup)
            return CHOOSE_CATEGORY
        else:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["send_message_to_users_text"],
                reply_markup=reply_markup)
            return MESSAGE_TO_USERS

    def choose_question(self, update, context):
        context.user_data["user_category"] = update.message.text
        buttons = list()
        buttons.append([InlineKeyboardButton(
                            text=context.bot.lang_dict["back_button"],
                            callback_data="messages_menu_back")])
        reply_markup = InlineKeyboardMarkup(buttons)
        # TODO STRINGS
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text="Cool",
                                 reply_markup=ReplyKeyboardRemove())
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=context.bot.lang_dict["send_message_1"],
                                 reply_markup=reply_markup)
        return MESSAGE_TO_USERS

    def received_message(self, update, context):
        delete_messages(update, context)
        add_to_content(update, context)
        final_reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                  callback_data="send_message_finish")],
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                  callback_data="messages_menu_back")]
        ])
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["send_message_4"],
                reply_markup=final_reply_markup))

        return MESSAGE_TO_USERS

    # @run_async
    def send_message_finish(self, update, context):  # TODO does not work
        if "user_category" not in context.user_data:
            users = users_table.find({"bot_id": context.bot.id,
                                      "blocked": False,
                                      "unsubscribed": False})
        elif context.user_data["user_category"] == "All":
            users = users_table.find({"bot_id": context.bot.id,
                                      "blocked": False,
                                      "unsubscribed": False})
        else:
            users = users_table.find(
                {"bot_id": context.bot.id,
                 "user_category": context.user_data["user_category"],
                 "blocked": False,
                 "unsubscribed": False})
        for user in users:
            update_user_fields(context, user)
            if user["chat_id"] != update.callback_query.message.chat_id:
                if not user["unsubscribed"]:
                    try:
                        send_not_deleted_message_content(
                            context,
                            chat_id=user["chat_id"],
                            content=context.user_data["content"])
                    except:
                        continue
        # context.bot.delete_message(
        #     chat_id=update.callback_query.message.chat_id,
        #     message_id=update.callback_query.message.message_id)
        # buttons = list()
        # buttons.append([InlineKeyboardButton(
        #     text=context.bot.lang_dict["back_button"],
        #     callback_data="help_module(users)")])

        # final_reply_markup = InlineKeyboardMarkup(buttons)
        # context.bot.send_message(update.callback_query.message.chat_id,
        #                          text=context.bot.lang_dict["send_message_5"],
        #                          reply_markup=final_reply_markup)
        logger.info("Admin {} on bot {}:{} sent message to all users".format(
            update.effective_user.first_name, context.bot.first_name,
            context.bot.id))
        return back_to_messages_menu(update, context)

    # def send_message_cancel(self, update, context):
    #     context.bot.delete_message(
    #         chat_id=update.callback_query.message.chat_id,
    #         message_id=update.callback_query.message.message_id)
    #     buttons = list()
    #     buttons.append(
    #         [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
    #                               callback_data="help_module(users)")])
    #     final_reply_markup = InlineKeyboardMarkup(buttons)
    #     context.bot.send_message(update.callback_query.message.chat_id,
    #                              context.bot.lang_dict["send_message_9"],
    #                              reply_markup=final_reply_markup)
    #     context.user_data.clear()
    #     return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)
        get_help(update, context)
        return ConversationHandler.END


class DeleteMessage(object):
    def delete_messages_menu(self, update, context):
        delete_messages(update, context, True)
        messages = users_messages_to_admin_table.find({"bot_id": context.bot.id,
                                                       "deleted": False})
        delete_buttons = []
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
                                         text=delete_messages_menu_str,
                                         reply_markup=InlineKeyboardMarkup(delete_buttons)))
            return ConversationHandler.END
        else:
            update.callback_query.answer(no_messages_blink)
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
                            callback_data="delete_messages/" + message_id)]]
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
            # else:
            #     users_messages_to_admin_table.delete_one(
            #         {"_id": ObjectId(message_id)})
            #     context.bot.send_message(
            #         chat_id=update.callback_query.message.chat_id,
            #         text=context.bot.lang_dict["delete_message_str_1"],
            #         reply_markup=reply_markup)
            #     return ConversationHandler.END
        else:
            update.callback_query.answer("There are no messages yet")
            return back_to_messages_menu(update, context)
            # context.bot.send_message(update.callback_query.message.chat_id,
            #                          context.bot.lang_dict["send_message_6"],
            #                          reply_markup=reply_markup)
            # return ConversationHandler.END

    def delete_message_double_check(self, update, context):
        context.bot.delete_message(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id)

        # buttons = [[InlineKeyboardButton(
        #                 text=context.bot.lang_dict["back_button"],
        #                 callback_data="back_to_inbox")]]
        # reply_markup = InlineKeyboardMarkup(buttons)

        if "all" in context.user_data["message_id"]:
            # delete all messages from the users
            # users_messages_to_admin_table.delete_many(
            #     {"bot_id": context.bot.id})
            users_messages_to_admin_table.update_many(
                {"bot_id": context.bot.id}, {"$set": {"deleted": True}})

        elif "week" in context.user_data["message_id"]:
            # delete all messages from the users for last week
            time_past = datetime.datetime.now() - datetime.timedelta(days=7)
            # users_messages_to_admin_table.delete_many(
            #     {"bot_id": context.bot.id, "timestamp": {'$gt': time_past}})
            users_messages_to_admin_table.update_many(
                {"bot_id": context.bot.id, "timestamp": {'$gt': time_past}},
                {"$set": {"deleted": True}})

        elif "month" in context.user_data["message_id"]:
            # delete all messages from the users for last month
            time_past = datetime.datetime.now() - datetime.timedelta(days=30)
            # users_messages_to_admin_table.delete_many(
            #     {"bot_id": context.bot.id, "timestamp": {'$gt': time_past}})
            users_messages_to_admin_table.update_many(
                {"bot_id": context.bot.id, "timestamp": {'$gt': time_past}},
                {"$set": {"deleted": True}})

        else:
            message_id = ObjectId(context.user_data["message_id"].split("/")[1])
            users_messages_to_admin_table.update_one(
                {"_id": message_id},
                {"$set": {"deleted": True}})
            update.callback_query.answer(success_delete_blink)
            return SeeMessageToAdmin().back_to_inbox(update, context)
        if not users_messages_to_admin_table.find(
                {"bot_id": context.bot.id, "deleted": False}).count():
            update.callback_query.answer(no_messages_blink)
            return back_to_messages_menu(update, context)
        else:
            return self.back_to_del_messages_menu(update, context)
        # context.bot.send_message(
        #     chat_id=update.callback_query.message.chat_id,
        #     text=context.bot.lang_dict["delete_message_str_1"],
        #     reply_markup=reply_markup)
        # return ConversationHandler.END

    def back_to_del_messages_menu(self, update, context):
        delete_messages(update, context, True)
        context.user_data.clear()
        return self.delete_messages_menu(update, context)


class SeeMessageToAdmin(object):
    def see_messages(self, update, context):
        delete_messages(update, context, True)
        # Set current page integer in user_data.
        if update.callback_query.data.startswith("inbox_pagination_"):
            context.user_data["page"] = int(
                update.callback_query.data.replace("inbox_pagination_", ""))
        if not context.user_data.get("page"):
            context.user_data["page"] = 1

        buttons = list()
        buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="messages_menu_back")])

        """delete_buttons = buttons[:]
        delete_buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["delete_button_str_all"],
                callback_data="delete_message_all")])
        delete_buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["delete_button_str_last_week"],
                callback_data="delete_message_week"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["delete_button_str_last_month"],
                 callback_data="delete_message_month")])"""

        messages = users_messages_to_admin_table.find(
            {"bot_id": context.bot.id, "deleted": False}).sort([["_id", -1]])

        if messages.count():
            pagination = Pagination(messages, context.user_data["page"])
            for message in pagination.content:
                message_buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text=context.bot.lang_dict["view_message_str"],
                        callback_data=f"view_message_{message['_id']}")]
                ])
                # Send message template.
                MessageTemplate(message, context).send(
                    update.effective_chat.id, reply_markup=message_buttons)

            pagination.send_keyboard(
                update, context,
                buttons=buttons, page_prefix="inbox_pagination",
                text=context.bot.lang_dict["message_count_str"].format(
                    messages.count()))
        else:
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["send_message_6"],
                reply_markup=InlineKeyboardMarkup(buttons))
        return ConversationHandler.END

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

        user_sender = users_table.find_one(
            {"user_id": context.user_data["message"]["user_id"],
             "bot_id": context.bot.id})

        # Send user message content
        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="<b>User Message:</b>",
                                     parse_mode=ParseMode.HTML))
        send_deleted_message_content(
            context,
            chat_id=update.effective_user.id,
            content=context.user_data["message"]["content"])
        # If answer exist show it
        if context.user_data["message"]["answer_content"]:
            context.user_data["to_delete"].append(
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="<b>Your Answer:</b>",
                                         parse_mode=ParseMode.HTML))
            send_deleted_message_content(
                context,
                chat_id=update.effective_user.id,
                content=context.user_data["message"]["answer_content"])

        buttons = [[]]
        if not context.user_data["message"]["answer_content"]:
            buttons[0].append(InlineKeyboardButton(
                text=context.bot.lang_dict["answer_button_str"],
                callback_data="answer_to_message/"
                              + str(context.user_data["message"]["_id"])))

        buttons[0].append(InlineKeyboardButton(
                 text=context.bot.lang_dict["delete_button_str"],
                 callback_data="delete_message/"
                               + str(context.user_data["message"]["_id"])))

        if context.user_data["message"]["anonim"]:
            if user_sender["anonim_messages_blocked"]:
                buttons.append([InlineKeyboardButton(
                    text=context.bot.lang_dict["unblock_messages_button"],
                    callback_data="unblock_anonim_messaging_"
                                  + str(user_sender["user_id"]))])
            else:
                buttons.append([InlineKeyboardButton(
                    text=context.bot.lang_dict["block_messages_button"],
                    callback_data="block_anonim_messaging_"
                                  + str(user_sender["user_id"]))])
        else:
            if user_sender["regular_messages_blocked"]:
                buttons.append([InlineKeyboardButton(
                    text=context.bot.lang_dict["unblock_messages_button"],
                    callback_data=f"from_inbox_unblock_messages_"
                                  + str(user_sender['user_id']))])
            else:
                buttons.append([InlineKeyboardButton(
                    text=context.bot.lang_dict["block_messages_button"],
                    callback_data=f"from_inbox_block_messages_"
                                  + str(user_sender['user_id']))])
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
            page = context.user_data["page"]
        except KeyError:
            context.user_data.clear()
            return get_help(update, context)

        context.user_data.clear()
        message = users_messages_to_admin_table.find_one({"_id": message["_id"]})
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
        page = context.user_data.get("page", 1)

        context.user_data.clear()
        context.user_data["page"] = page
        return self.see_messages(update, context)


class SubscriberOpenMessage(object):
    # TODO STRINGS
    def open(self, update, context):
        delete_messages(update, context)
        message_id = ObjectId(update.callback_query.data.split("/")[1])
        # update.effective_message.edit_reply_markup(
        #     reply_markup=InlineKeyboardMarkup([
        #         [InlineKeyboardButton(
        #             text="Show",
        #             callback_data=f"subscriber_open_message_false/{message_id}")]
        #     ]))
        message = users_messages_to_admin_table.find_one({"_id": message_id})
        if "open_delete" not in context.user_data:
            context.user_data["open_delete"] = list()
        # Send user message content
        context.user_data["open_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="<b>Your Message:</b>",
                                     parse_mode=ParseMode.HTML))
        send_deleted_message_content(context,
                                     chat_id=update.effective_user.id,
                                     content=message["content"],
                                     delete_key_name="open_delete")
        # Send admin answer content.
        # User can open message only if the answer exist
        context.user_data["open_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="<b>Answer:</b>",
                                     parse_mode=ParseMode.HTML))
        send_deleted_message_content(context,
                                     chat_id=update.effective_user.id,
                                     content=message["answer_content"],
                                     delete_key_name="open_delete")
        # Back button
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="Hide",
                callback_data="hide_answer")]])
        context.user_data["open_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=context.bot.lang_dict["back_text"],
                                     reply_markup=reply_markup))
        return ConversationHandler.END

    def hide_answer(self, update, context):
        for msg in context.user_data.get('open_delete', list()):
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
    entry_points=[
        CallbackQueryHandler(
            pattern="send_message_to_admin",
            callback=SendMessageToAdmin().send_message)],

    states={
        MESSAGE: [
            MessageHandler(
                filters=Filters.all,
                callback=SendMessageToAdmin().received_message)],
        # TOPIC: [MessageHandler(Filters.all, SendMessageToAdmin().send_topic), ]
        # SEND_ANONIM: [MessageHandler(Filters.all, SendMessageToAdmin().send_anonim), ]
    },

    fallbacks=[
        CallbackQueryHandler(
            pattern=r"send_message_finish",
            callback=SendMessageToAdmin().send_message_finish),
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
    entry_points=[
        CallbackQueryHandler(
            pattern="send_message_to_all_users",
            callback=SendMessageToUsers().send_message)],

    states={
        CHOOSE_CATEGORY: [
            MessageHandler(
                filters=Filters.all,
                callback=SendMessageToUsers().choose_question)],

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
            callback=back_to_messages_menu)
        # CallbackQueryHandler(
        #     pattern=r"help_module",
        #     callback=SendMessageToUsers().send_message_cancel),
        # CallbackQueryHandler(
        #     pattern=r"help_back",
        #     callback=SendMessageToUsers().send_message_cancel)
        ]
)


"""INBOX"""
SEE_MESSAGES_HANDLER = CallbackQueryHandler(
    pattern="^(inbox_message|inbox_pagination)",
    callback=SeeMessageToAdmin().see_messages)


"""DELETE 'WEEK' 'MONTH' 'ALL' MESSAGES"""
DELETE_MESSAGES_MENU_HANDLER = CallbackQueryHandler(
    pattern="del_messages_menu",
    callback=DeleteMessage().delete_messages_menu)

DELETE_MESSAGES_HANDLER = ConversationHandler(
    entry_points=[
        # CallbackQueryHandler(
        #     pattern="del_messages_menu",
        #     callback=DeleteMessage().delete_messages_menu)
        CallbackQueryHandler(
            pattern="delete_message",
            callback=DeleteMessage().delete_message)
    ],

    states={
        # DELETE_MESSAGES_MENU: [
        #     CallbackQueryHandler(
        #                 pattern="delete_message",
        #                 callback=DeleteMessage().delete_message)],

        DOUBLE_CHECK: [
            CallbackQueryHandler(
                pattern=r"delete_messages",
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

        # CallbackQueryHandler(
        #     pattern="help_back",
        #     callback=SendMessageToUsers().send_message_cancel)
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


# MESSAGE_CATEGORY_HANDLER = CallbackQueryHandler(pattern="show_message_categories",
#                                                 callback=MessageCategory().show_category)
# DELETE_MESSAGE_CATEGORY_HANDLER = CallbackQueryHandler(pattern="delete_category_",
#                                                        callback=DeleteMessageCategory().delete_category)
# ADD_MESSAGE_CATEGORY_HANDLER = ConversationHandler(
#     entry_points=[CallbackQueryHandler(pattern="add_message_category",
#                                        callback=AddMessageCategory().add_category)],
#
#     states={
#         TOPIC: [MessageHandler(Filters.all, AddMessageCategory().add_category_finish)],
#     },
#
#     fallbacks=[
#         CallbackQueryHandler(callback=SendMessageToUsers().back,
#                              pattern=r"help_module"),
#         CallbackQueryHandler(callback=SendMessageToUsers().back,
#                              pattern=r"help_back"),
#     ]
# )
