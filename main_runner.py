import re
import logging
import telegram.ext as tg
import importlib
from typing import Optional

from telegram import Chat, Update, Bot, ReplyKeyboardMarkup
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, ChatMigrated, TelegramError
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, \
    RegexHandler
from telegram.ext.dispatcher import run_async
from database import users_table, chatbots_table, custom_buttons_table
from modules import ALL_MODULES
from modules.add_menu_buttons import BUTTON_ADD_HANDLER, DELETE_BUTTON_HANDLER
from modules.old_scripts.answer_payment import EXECUTE_PAYMENT_HANDLER
from modules.answer_surveys import ANSWER_SURVEY_HANDLER
from modules.bot_info import BOT_INFO_HANDLER
from modules.create_donation import CREATE_DONATION_HANDLER
from modules.old_scripts.create_payment import CREATE_PAYMENT_HANDLER
from modules.create_survey import DELETE_SURVEYS_HANDLER, SHOW_SURVEYS_HANDLER, SEND_SURVEYS_HANDLER, \
    CREATE_SURVEY_HANDLER
from modules.helper_funcs.auth import initiate_chat_id, if_admin
from modules.helper_funcs.misc import paginate_modules
from modules.pay_donation import DONATE_HANDLER
from modules.payment_edit_delete_results import CHANGE_PAYMENT_TOKEN, EDIT_PAYMENT_HANDLER
from modules.polls import POLL_HANDLER, SEND_POLLS_HANDLER, BUTTON_HANDLER, DELETE_POLLS_HANDLER, BOTS_POLLS_HANDLER
from modules.tags import ADD_TAGS_HANDLER, RM_TAGS_HANDLER, TAGLIST_HANDLER, SEND_BY_HANSHTAG_HANDLER, \
    MYTAGLIST_HANDLER, RM_CHAT_TAGS_HANDLER
from modules.users import USER_AUTHENTICATION_HANDLER, USER_REMOVE_HANDLER, SHOW_USERS_HANDLER

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)


def test():
    print("hi")


PM_START_TEXT = """
Hey there! My name is {}.
I'm a modular group management bot with a few fun extras! Have a look at the following for an idea of some of \
the things I can help you with.

/help: to PM's you this message.
"""

HELP_STRINGS = """
Hey there! My name is {}.
I'm an organization management bot with a few fun extras! Have a look at the following for an idea of some of \
the things I can help you with.

/help: to PM's you this message.
"""

# DONATE_STRING = """"""
IMPORTED = {}
MIGRATEABLE = []
ADMIN_HELPABLE = {}
USER_HELPABLE = {}
VISITOR_HELPABLE = {}

STATS = []
USER_INFO = []
DATA_IMPORT = []
DATA_EXPORT = []

CHAT_SETTINGS = {}
USER_SETTINGS = {}

GDPR = []

for module_name in ALL_MODULES:
    imported_module = importlib.import_module("modules." + module_name)
    if not hasattr(imported_module, "__mod_name__"):
        imported_module.__mod_name__ = imported_module.__name__
    if not imported_module.__mod_name__.lower() in IMPORTED:
        IMPORTED[imported_module.__mod_name__.lower()] = imported_module
    else:
        raise Exception("Can't have two modules with the same name! Please change one")

    if hasattr(imported_module, "__admin_help__") and imported_module.__admin_help__:
        ADMIN_HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__user_help__") and imported_module.__user_help__:
        USER_HELPABLE[imported_module.__mod_name__.lower()] = imported_module

    if hasattr(imported_module, "__visitor_help__") and imported_module.__visitor_help__:
        VISITOR_HELPABLE[imported_module.__mod_name__.lower()] = imported_module


# do not async
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


# for test purposes
def error_callback(bot, update, error):
    try:
        raise error
    except Unauthorized:
        print(error)
        # remove update.message.chat_id from conversation list
    except BadRequest:
        print("BadRequest caught")
        print(error)

        # handle malformed requests - read more below!
    except TimedOut as err:
        print("TimedOut")
        print(err)
        # handle slow connection problems
    except NetworkError:
        print("NetworkError")
        # handle other connection problems
    except ChatMigrated as err:
        print("ChatMigrated")
        print(err)
        # the chat_id of a group has changed, use e.new_chat_id instead
    except TelegramError:
        print(error)
        # handle all other telegram related errors


