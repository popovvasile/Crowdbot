#!/usr/bin/env python
# -*- coding: utf-8 -*-
# TODO for Admins only. to add tags for themselves, add onboarding and info for users + add settings button
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging

# Enable logging
from database import chatbots_table

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

reply_keyboard = [['Rules', 'Contacts'],
                  ['Useful links', 'Something else...'],
                  ['Done']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


__mod_name__ = "Info"

__admin_help__ = """
 Information about your chatbot.
 
 To change it, click /change_org_info
"""

# __admin_keyboard__ = [["/change_org_info"]]

# __user_help__ = """
#     Click:
#     - /org_info
# """
# __user_keyboard__ = [["/org_info"]]
#
#
__visitor_help__ = """
    Information about us
"""
# __visitor_keyboard__ = [["/org_info"]]


class BotInfo(object):
    @staticmethod
    def facts_to_str(user_data):
        facts = list()

        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @staticmethod
    def start(bot, update):
        update.message.reply_text(
            "Let's add some useful information for your users."
            " First, choose what information do you want to add to the bot".format(bot.name),
            reply_markup=markup)

        return CHOOSING

    @staticmethod
    def regular_choice(bot, update, user_data):
        text = update.message.text
        user_data['choice'] = text
        update.message.reply_text(
            '{}? Perfect! Now, send me the text that will be displayed to the users'.format(text))

        return TYPING_REPLY

    @staticmethod
    def custom_choice(bot, update):
        update.message.reply_text('Alright, please send me the category first, '
                                  'for example "About us"')

        return TYPING_CHOICE

    @staticmethod
    def received_information(bot, update, user_data):
        text = update.message.text
        category = user_data['choice']
        user_data[category] = text
        del user_data['choice']

        update.message.reply_text("Neat! Just so you know, this is what you already told me:\n"
                                  "{}\n"
                                  "You can tell me more, or change your opinion on something.".format(
                                    BotInfo().facts_to_str(user_data)), reply_markup=markup)

        return CHOOSING

    @staticmethod
    def done(bot, update, user_data):  # TODO you can't use replace here, you must information here
        if 'choice' in user_data:
            del user_data['choice']

        update.message.reply_text("Now I can tell to your users the following:"
                                  "{}"
                                  .format(BotInfo().facts_to_str(user_data)))
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        chatbot["chatbot_info"] = user_data
        chatbots_table.replace_one({"bot_id": bot.id}, chatbot)
        user_data.clear()
        # get_help(bot=bot, update=update)

        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)


BOT_INFO_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('change_org_info', BotInfo().start)],
    states={
        CHOOSING: [RegexHandler('^(Rules|Contacts|Useful links)$',
                                BotInfo().regular_choice,
                                pass_user_data=True),
                   RegexHandler('^Something else...$',
                                BotInfo().custom_choice),
                   ],

        TYPING_CHOICE: [MessageHandler(Filters.text,
                                       BotInfo().regular_choice,
                                       pass_user_data=True),
                        ],

        TYPING_REPLY: [MessageHandler(Filters.text,
                                      BotInfo().received_information,
                                      pass_user_data=True),
                       ],
    },

    fallbacks=[RegexHandler('^Done$', BotInfo().done, pass_user_data=True),
               RegexHandler('^done$', BotInfo().done, pass_user_data=True),
               CommandHandler('done', BotInfo().done, pass_user_data=True)]
)

