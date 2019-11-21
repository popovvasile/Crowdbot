import re

from telegram import ParseMode, InlineKeyboardMarkup, Bot, Update, InlineKeyboardButton
from telegram.error import BadRequest, TimedOut, NetworkError, TelegramError, ChatMigrated
from telegram.ext import ConversationHandler
from urllib3.exceptions import HTTPError

from database import custom_buttons_table, users_table, chatbots_table, user_mode_table, products_table, groups_table
from helper_funcs.auth import if_admin, initiate_chat_id, register_chat
from helper_funcs.lang_strings.help_strings import help_strings, helpable_dict
from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.misc import paginate_modules, LOGGER, delete_messages

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

    donation_request = chatbots_table.find_one({"bot_id": bot.id})
    if donation_request.get("donate") is not None and donation_request.get("donate") != {}:
        buttons = [InlineKeyboardButton(string_dict(bot)["send_message_1"], callback_data="help_module(messages)"),
                   InlineKeyboardButton(string_dict(bot)["pay_donation_mode_str"], callback_data='pay_donation')]
    else:
        buttons = [InlineKeyboardButton(string_dict(bot)["send_message_1"], callback_data="help_module(messages)")]
    product_list_of_dicts = products_table.find({
        "bot_id": bot.id})
    if product_list_of_dicts.count() != 0:
        buttons = buttons + [InlineKeyboardButton(text="Shop", callback_data="products")]

    buttons += [InlineKeyboardButton(button["button"],
                                     callback_data="button_{}".format(button["button"].replace(" ", "").lower()))
                for button in custom_buttons_table.find({"bot_id": bot.id, "link_button": False})]
    buttons += [InlineKeyboardButton(text=button["button"],url=button["link"])
                for button in custom_buttons_table.find({"bot_id": bot.id, "link_button": True})]
    if len(buttons) % 2 == 0:
        pairs = list(zip(buttons[::2], buttons[1::2]))
    else:
        pairs = list(zip(buttons[::2], buttons[1::2])) + [(buttons[-1],)]
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=InlineKeyboardMarkup(
                         pairs
                     ))


