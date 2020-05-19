#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from telegram import InlineKeyboardMarkup

from database import chatbots_table


def payments_checker(bot):
    while True:
        chatbots = chatbots_table.find({"active": True})
        for chatbot in chatbots:
            created_at = chatbot["creation_timestamp"]
            if created_at + datetime.timedelta(days=14) < chatbot["premium_payments"][0]:
                pass
                # bot.send_message(
                #     chat_id=update.effective_chat.id,
                #     text=get_str(update, context, 'WRONG_TOKEN'),
                #     reply_markup=InlineKeyboardMarkup(buttons)))