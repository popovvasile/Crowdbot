# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
# import random
from haikunator import Haikunator
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from database import donations_table, users_table
from helper_funcs.helper import get_help
from helper_funcs.pagination import Pagination, set_page_key
from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.misc import delete_messages, back_button, back_reply
from bson.objectid import ObjectId
from bson.errors import InvalidId
from validate_email import validate_email
from modules.users.users import get_obj, back_to_users_menu
from uuid import uuid4
from threading import Thread
from helper_funcs.mailer import SMTPMailer


# Make string for adding admins emails menu
def emails_layout(context, text) -> str:
    # result = text + '\n'
    if len(context.user_data['new_admins']) > 0:
        return f"{text} \nAdmins:\n" + \
               '\n'.join([i['email']
                          for i in context.user_data['new_admins']])
        # result += 'Admins:'
        # for i in context.user_data['new_admins']:
        #     result += f"\n{i['email']}"
    return text


class Admin:
    def __init__(self, obj: (ObjectId, dict, str)):
        obj = get_obj(users_table, obj)
        self._id = obj["_id"]
        self.name = obj.get("mention_markdown")
        self.email = obj.get("email")
        self.registered = obj["registered"]
        self.timestamp = obj.get("timestamp")

    def template(self, context):
        return string_dict(context.bot)["registered_admin_temp"].format(
            self.name, self.email, self.timestamp.strftime("%d, %b %Y, %H:%M")) \
            if self.registered else \
            string_dict(context.bot)["not_registered_admin_temp"].format(
                self.email)

    def send_template(self, update, context, text="", reply_markup=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(update.effective_chat.id,
                                     f"{self.template(context)}"
                                     f"\n\n{text}",
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=reply_markup
                                     if reply_markup else
                                     self.reply_markup(context)))

    def reply_markup(self, context):
        reply_markup = [
            [InlineKeyboardButton(string_dict(context)["delete_button_str"],
                                  callback_data=f"delete_admin/{self._id}")]]
        # if not self.registered:
        #     reply_markup[0].append(
        #         InlineKeyboardButton(
        #             string_dict(context)["resend_password_btn_str"],
        #             callback_data=f"resend_password/{self._id}"))
        return InlineKeyboardMarkup(reply_markup)

    def delete(self):
        users_table.delete_one({"_id": self._id})

    @staticmethod
    def get_all(context):
        return users_table.find({"bot_id": context.bot.id,
                                 "is_admin": True,
                                 "superuser": False}).sort([["_id", -1]])

    @staticmethod
    def add_new_admins(context):
        for admin in context.user_data["new_admins"]:
            admin["bot_id"] = context.bot.id
            admin["is_admin"] = True
            admin["registered"] = False
            admin["password"] = str(uuid4())[:10]
            admin["superuser"] = False
            if "user_id" in admin:
                users_table.update({"user_id": admin["user_id"],
                                    "bot_id": context.bot.id}, admin, upsert=True)
            elif "email" in admin:
                users_table.update({"email": admin["email"],
                                    "bot_id": context.bot.id}, admin, upsert=True)
            else:
                users_table.save(admin)
        Thread(target=SMTPMailer().send_registration_msgs,
               args=(context, context.user_data['new_admins'])).start()


