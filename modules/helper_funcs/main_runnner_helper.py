import re
from telegram import ParseMode, InlineKeyboardMarkup, Bot, Update, InlineKeyboardButton
from telegram.error import Unauthorized, BadRequest, TimedOut, NetworkError, TelegramError, ChatMigrated
from telegram.ext import run_async, ConversationHandler
from urllib3.exceptions import HTTPError

from database import custom_buttons_table, users_table, chatbots_table, user_mode_table
from modules.helper_funcs.auth import if_admin, initiate_chat_id, register_chat
from modules.helper_funcs.lang_strings.help_strings import help_strings, helpable_dict
from modules.helper_funcs.lang_strings.strings import string_dict
from modules.helper_funcs.misc import paginate_modules, LOGGER, EqInlineKeyboardButton

HELP_STRINGS = """
{}
"""


# do not async
def send_admin_help(bot, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, helpable_dict(bot)["ADMIN_HELPABLE"], "help", bot.id))
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=keyboard)


def send_visitor_help(bot, chat_id, text, keyboard=None):
    buttons = [InlineKeyboardButton(string_dict(bot)["send_message_1"], callback_data="send_message_to_admin"),
               InlineKeyboardButton(string_dict(bot)["pay_donation_mode_str"], callback_data='pay_donation')]
    buttons += [InlineKeyboardButton(button["button"],
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
    buttons = [InlineKeyboardButton(string_dict(bot)["send_message_1"], callback_data="send_message_to_admin"),
               InlineKeyboardButton(string_dict(bot)["pay_donation_mode_str"], callback_data='pay_donation')]
    buttons = buttons + [InlineKeyboardButton(button["button"],
                                     callback_data="button_{}".format(button["button"].replace(" ", "").lower()))
                for button in custom_buttons_table.find({"bot_id": bot.id})]
    buttons = buttons + [InlineKeyboardButton(text="ADMIN MODE", callback_data="turn_user_mode_off")]
    if len(buttons)%2==0:
        pairs = list(zip(buttons[::2], buttons[1::2]))
    else:
        pairs = list(zip(buttons[::2], buttons[1::2])) + [(buttons[-1],)]
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=InlineKeyboardMarkup(
                         pairs
                     ))


# for test purposes
def error_callback(bot, update, error):
    back_buttons = InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                   callback_data="error_back")]])
    print(error)
    try:

        if hasattr(update, 'callback_query'):
            update.callback_query.message.reply_text("An error accured =( Please proceed to the main menu",
                                      reply_markup=back_buttons)
        elif hasattr(update, 'message'):
            bot.send_message(update.callback_query.chat_instance,
                             "An error happened =( Please proceed to the main menu",
                             reply_markup=back_buttons)

        return

    except TimedOut as err:
        print("TimedOut")
        print(err)

        # handle slow connection problems
    except HTTPError:
        print("HTTPError")
        # handle other connection problems


def button_handler(bot: Bot, update: Update):
    query = update.callback_query
    button_callback_data = query.data
    buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]]
    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    try:
        button_info = custom_buttons_table.find_one(
            {"bot_id": bot.id, "button_lower": button_callback_data.replace("button_", "")}
        )  # TODO add files and images
        if "descriptions" in button_info:
            for descr in button_info["descriptions"]:  # TODO adjust for images and files
                query.message.reply_text(text=descr)
        if "audio_files" in button_info:
            for filename in button_info["audio_files"]:
                query.message.reply_audio(filename)
        if "video_files" in button_info:
            for filename in button_info["video_files"]:
                query.message.reply_video(filename)
        if "document_files" in button_info:
            for filename in button_info["document_files"]:
                if ".png" in filename or ".jpg" in filename:
                    bot.send_photo(chat_id=query.message.chat.id,
                                   photo=filename)
                else:
                    bot.send_document(chat_id=query.message.chat.id,
                                      document=filename)
        if "photo_files" in button_info:
            for filename in button_info["photo_files"]:
                bot.send_photo(chat_id=query.message.chat.id,
                               photo=filename)

    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in help buttons. %s", str(query.data))
    bot.send_message(chat_id=update.callback_query.message.chat_id,
                     text=string_dict(bot)["back_button"], reply_markup=InlineKeyboardMarkup(
            buttons))


# chatbots_table.find_one({"bot_id": bot.id})["donation"]["description"]

# ADMIN_USER_MODE = {'Donate': "",
#                    'Send a message': "",
#                    "User view": ""}

