from math import ceil
from typing import List, Dict

from telegram import (InlineKeyboardButton, Bot, ParseMode,
                      InlineKeyboardMarkup)
from telegram.ext import CallbackContext
from telegram.error import TelegramError
import logging
from helper_funcs.lang_strings.strings import string_dict, string_dict_dict
# from settings import LOAD, NO_LOAD, LOGGER
from database import custom_buttons_table
from babel.dates import format_datetime
from database import chatbots_table
from bson.objectid import ObjectId


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)
LOAD = []
NO_LOAD = ['translation', 'rss']


def delete_messages(update, context, message_from_update=False):
    if message_from_update:
        try:
            context.bot.delete_message(update.effective_chat.id,
                                       update.effective_message.message_id)
        except TelegramError:
            pass
    if 'to_delete' in context.user_data:
        for msg in context.user_data['to_delete']:
            try:
                if msg.message_id != update.effective_message.message_id:
                    context.bot.delete_message(
                        update.effective_chat.id, msg.message_id)
            except TelegramError:
                continue
        context.user_data['to_delete'] = list()
    else:
        context.user_data['to_delete'] = list()


def back_button(context, callback_data: str):
    return InlineKeyboardButton(
        string_dict(context.bot)["back_button"], callback_data=callback_data)


def back_reply(context, callback_data: str):
    return InlineKeyboardMarkup([[back_button(context, callback_data)]])


# http://babel.pocoo.org/en/latest/dates.html
def lang_timestamp(bot_lang: (CallbackContext, str), timestamp,
                   pattern="d, MMM yyyy, hh:mm"):
    if timestamp is None:
        return ""
    lang_keys = {"ENG": "en", "RUS": "ru"}
    if isinstance(bot_lang, CallbackContext):
        bot_lang = chatbots_table.find_one({"bot_id": bot_lang.bot.id})["lang"]
    return format_datetime(timestamp, pattern, locale=lang_keys[bot_lang])


# May raise Exception and bson.errors.InvalidId
def get_obj(table, obj: (ObjectId, dict, str)):
    if type(obj) is dict:
        return obj
    elif type(obj) is ObjectId:
        return table.find_one({"_id": obj})
    elif type(obj) is str:
        return table.find_one({"_id": ObjectId(obj)})
    else:
        raise Exception


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(page_n: int, module_dict: Dict, prefix, bot_id, chat=None) -> List:
    buttons = [[EqInlineKeyboardButton(button["button"],
                                      callback_data="button_{}".format(button["button"].replace(" ", "").lower()))]
               for button in custom_buttons_table.find({"bot_id": bot_id, "link_button": False})]
    buttons += [[EqInlineKeyboardButton(text=button["button"],
                url=button["link"])]
                for button in custom_buttons_table.find({"bot_id": bot_id, "link_button": True})]

    if not chat:
        modules = [
                      [EqInlineKeyboardButton(x, callback_data="{}_module({})".format(prefix, module_dict[x]))]
                      for x in module_dict
                  ] + buttons
    else:
        modules = [
            [EqInlineKeyboardButton(x, callback_data="{}_module({},{})".format(prefix, chat, module_dict[x]))]
            for x in module_dict
        ]
    # pairs = list(zip(modules[::2], modules[1::2]))
    #
    # if len(modules) % 2 == 1:
    #     pairs.append((modules[-1],))
    #
    # max_num_pages = ceil(len(pairs) / 7)
    # modulo_page = page_n % max_num_pages
    #
    # # can only have a certain amount of buttons side by side
    # if len(pairs) > 7:
    #     pairs = pairs[modulo_page * 7:7 * (modulo_page + 1)] + [
    #         (EqInlineKeyboardButton("<", callback_data="{}_prev({})".format(prefix, modulo_page)),
    #          EqInlineKeyboardButton(">", callback_data="{}_next({})".format(prefix, modulo_page)))]
    pairs = modules

    return pairs


def send_to_list(update, send_to: list, message: str, markdown=False, html=False) -> None:
    if html and markdown:
        raise Exception("Can only send with either markdown or HTML!")
    for user_id in set(send_to):
        try:
            if markdown:
                context.bot.send_message(user_id, message, parse_mode=ParseMode.MARKDOWN)
            elif html:
                context.bot.send_message(user_id, message, parse_mode=ParseMode.HTML)
            else:
                context.bot.send_message(user_id, message)
        except TelegramError:
            pass  # ignore users who fail


def build_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn.same_line and keyb:
            keyb[-1].append(InlineKeyboardButton(btn.name, url=btn.url))
        else:
            keyb.append([InlineKeyboardButton(btn.name, url=btn.url)])

    return keyb


def revert_buttons(buttons):
    res = ""
    for btn in buttons:
        if btn.same_line:
            res += "\n[{}](buttonurl://{}:same)".format(btn.name, btn.url)
        else:
            res += "\n[{}](buttonurl://{})".format(btn.name, btn.url)

    return res


def is_module_loaded(name):
    return (not LOAD or name in LOAD) and name not in NO_LOAD
