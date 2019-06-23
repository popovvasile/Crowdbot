from math import ceil
from typing import List, Dict
from telegram import ParseMode, InlineKeyboardMarkup, Bot, Update, InlineKeyboardButton
from telegram.ext import run_async

from database import custom_buttons_table, chats_table, chatbots_table, users_table, user_mode_table
from modules.helper_funcs.lang_strings.help_strings import helpable_dict
from modules.helper_funcs.lang_strings.strings import string_dict

HELP_STRINGS = """
{}
"""


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
        modules = sorted([
            EqInlineKeyboardButton(x, callback_data="{}_module({})".format(prefix, module_dict[x])) for x in module_dict
        ]) + buttons
    else:
        modules = sorted([
            EqInlineKeyboardButton(x, callback_data="{}_module({},{})".format(prefix, chat, module_dict[x])) for x in
            module_dict
        ])

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
    if update.message:
        user_id = update.message.from_user.id
    else:
        user_id = update.callback_query.from_user.id
    superuser = chatbots_table.find_one({"bot_id": bot.id})["superuser"]
    if user_id == superuser:
        return True
    admin_chat = users_table.find_one({'user_id': user_id, "bot_id": bot.id})
    if admin_chat is not None:
        if admin_chat["registered"] and admin_chat["is_admin"]:
            return True
        else:
            return False
    else:
        return False


def register_chat(bot, update):
    chat_id = update.effective_chat.id
    chat_name = update.effective_user.full_name
    bot_id = bot.id
    user_id = update.effective_user.id
    chats_table.update({"bot_id": bot.id, "chat_id": chat_id},
                       {"bot_id": bot_id, "chat_id": chat_id,
                        "name": chat_name, "user_id": user_id, "tag": "#all"},
                       upsert=True)


def get_help(bot: Bot, update: Update):
    chatbot = chatbots_table.find_one({"bot_id": bot.id})
    register_chat(bot, update)
    chat = update.effective_chat
    current_user_mode = user_mode_table.find_one({"bot_id": bot.id,
                                                  "user_id": update.effective_user.id})
    if chatbot:
        if 'welcomeMessage' in chatbot:
            welcome_message = chatbot['welcomeMessage']
        else:
            welcome_message = "Hello"
    else:
        welcome_message = "Hello"
    if if_admin(bot=bot, update=update):
        if "user_mode" in current_user_mode:
            if current_user_mode.get("user_mode") is True:
                send_admin_user_mode(bot, chat.id, HELP_STRINGS.format(welcome_message))
            else:
                send_admin_help(bot, chat.id, HELP_STRINGS.format(welcome_message))
        else:
            user_mode_table.insert({"bot_id": bot.id,
                                    "user_id": update.effective_user.id,
                                    "user_mode": False})
            send_admin_help(bot, chat.id, HELP_STRINGS.format(welcome_message))
    else:
        send_visitor_help(bot, chat.id, HELP_STRINGS.format(welcome_message))


# do not async
def send_admin_help(bot, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, helpable_dict(bot)["ADMIN_HELPABLE"], "help", bot.id))
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=keyboard)


def send_visitor_help(bot, chat_id, text, keyboard=None):
    buttons = [InlineKeyboardButton(string_dict(bot)["user_messages_str"], callback_data="send_message_to_admin"),
               InlineKeyboardButton(string_dict(bot)["pay_donation_mode_str"], callback_data='pay_donation')]
    buttons = buttons + [InlineKeyboardButton(button["button"],
                                     callback_data="button_{}".format(button["button"].replace(" ", "").lower()))
                for button in custom_buttons_table.find({"bot_id": bot.id})]
    pairs = list(zip(buttons[::2], buttons[1::2]))

    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=InlineKeyboardMarkup(
                         pairs
                     ))


def send_admin_user_mode(bot, chat_id, text, keyboard=None):
    buttons = [InlineKeyboardButton(string_dict(bot)["user_messages_str"], callback_data="send_message_to_admin"),
               InlineKeyboardButton(string_dict(bot)["pay_donation_mode_str"], callback_data='pay_donation')]
    buttons = buttons + [InlineKeyboardButton(button["button"],
                                     callback_data="button_{}".format(button["button"].replace(" ", "").lower()))
                for button in custom_buttons_table.find({"bot_id": bot.id})]
    buttons = buttons + [InlineKeyboardButton(text="ADMIN MODE", callback_data="turn_user_mode_off")]
    pairs = list(zip(buttons[::2], buttons[1::2]))

    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=InlineKeyboardMarkup(
                         pairs
                     ))