def help_button(bot: Bot, update: Update):
    # users_table.update({"user_id": update.message.from_user.id},
    #                    {'bot_id': bot.id,
    #                     "chat_id": update.message.chat.id,
    #                     "user_id": update.message.from_user.id,
    #                     "username": update.message.from_user.username,
    #                     "full_name": update.message.from_user.full_name,
    #                     'registered': False,
    #                     "pending": False,
    #                     "is_admin": False,
    #                     "tags": ["#all", "#user"]
    #                     }, upsert=True)
    if if_admin(update=update, bot=bot):
        HELPABLE = helpable_dict(bot)["ADMIN_HELPABLE"]
    else:
        HELPABLE = helpable_dict(bot)["VISITOR_HELPABLE"]
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    chatbot = chatbots_table.find_one({"bot_id": bot.id})
    if chatbot:
        if 'welcomeMessage' in chatbot:
            welcome_message = chatbot['welcomeMessage']
        else:
            welcome_message = "Hello"
    else:
        welcome_message = "Hello"
    try:
        if mod_match:
            module = mod_match.group(1)
            if module == "donate":
                chatbot_info = chatbots_table.find_one(
                    {"bot_id": bot.id})
                if "donate" in chatbot_info:
                    if "description" in chatbot_info["donate"]:
                        text = chatbot_info["donate"]["description"]
            current_user_mode = user_mode_table.find_one({"bot_id": bot.id,
                                                          "user_id": update.effective_user.id})
            if if_admin(update=update, bot=bot):
                if current_user_mode:
                    if current_user_mode.get("user_mode") is True:
                        text = help_strings(bot)[module]["visitor_help"]  # TODO modify for languages
                        commands_keyboard = help_strings(bot)[module]["visitor_keyboard"]
                    else:
                        text = help_strings(bot)[module]["admin_help"]
                        commands_keyboard = help_strings(bot)[module]["admin_keyboard"]
                else:
                    text = help_strings(bot)[module]["admin_help"]
                    commands_keyboard = help_strings(bot)[module]["admin_keyboard"]
            else:
                text = help_strings(bot)[module]["visitor_help"]
                commands_keyboard = help_strings(bot)[module]["visitor_keyboard"]

            pairs = list(zip(commands_keyboard[::2], commands_keyboard[1::2]))

            if len(commands_keyboard) % 2 == 1:
                pairs.append((commands_keyboard[-1],))
            pairs.append(
                [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]
            )
            query.message.reply_text(text=text,
                                     reply_markup=InlineKeyboardMarkup(pairs))

        elif prev_match:
            curr_page = int(prev_match.group(1))
            query.message.reply_text(HELP_STRINGS.format(welcome_message),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(curr_page - 1, HELPABLE, "help", bot.id)))
        elif next_match:
            next_page = int(next_match.group(1))
            query.message.reply_text(HELP_STRINGS.format(welcome_message),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(next_page + 1, HELPABLE, "help", bot.id)))

        elif back_match:
            bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
            get_help(bot, update)
            return ConversationHandler.END
        else:
            query.message.reply_text(text=HELP_STRINGS.format(welcome_message),
                                     reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", bot.id)))
            return ConversationHandler.END
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
        print(current_user_mode)
        if current_user_mode:
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


class WelcomeBot(object):
    @staticmethod
    def start(bot, update):
        chat_id, txt = initiate_chat_id(update)
        user_id = update.message.from_user.id
        register_chat(bot, update)
        users_table.update({"user_id": user_id},
                           {'bot_id': bot.id,
                            "chat_id": chat_id,
                            "user_id": user_id,
                            "username": update.message.from_user.username,
                            "full_name": update.message.from_user.full_name,
                            'registered': False,
                            "pending": False,
                            "is_admin": False,
                            "tags": ["#all", "#user"]
                            }, upsert=True)
        if "survey_" in txt:
            bot.send_message(chat_id=chat_id, text=string_dict(bot)["survey_str_20"],
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(text=string_dict(bot)["start_button"],
                                                        callback_data="{}".format(
                                                            str(txt.replace("/start ", ""))
                                                        ))]]
                             ))
        else:
            if if_admin(update=update, bot=bot):
                bot.send_message(chat_id,
                                 string_dict(bot)["start_help"].format(bot.first_name))
            get_help(bot=bot, update=update)
        # initial_survey = surveys_table.find_one({
        #     "bot_id": bot.id,
        #     "title": "initial"
        # })
        # if initial_survey:
        #     bot.send_message(chat_id=chat_id,
        #                      text="Dear {}, before you start, please answer a some quick questions. "
        #                           "To start the survey, press the button START".format(
        #                          update.message.from_user.first_name),
        #                      reply_markup=InlineKeyboardMarkup(
        #                          [InlineKeyboardButton(text="START",
        #                                                callback_data="survey_{}".format(
        #                                                    "initial"
        #                                                ))]
        #                      ))
        return ConversationHandler.END

    @staticmethod
    def cancel(bot, update):
        update.message.reply_text("Until next time!")
        return ConversationHandler.END