def send_admin_user_mode(bot, chat_id, text, keyboard=None):
    donation_request = chatbots_table.find_one({"bot_id": bot.id})
    if donation_request.get("donate") is not None and donation_request.get("donate") != {}:
        buttons = [InlineKeyboardButton(string_dict(bot)["send_message_1"], callback_data="help_module(messages)"),
                   InlineKeyboardButton(string_dict(bot)["pay_donation_mode_str"], callback_data='pay_donation')]
    else:
        buttons = [InlineKeyboardButton(string_dict(bot)["send_message_1"], callback_data="help_module(messages)")]
    buttons += [InlineKeyboardButton(button["button"],
                                     callback_data="button_{}".format(button["button"].replace(" ", "").lower()))
                for button in custom_buttons_table.find({"bot_id": bot.id, "link_button": False})]
    buttons += [InlineKeyboardButton(button["button"],url=button["link"])
                for button in custom_buttons_table.find({"bot_id": bot.id, "link_button": True})]
    product_list_of_dicts = products_table.find({
        "bot_id": bot.id})
    if product_list_of_dicts.count() != 0:
        buttons = buttons + [InlineKeyboardButton(text="Shop", callback_data="products"),
                             InlineKeyboardButton(text="ADMIN MODE", callback_data="turn_user_mode_off")]
    else:
        buttons = buttons + [InlineKeyboardButton(text="ADMIN MODE", callback_data="turn_user_mode_off")]
    if len(buttons) % 2 == 0:
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
    try:
        back_buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                   callback_data="help_back")]
             ])
        print(error)
        if update.effective_message.chat_id > 0:
            if hasattr(update, 'callback_query'):
                bot.send_message(update.effective_message.chat_id,
                                 "An error accured =( Please proceed to the main menu",
                                 reply_markup=back_buttons)
            elif hasattr(update, 'message'):
                bot.send_message(update.effective_message.chat.id,
                                 "An error happened =( Please proceed to the main menu",
                                 reply_markup=back_buttons)

            return
        else:
            return
    except BadRequest:  # TODO
        bot.send_message(update.effective_message.chat.id,
                         "An error happened =( Please proceed to the main menu",
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_back")]]))
    except ConnectionError as err:
        print("ConnectionError")
        print(err)
    except TimedOut as err:
        print("TimedOut")
        print(err)

        # handle slow connection problems
    except HTTPError:
        print("HTTPError")


    except NetworkError:
        print("Neworkerror")
    # handle other connection problems
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        print("ChatMigrated")

    except TelegramError:
        print("TeelgramError")


def button_handler(bot: Bot, update: Update, user_data):
    user_data['to_delete'] = []
    query = update.callback_query
    button_callback_data = query.data
    buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="back_from_button")]]
    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    try:
        button_info = custom_buttons_table.find_one(
            {"bot_id": bot.id, "button_lower": button_callback_data.replace("button_", "")}
        )
        for content_dict in button_info["content"]:
            if "text" in content_dict:
                user_data['to_delete'].append(query.message.reply_text(text=content_dict["text"],
                                                                       parse_mode='Markdown'))
            if "audio_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_audio(content_dict["audio_file"]))
            if "video_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_video(content_dict["video_file"]))
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    user_data['to_delete'].append(bot.send_photo(chat_id=query.message.chat.id,
                                                                 photo=content_dict["document_file"]))
                else:
                    user_data['to_delete'].append(bot.send_document(chat_id=query.message.chat.id,
                                                                    document=content_dict["document_file"]))
            if "photo_file" in content_dict:
                user_data['to_delete'].append(bot.send_photo(chat_id=query.message.chat.id,
                                                             photo=content_dict["photo_file"]))
            if "video_note_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_video_note(content_dict["video_note_file"]))
            if "voice_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_voice(content_dict["voice_file"]))
            if "animation_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_animation(content_dict["animation_file"]))
            if "sticker_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_sticker(content_dict["sticker_file"]))

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
                     text=string_dict(bot)["back_button"], reply_markup=InlineKeyboardMarkup(buttons))


def product_handler(bot: Bot, update: Update, user_data):
    user_data['to_delete'] = []
    query = update.callback_query
    button_callback_data = query.data
    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    try:
        button_info = products_table.find_one(
            {"bot_id": bot.id, "title_lower": button_callback_data.replace("product_", "")}
        )
        for content_dict in button_info["content"]:
            if "text" in content_dict:
                user_data['to_delete'].append(query.message.reply_text(text=content_dict["text"],
                                                                       parse_mode='Markdown'))
            if "audio_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_audio(content_dict["audio_file"]))
            if "video_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_video(content_dict["video_file"]))
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    user_data['to_delete'].append(bot.send_photo(chat_id=query.message.chat.id,
                                                                 photo=content_dict["document_file"]))
                else:
                    user_data['to_delete'].append(bot.send_document(chat_id=query.message.chat.id,
                                                                    document=content_dict["document_file"]))
            if "photo_file" in content_dict:
                user_data['to_delete'].append(bot.send_photo(chat_id=query.message.chat.id,
                                                             photo=content_dict["photo_file"]))
            if "video_note_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_video_note(content_dict["video_note_file"]))
            if "voice_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_voice(content_dict["voice_file"]))
            if "animation_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_animation(content_dict["animation_file"]))
            if "sticker_file" in content_dict:
                user_data['to_delete'].append(query.message.reply_sticker(content_dict["sticker_file"]))

    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in help buttons. %s", str(query.data))
    bot.send_message(update.callback_query.message.chat_id, "Buy this product",
                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
                         text=string_dict(bot)["buy_button"],
                         callback_data="pay_product_{}".format(button_callback_data.replace("product_", ""))),
                                  InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="products")
                     ]]))


