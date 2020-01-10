import logging
from typing import List, Dict

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from telegram.error import TelegramError
from babel.dates import format_datetime
from bson.objectid import ObjectId

from database import custom_buttons_table
from database import chatbots_table


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
            if type(msg) is list:
                for ms in msg:
                    try:
                        if ms.message_id != update.effective_message.message_id:
                            context.bot.delete_message(
                                update.effective_chat.id, ms.message_id)
                    except TelegramError:
                        continue
            else:
                try:
                    if msg.message_id != update.effective_message.message_id:
                        context.bot.delete_message(
                            update.effective_chat.id, msg.message_id)
                except TelegramError:
                    continue
        context.user_data['to_delete'] = list()
    else:
        context.user_data['to_delete'] = list()


# todo OVERKILL
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
    if obj is None:
        return {}
    if type(obj) is dict:
        return obj
    elif type(obj) is ObjectId:
        return table.find_one({"_id": obj})
    elif type(obj) is str:
        return table.find_one({"_id": ObjectId(obj)})
    else:
        raise Exception


def user_mention(username, string):
    """Users that have blocked the bot or never start it
    can't be shown as the url mention using "tg://user?id=".

    But can be showing using "https://t.me/"
    but in this case we use username which must exist and be correct
    """
    # return f'<a href="tg://user?id={user_id}">{string}</a>'
    return f'<a href="https://t.me/{username}">{string}</a>'


class EqInlineKeyboardButton(InlineKeyboardButton):
    def __eq__(self, other):
        return self.text == other.text

    def __lt__(self, other):
        return self.text < other.text

    def __gt__(self, other):
        return self.text > other.text


def paginate_modules(module_dict: Dict, prefix, bot_id, chat=None) -> List:
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
    pairs = modules

    return pairs


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