@run_async
def return_bot_info(bot: Bot, update: Update):
    query = update.callback_query
    bot.answer_callback_query(query.id)
    try:
        chatbot_info = chatbots_table.find_one({"bot_id": bot.id})["chatbot_info"]
        info_name = query.data.replace("bot_info_", "")
        information_text = chatbot_info[info_name]
        buttons = [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
        query.message.reply_text(text=info_name + ": " + information_text,
                                 reply_markup=InlineKeyboardMarkup(
                                     buttons))
        query.message.delete()
    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in help buttons. %s", str(query.data))


@run_async
def button_handler(bot: Bot, update: Update):
    query = update.callback_query
    button_callback_data = query.data
    bot.answer_callback_query(query.id)
    print(button_callback_data)
    try:
        button_info = custom_buttons_table.find_one(
            {"bot_id": bot.id, "button_lower": button_callback_data.replace("button_", "")}
        )["button_lower"]
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back to main menu", callback_data="help_back")])
        query.message.reply_text(text=button_info,
                                 reply_markup=InlineKeyboardMarkup(
                                     buttons))
    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in help buttons. %s", str(query.data))


@run_async
def help_button(bot: Bot, update: Update):
    chat_id = update.effective_chat.id

    if if_admin(update=update, bot=bot):
        HELPABLE = ADMIN_HELPABLE
    else:
        HELPABLE = VISITOR_HELPABLE
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    try:
        if mod_match:
            module = mod_match.group(1)
            if HELPABLE[module].__mod_name__ == "Info":
                chatbot_infos = chatbots_table.find_one({"bot_id": bot.id})["chatbot_info"]
                buttons = []
                for info in chatbot_infos:
                    buttons.append([InlineKeyboardButton(text=info, callback_data="bot_info_" + info)])
                buttons.append([InlineKeyboardButton(text="Back", callback_data="help_back")])
                query.message.reply_text(text="Here you can see the information about us",
                                         reply_markup=InlineKeyboardMarkup(
                                             buttons))
            else:
                if if_admin(update=update, bot=bot):
                    text = "{}:\n".format(HELPABLE[module].__mod_name__) \
                           + HELPABLE[module].__admin_help__
                    commands_keyboard = HELPABLE[module].__admin_keyboard__
                else:
                    text = "{}:\n".format(HELPABLE[module].__mod_name__) \
                           + HELPABLE[module].__visitor_help__
                    commands_keyboard = HELPABLE[module].__visitor_keyboard__
                query.message.reply_text(text=text,
                                         reply_markup=InlineKeyboardMarkup(
                                             [[InlineKeyboardButton(text="Back", callback_data="help_back")]]))
                bot.send_message(chat_id=chat_id, text="Choose your action",
                                 reply_markup=ReplyKeyboardMarkup(commands_keyboard,
                                                                  one_time_keyboard=True))

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.reply_text(HELP_STRINGS.format(bot.first_name),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(curr_page - 1, HELPABLE, "help", bot.id)))
        elif next_match:
            next_page = int(next_match.group(1))
            query.message.reply_text(HELP_STRINGS.format(bot.first_name),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(next_page + 1, HELPABLE, "help", bot.id)))

        elif back_match:
            query.message.reply_text(text=HELP_STRINGS.format(bot.first_name),
                                     reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", bot.id)))

        # ensure no spinny white circle
        bot.answer_callback_query(query.id)
        query.message.delete()
        return ConversationHandler.END

    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in help buttons. %s", str(query.data))


@run_async
def get_help(bot: Bot, update: Update):
    chat = update.effective_chat  # type: Optional[Chat]

    if if_admin(bot=bot, update=update):
        send_admin_help(bot, chat.id, HELP_STRINGS.format(bot.first_name))
    else:
        send_visitor_help(bot, chat.id, HELP_STRINGS.format(bot.first_name))


TYPING_EMAIL, TYPING_PASS, TYPING_TAGS = range(3)


class WelcomeBot(object):
    @staticmethod
    def start(bot, update):

        chat_id, txt = initiate_chat_id(update)
        user_id = update.message.from_user.id
        if if_admin(update, bot):
            get_help(bot=bot, update=update)

            bot.send_message(chat_id, "As a first step, let's add some information about this chatbot.\n"
                                      "To do this, click the command /bot_info".format(bot.name),
                             reply_markup=InlineKeyboardMarkup(
                                 inline_keyboard=[[InlineKeyboardButton(text="Back", callback_data="help_back")]])
                             )
        else:
            users_table.save({'bot_id': bot.id,
                              "chat_id": chat_id,
                              "user_id": user_id,
                              "username": update.message.from_user.username,
                              "full_name": update.message.from_user.full_name,
                              'registered': False,
                              "pending": False,
                              "is_admin": False,
                              "tags": ["#all", "#user"]
                              })
            get_help(bot=bot, update=update)
        return ConversationHandler.END

    @staticmethod
    def cancel(bot, update):
        update.message.reply_text("Until next time!")
        return ConversationHandler.END


def main(token):
    updater = tg.Updater(token, workers=8)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler("start", WelcomeBot().start)
    help_handler = CommandHandler("help", get_help)
    rex_help_handler = RegexHandler(r"^help$", get_help)
    rex_help_handler2 = RegexHandler(r"^Help$", get_help)

    custom_button_callback_handler = CallbackQueryHandler(button_handler, pattern=r"button_")
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_")
    info_callback_handler = CallbackQueryHandler(return_bot_info, pattern=r"bot_info_")
    dispatcher.add_handler(custom_button_callback_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(info_callback_handler)
    dispatcher.add_handler(rex_help_handler)
    dispatcher.add_handler(rex_help_handler2)

    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_error_handler(error_callback)

    # POLLS
    dispatcher.add_handler(POLL_HANDLER)
    dispatcher.add_handler(SEND_POLLS_HANDLER)
    dispatcher.add_handler(BUTTON_HANDLER)
    dispatcher.add_handler(DELETE_POLLS_HANDLER)
    dispatcher.add_handler(BOTS_POLLS_HANDLER)

    # ADD_COMMANDS
    dispatcher.add_handler(BUTTON_ADD_HANDLER)
    dispatcher.add_handler(DELETE_BUTTON_HANDLER)
    # PAYMENTS
    dispatcher.add_handler(CREATE_PAYMENT_HANDLER)
    dispatcher.add_handler(EXECUTE_PAYMENT_HANDLER)
    dispatcher.add_handler(CHANGE_PAYMENT_TOKEN)
    dispatcher.add_handler(EDIT_PAYMENT_HANDLER)
    # DONATIONS
    dispatcher.add_handler(CREATE_DONATION_HANDLER)
    dispatcher.add_handler(DONATE_HANDLER)
    # SURVEYS
    # dispatcher.add_handler(MY_SURVEYS_LIST)
    dispatcher.add_handler(ANSWER_SURVEY_HANDLER)
    dispatcher.add_handler(SHOW_SURVEYS_HANDLER)
    dispatcher.add_handler(SEND_SURVEYS_HANDLER)
    dispatcher.add_handler(CREATE_SURVEY_HANDLER)
    dispatcher.add_handler(DELETE_SURVEYS_HANDLER)
    # BOT_IF
    dispatcher.add_handler(BOT_INFO_HANDLER)
    # TAGS
    dispatcher.add_handler(ADD_TAGS_HANDLER)
    dispatcher.add_handler(TAGLIST_HANDLER)
    dispatcher.add_handler(RM_TAGS_HANDLER)
    dispatcher.add_handler(MYTAGLIST_HANDLER)
    dispatcher.add_handler(SEND_BY_HANSHTAG_HANDLER)
    dispatcher.add_handler(RM_CHAT_TAGS_HANDLER)
    # USERS
    dispatcher.add_handler(USER_AUTHENTICATION_HANDLER)
    dispatcher.add_handler(USER_REMOVE_HANDLER)
    dispatcher.add_handler(SHOW_USERS_HANDLER)

    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4)

    updater.idle()


if __name__ == '__main__':
    LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
    main("633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg")