def back_from_button_handler(bot: Bot, update: Update, user_data):
    delete_messages(bot, update, user_data)
    help_button(bot, update)


# chatbots_table.find_one({"bot_id": bot.id})["donation"]["description"]

# ADMIN_USER_MODE = {'Donate': "",
#                    'Send a message': "",
#                    "User view": ""}

def help_button(bot: Bot, update: Update):
    if users_table.find_one({"user_id": update.effective_user.id, "bot_id":bot.id}).get("blocked", False):
        update.effective_message.reply_text("You've been blocked from this chatbot")
        return ConversationHandler.END
    if if_admin(update=update, bot=bot):
        HELPABLE = helpable_dict(bot)["ADMIN_HELPABLE"]
    else:
        HELPABLE = helpable_dict(bot)["VISITOR_HELPABLE"]
    query = update.callback_query
    print(query.data)
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    back_button_match = re.match(r"back_from_button", query.data)
    chatbot = chatbots_table.find_one({"bot_id": bot.id})
    if chatbot:
        if 'welcomeMessage' in chatbot:
            if if_admin(update=update, bot=bot):
                welcome_message = "Hi! Here is your bot menu. You can configure your bot as you wish"  # TODO change to multlilingual
            else:
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

        elif back_match or back_button_match:
            bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
            get_help(bot, update)
            return ConversationHandler.END
        else:
            query.message.reply_text(text=HELP_STRINGS.format(welcome_message),
                                     reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help", bot.id)))
            return ConversationHandler.END
        # ensure no spiny white circle
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
    if users_table.find_one({"user_id": update.effective_user.id, "bot_id":bot.id}).get("blocked", False):
        update.effective_message.reply_text("You've been blocked from this chatbot")
        return ConversationHandler.END
    chatbot = chatbots_table.find_one({"bot_id": bot.id})
    register_chat(bot, update)
    chat = update.effective_chat
    current_user_mode = user_mode_table.find_one({"bot_id": bot.id,
                                                  "user_id": update.effective_user.id})

    if chatbot:
        if 'welcomeMessage' in chatbot:
            if if_admin(update=update, bot=bot):
                welcome_message = "Hi! Here is your bot menu. You can configure your bot as you wish"  # TODO change to multlilingual
            else:
                welcome_message = chatbot['welcomeMessage']
        else:
            welcome_message = "Hello"
    else:
        welcome_message = "Hello"
    if if_admin(bot=bot, update=update):
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


def on_stupid_strings(bot: Bot, update: Update):
    get_help(bot, update)


class WelcomeBot(object):
    @staticmethod
    def start(bot, update):

        chat_id, txt = initiate_chat_id(update)
        if chat_id<0:
            print("Group")
            bot.send_message(chat_id=chat_id, text=string_dict(bot)["hello_group"],
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(text=string_dict(bot)["menu_button"],
                                                        url="https://telegram.me/{}".format(bot.username))]]
                             ))
            groups_table.update({"group_id": chat_id, "bot_id": bot.id},
                                {"group_id": chat_id, "bot_id": bot.id, "group_name": update.message.chat.title},
                                upsert=True)
            return ConversationHandler.END
        print("registration" in txt)
        user_id = update.message.from_user.id
        register_chat(bot, update)

        if "survey_" in txt:
            bot.send_message(chat_id=chat_id, text=string_dict(bot)["survey_str_20"],
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(text=string_dict(bot)["start_button"],
                                                        callback_data="{}".format(
                                                            str(txt.replace("/start ", ""))
                                                        ))]]
                             ))
        elif "registration" in txt:
            bot.send_message(chat_id=chat_id, text=string_dict(bot)["register_str"],
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(text=string_dict(bot)["menu_button"],
                                                        callback_data="help_back")]]
                             ))
        elif "pay_donation" in txt:
            bot.send_message(chat_id=chat_id, text=string_dict(bot)["donate_button"],
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(text=string_dict(bot)["donate_button"],
                                                        callback_data="pay_donation")]]
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