class AdminHandler(object):
    # todo maybe add new admins right in telegram
    def admins(self, update, context):
        delete_messages(update, context)
        set_page_key(update, context, "admins")
        self.send_admins_layout(update, context)
        return ADMINS

    def send_admins_layout(self, update, context):
        all_admins = Admin.get_all(context)
        per_page = 5
        context.user_data['to_delete'].append(
            context.bot.send_message(
                update.callback_query.message.chat_id,
                string_dict(context)["admins_layout_title"].format(
                    all_admins.count()), ParseMode.MARKDOWN))
        if all_admins.count() == 0:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    string_dict(context)["no_admins_str"],
                    reply_markup=back_reply(context, "back_to_users_menu")))
        else:
            pagination = Pagination(context, per_page, all_admins)
            for admin in pagination.page_content():
                Admin(admin).send_template(update, context)
            pagination.send_keyboard(
                update, [[back_button(context, "back_to_users_menu")]])

    def confirm_delete_admin(self, update, context):
        delete_messages(update, context)
        context.user_data["admin"] = Admin(
            update.callback_query.data.split("/")[1])
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(string_dict(context)["delete_button_str"],
                                  callback_data="finish_delete_admin")],
            [back_button(context, "back_to_admin_list")]
        ])
        context.user_data["admin"].send_template(
            update, context, reply_markup=reply_markup,
            text=string_dict(context)["confirm_delete_admin_str"])
        return CONFIRM_DELETE_ADMIN

    def finish_delete_admin(self, update, context):
        delete_messages(update, context)
        context.user_data["admin"].delete()
        update.callback_query.answer(
            string_dict(context)["admin_deleted_blink"])
        return self.back_to_admins_list(update, context)

    def start_add_admins(self, update, context):
        delete_messages(update, context)
        context.user_data["new_admins"] = list()
        context.user_data['to_delete'].append(
            context.bot.send_message(
                update.effective_chat.id,
                string_dict(context)["enter_new_admin_email"],
                reply_markup=back_reply(context, "back_to_users_menu")))
        return ADD_ADMINS

    def continue_add_admins(self, update, context):
        delete_messages(update, context)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(string_dict(context)["add_button"],
                                  callback_data="finish_add_admins"),
             back_button(context, "back_to_users_menu")]
            if context.user_data["new_admins"]
            else [back_button(context, "back_to_users_menu")]])

        # https://pypi.org/project/validate_email/
        is_valid = validate_email(update.message.text)
        if is_valid:
            if not any(admin["email"] == update.message.text
                       for admin in context.user_data["new_admins"]) \
                    and not users_table.find_one({"bot_id": context.bot.id,
                                                  "is_admin": True,
                                                  "email": update.message.text}):
                context.user_data["new_admins"].append(
                    {"email": update.message.text})
                kb = InlineKeyboardMarkup([
                    [InlineKeyboardButton(string_dict(context)["add_button"],
                                          callback_data="finish_add_admins"),
                     back_button(context, "back_to_users_menu")]])
                text = emails_layout(
                    context, string_dict(context)["next_email_request"])
                context.user_data["to_delete"].append(
                    context.bot.send_message(update.effective_chat.id,
                                             text, reply_markup=kb,
                                             parse_mode=ParseMode.MARKDOWN))
            else:
                text = emails_layout(
                    context,
                    string_dict(context)["add_already_exist_admin"].format(
                        update.message.text) +
                    string_dict(context)["next_email_request"])

                context.user_data["to_delete"].append(
                    context.bot.send_message(update.effective_chat.id,
                                             text, reply_markup=reply_markup,
                                             parse_mode=ParseMode.MARKDOWN))
        else:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    emails_layout(context, string_dict(context)["wrong_email"]),
                    reply_markup=reply_markup))
        return ADD_ADMINS

    def finish_add_admins(self, update, context):
        delete_messages(update, context)
        Admin.add_new_admins(context)
        update.callback_query.answer(string_dict(context)["admins_added_blink"])
        return back_to_users_menu(update, context)

    def back_to_admins_list(self, update, context):
        delete_messages(update, context)
        page = context.user_data.get("page")
        context.user_data.clear()
        context.user_data["page"] = page
        return self.admins(update, context)


ADMINS, CONFIRM_DELETE_ADMIN, ADD_ADMINS = range(3)


ADMINS_LIST_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern="admins",
                                       callback=AdminHandler().admins)],

    states={
        ADMINS: [CallbackQueryHandler(pattern="^[0-9]+$",
                                      callback=AdminHandler().admins),
                 CallbackQueryHandler(
                     pattern=r"delete_admin",
                     callback=AdminHandler().confirm_delete_admin)],

        CONFIRM_DELETE_ADMIN: [
            CallbackQueryHandler(pattern=r"finish_delete_admin",
                                 callback=AdminHandler().finish_delete_admin)],

        ADD_ADMINS: [
            MessageHandler(callback=AdminHandler().continue_add_admins,
                           filters=Filters.text),
            CallbackQueryHandler(AdminHandler().finish_add_admins,
                                 pattern=r"finish_add_admins")]
    },

    fallbacks=[
        CallbackQueryHandler(pattern=r"back_to_users_menu",
                             callback=back_to_users_menu),
        CallbackQueryHandler(pattern=r"back_to_admin_list",
                             callback=AdminHandler().back_to_admins_list)
        # CallbackQueryHandler(pattern=r"help_back",
        #                      callback=UsersHandler()),
    ]
)

ADD_ADMIN_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(pattern="start_add_admins",
                             callback=AdminHandler().start_add_admins)],

    states={
        ADD_ADMINS: [
            MessageHandler(callback=AdminHandler().continue_add_admins,
                           filters=Filters.text),
            CallbackQueryHandler(AdminHandler().finish_add_admins,
                                 pattern=r"finish_add_admins")]
    },

    fallbacks=[
        CallbackQueryHandler(pattern=r"back_to_users_menu",
                             callback=back_to_users_menu),
        CallbackQueryHandler(pattern=r"back_to_admin_list",
                             callback=AdminHandler().back_to_admins_list)
        # CallbackQueryHandler(pattern=r"help_back",
        #                      callback=UsersHandler()),
    ]
)
