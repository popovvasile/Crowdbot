#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram.error import Unauthorized

from database import users_table


def update_user_unsubs(context):
    users_list = users_table.find({"bot_id": context.bot.id})
    """Update user full_name, username and unsubscribed status.
    Used for showing users list, admins, users in shop order"""
    for user in users_list:
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
                                   {"$set": new_user_fields})