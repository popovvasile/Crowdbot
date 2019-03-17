import importlib
import re
from math import ceil
from typing import List, Dict
from telegram import ParseMode, InlineKeyboardMarkup, Bot, Update, InlineKeyboardButton
from telegram.ext import run_async

from database import custom_buttons_table, chats_table

HELP_STRINGS = """
Hey there! My name is {}.
I'm an organization management bot with a few fun extras! Have a look at the following for an idea of some of \
the things I can help you with.

/help: to PM's you this message.
"""

ALL_MODULES = ['add_menu_buttons', 'answer_surveys', 'create_donation', 'create_survey',
               'donations_edit_delete_results', 'pay_donation', 'report_chatbot_scam', 'send_message']
ADMIN_HELPABLE = {'add_menu_buttons': "",
                  'answer_surveys': "",
                  'pay_donation': "",
                  'send_message': ""}

VISITOR_HELPABLE = {'pay_donation', 'report_chatbot_scam', 'send_message'}


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n: int, module_dict: Dict, prefix, bot_id, chat=None) -> List:
    buttons = [EqInlineKeyboardButton(button["button"],
                                      callback_data="button_{}".format(button["button"].replace(" ", "").lower()))
               for button in custom_buttons_table.find({"bot_id": bot_id})]

    if not chat:
        modules = [
            EqInlineKeyboardButton(x, callback_data="{}_module({})".format(prefix, x)) for x in module_dict
        ] + buttons
    else:
        modules = [
            EqInlineKeyboardButton(x, callback_data="{}_module({},{})".format(prefix, chat, x)) for x in module_dict
        ]

    pairs = list(zip(modules[::2], modules[1::2]))

    if len(modules) % 2 == 1:
        pairs.append((modules[-1],))

    max_num_pages = ceil(len(pairs) / 7)
    modulo_page = page_n % max_num_pages

    # can only have a certain amount of buttons side by side
    if len(pairs) > 7:
        pairs = pairs[modulo_page * 7:7 * (modulo_page + 1)] + [
            (EqInlineKeyboardButton("<", callback_data="{}_prev({})".format(prefix, modulo_page)),
             EqInlineKeyboardButton(">", callback_data="{}_next({})".format(prefix, modulo_page)))]

    return pairs


def if_admin(update, bot):
    # if update.message:
    #     user_id = update.message.from_user.id
    # else:
    #     user_id = update.callback_query.from_user.id
    # superuser = chatbots_table.find_one({"bot_id": bot.id})["superuser"]
    # if user_id == superuser:
    #     return True
    # admin_chat = users_table.find_one({'user_id': user_id, "bot_id": bot.id})
    # if admin_chat is not None:
    #     if admin_chat["registered"] and admin_chat["is_admin"]:
    #         return True
    #     else:
    #         return False
    # else:
    #     return False
    return True


def register_chat(bot, update):
    chat_id = update.effective_chat.id
    chat_name = update.effective_user.full_name
    bot_id = bot.id
    user_id = update.effective_user.id
    chats_table.update({"bot_id": bot.id, "chat_id": chat_id},
                       {"bot_id": bot_id, "chat_id": chat_id,
                        "name": chat_name, "user_id": user_id, "tag": "#all"},
                       upsert=True)


@run_async
def get_help(bot: Bot, update: Update):
    register_chat(bot, update)
    chat = update.effective_chat

    if if_admin(bot=bot, update=update):
        send_admin_help(bot, chat.id, HELP_STRINGS.format(bot.first_name))
    else:
        send_visitor_help(bot, chat.id, HELP_STRINGS.format(bot.first_name))


def send_admin_help(bot, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, ADMIN_HELPABLE, "help", bot.id))
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=keyboard)


def send_visitor_help(bot, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, VISITOR_HELPABLE, "help", bot.id))
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=keyboard)
