import logging
import re
from urllib3.exceptions import HTTPError

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
from telegram.ext import ConversationHandler
from telegram.error import (BadRequest, TimedOut, NetworkError, TelegramError,
                            ChatMigrated)

from helper_funcs.lang_strings.help_strings import help_strings, helpable_dict
from helper_funcs.misc import paginate_modules, LOGGER, delete_messages
from helper_funcs.auth import (if_admin, initiate_chat_id,
                               register_chat, register_admin)
from database import (custom_buttons_table, users_table, chatbots_table,
                      user_mode_table, products_table, groups_table)

HELP_STRINGS = """
{}
"""


# do not async
def send_admin_help(bot, chat_id, text, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(
            paginate_modules(helpable_dict(bot)["ADMIN_HELPABLE"], "help", bot.id)+\
                   [[InlineKeyboardButton(text=bot.lang_dict["user_mode_module"],
                                          callback_data="turn_user_mode_on")]])
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=keyboard)


def send_visitor_help(bot, chat_id, text):
    # donation_request = chatbots_table.find_one({"bot_id": bot.id})
    # if donation_request.get("donate") is not None and donation_request.get("donate") != {}:
    #     buttons = [InlineKeyboardButton(bot.lang_dict["send_message_1"],
    #                                     callback_data="send_message_to_admin"),
    #                InlineKeyboardButton(bot.lang_dict["pay_donation_mode_str"],
    #                                     callback_data='pay_donation'), ]
    #
    # else:
    first_buttons = [[InlineKeyboardButton(bot.lang_dict["send_message_1"],
                                           callback_data="send_message_to_admin")]]
    product_list_of_dicts = products_table.find({
        "bot_id": bot.id})
    buttons = list()
    if product_list_of_dicts.count() != 0:
        buttons = [InlineKeyboardButton(text=bot.lang_dict["shop"],
                                        callback_data="help_module(shop)")]

    buttons += [InlineKeyboardButton(button["button"],
                                     callback_data="button_{}".
                                     format(button["button"].replace(" ", "").lower()))
                for button in custom_buttons_table.find({"bot_id": bot.id, "link_button": False})]

    buttons += [InlineKeyboardButton(text=button["button"], url=button["link"])
                for button in custom_buttons_table.find({"bot_id": bot.id, "link_button": True})]

    if len(buttons) % 2 == 0:
        pairs = list(zip(buttons[::2], buttons[1::2]))
    else:
        pairs = list(zip(buttons[::2], buttons[1::2])) + [(buttons[-1],)]
    pairs = first_buttons + pairs

    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=InlineKeyboardMarkup(
                         pairs
                     ))


def send_admin_user_mode(bot, chat_id, text):

    first_buttons = [[InlineKeyboardButton(bot.lang_dict["send_message_1"],
                                           callback_data="send_message_to_admin")]]
    product_list_of_dicts = products_table.find({
        "bot_id": bot.id})
    if product_list_of_dicts.count() != 0:
        first_buttons += [[InlineKeyboardButton(text=bot.lang_dict["shop"],
                                                callback_data="help_module(shop)")]]

    buttons = [InlineKeyboardButton(button["button"],
                                    callback_data="button_{}".
                                    format(button["button"].replace(" ", "").lower()))
               for button in custom_buttons_table.find({"bot_id": bot.id, "link_button": False})]

    buttons += [InlineKeyboardButton(button["button"], url=button["link"])
                for button in custom_buttons_table.find({"bot_id": bot.id, "link_button": True})]

    if len(buttons) % 2 == 0:
        pairs = list(zip(buttons[::2], buttons[1::2]))
    else:
        pairs = list(zip(buttons[::2], buttons[1::2])) + [(buttons[-1],)]
    pairs = first_buttons + pairs + [[InlineKeyboardButton(text="ADMIN MODE",
                                                           callback_data="turn_user_mode_off")]]
    bot.send_message(chat_id=chat_id,
                     text=text,
                     parse_mode=ParseMode.MARKDOWN,
                     reply_markup=InlineKeyboardMarkup(
                         pairs
                     ))


def check_provider_token(provider_token, update, context):
    prices = [LabeledPrice("TEST", 100)]
    if "to_delete" not in context.user_data:
        context.user_data["to_delete"] = []

    if update.callback_query:
        update_data = update.callback_query
    else:
        update_data = update
    try:
        context.user_data["to_delete"].append(
            context.bot.sendInvoice(update_data.message.chat_id, "TEST",
                                    "A testing payment invoice to check the token",
                                    "test",
                                    provider_token, "test", "USD", prices,
                                    need_name=True, need_phone_number=True,
                                    need_email=True, need_shipping_address=False,
                                    is_flexible=True
                                    ))

    except Exception as e:
        print(e)
        return False
    delete_messages(update, context, True)
    return True

# for test purposes
def error_callback(update, context):
    try:
        back_buttons = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                   callback_data="help_back")]
             ])
        # print(error)
        if update.effective_message.chat_id > 0:
            if hasattr(update, 'callback_query'):
                context.bot.send_message(update.effective_message.chat_id,
                                         "An error accured =( Please proceed to the shop menu",
                                         reply_markup=back_buttons)
            elif hasattr(update, 'message'):
                context.bot.send_message(update.effective_message.chat.id,
                                         "An error happened =( Please proceed to the shop menu",
                                         reply_markup=back_buttons)

            return
        else:
            return

    except ConnectionError as err:
        print("ConnectionError")
        print(err)
    except TimedOut as err:
        print("TimedOut")
        print(err)

        # handle slow connection problems
    except (HTTPError, BadRequest):
        print("HTTPError")

    except NetworkError:
        print("Neworkerror")
    # handle other connection problems
    except ChatMigrated as e:
        # the chat_id of a group has changed, use e.new_chat_id instead
        print("ChatMigrated")

    except TelegramError:
        print("TeelgramError")
    except Exception as e:
        logging.error(e.__repr__())
        context.bot.send_message(update.effective_message.chat.id,
                                 "An error happened =( Please proceed to the shop menu",
                                 reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton(
                                         text=context.bot.lang_dict["back_button"],
                                         callback_data="help_back")]]))


def button_handler(update, context):
    context.user_data['to_delete'] = []
    query = update.callback_query
    button_callback_data = query.data
    buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                     callback_data="back_from_button")]]
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
    try:
        button_info = custom_buttons_table.find_one(
            {"bot_id": context.bot.id, "button_lower": button_callback_data.replace("button_", "")}
        )
        for content_dict in button_info["content"]:
            if "text" in content_dict:
                context.user_data['to_delete'].append(
                    query.message.reply_text(text=content_dict["text"], parse_mode='Markdown'))
            if "audio_file" in content_dict:
                context.user_data['to_delete'].append(
                    query.message.reply_audio(content_dict["audio_file"]))
            if "video_file" in content_dict:
                context.user_data['to_delete'].append(
                    query.message.reply_video(content_dict["video_file"]))
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" \
                        in content_dict["document_file"]:
                    context.user_data['to_delete'].append(
                        context.bot.send_photo(chat_id=query.message.chat.id,
                                               photo=content_dict["document_file"]))
                else:
                    context.user_data['to_delete'].append(context.bot.send_document(
                        chat_id=query.message.chat.id,
                        document=content_dict["document_file"]))
            if "photo_file" in content_dict:
                context.user_data['to_delete'].append(
                    context.bot.send_photo(chat_id=query.message.chat.id,
                                           photo=content_dict["photo_file"]))
            if "video_note_file" in content_dict:
                context.user_data['to_delete'].append(
                    query.message.reply_video_note(content_dict["video_note_file"]))
            if "voice_file" in content_dict:
                context.user_data['to_delete'].append(
                    query.message.reply_voice(content_dict["voice_file"]))
            if "animation_file" in content_dict:
                context.user_data['to_delete'].append(
                    query.message.reply_animation(content_dict["animation_file"]))
            if "sticker_file" in content_dict:
                context.user_data['to_delete'].append(query.message.reply_sticker(
                    content_dict["sticker_file"]))

    except BadRequest as excp:
        if excp.message == "Message is not modified":
            pass
        elif excp.message == "Query_id_invalid":
            pass
        elif excp.message == "Message can't be deleted":
            pass
        else:
            LOGGER.exception("Exception in help buttons. %s", str(query.data))
    context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                             text=context.bot.lang_dict["back_button"],
                             reply_markup=InlineKeyboardMarkup(buttons))


#
# def product_handler(update, context):
#     context.user_data['to_delete'] = []
#     query = update.callback_query
#     button_callback_data = query.data
#     context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
#                                message_id=update.callback_query.message.message_id)
#     try:
#         button_info = products_table.find_one(
#             {"bot_id": context.bot.id, "title_lower": button_callback_data.replace("product_", "")}
#         )
#         for content_dict in button_info["content"]:
#             if "text" in content_dict:
#                 context.user_data['to_delete'].append(query.message.reply_text(text=content_dict["text"],
#                                                                                parse_mode='Markdown'))
#             if "audio_file" in content_dict:
#                 context.user_data['to_delete'].append(query.message.reply_audio(content_dict["audio_file"]))
#             if "video_file" in content_dict:
#                 context.user_data['to_delete'].append(query.message.reply_video(content_dict["video_file"]))
#             if "document_file" in content_dict:
#                 if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
#                     context.user_data['to_delete'].append(context.bot.send_photo(chat_id=query.message.chat.id,
#                                                                                  photo=content_dict["document_file"]))
#                 else:
#                     context.user_data['to_delete'].append(context.bot.send_document(chat_id=query.message.chat.id,
#                                                                                     document=content_dict[
#                                                                                         "document_file"]))
#             if "photo_file" in content_dict:
#                 context.user_data['to_delete'].append(context.bot.send_photo(chat_id=query.message.chat.id,
#                                                                              photo=content_dict["photo_file"]))
#             if "video_note_file" in content_dict:
#                 context.user_data['to_delete'].append(query.message.reply_video_note(content_dict["video_note_file"]))
#             if "voice_file" in content_dict:
#                 context.user_data['to_delete'].append(query.message.reply_voice(content_dict["voice_file"]))
#             if "animation_file" in content_dict:
#                 context.user_data['to_delete'].append(query.message.reply_animation(content_dict["animation_file"]))
#             if "sticker_file" in content_dict:
#                 context.user_data['to_delete'].append(query.message.reply_sticker(content_dict["sticker_file"]))
#
#     except BadRequest as excp:
#         if excp.message == "Message is not modified":
#             pass
#         elif excp.message == "Query_id_invalid":
#             pass
#         elif excp.message == "Message can't be deleted":
#             pass
#         else:
#             LOGGER.exception("Exception in help buttons. %s", str(query.data))
#     context.bot.send_message(update.callback_query.message.chat_id, "Buy this product",
#                              reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(
#                                  text=context.bot.lang_dict["buy_button"],
#                                  callback_data="pay_product_{}".format(button_callback_data.replace("product_", ""))),
#                                  InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                                       callback_data="products")
#                              ]]))


def back_from_button_handler(update, context):
    delete_messages(update, context)
    help_button(update, context)


def back_to_modules(update, context):
    """All backs to main menu buttons(modules) must be done through this func.
    Need to do better with logic in help_button function.
    Don't want to reformat for now so use little trick here.

    update.callback_query.data = "back_to_module_{here is the name of module}"
    """
    delete_messages(update, context)
    context.user_data.clear()
    module_name = update.callback_query.data.replace("back_to_module_", "")
    update.callback_query.data = f"help_module({module_name})"
    return help_button(update, context)


# chatbots_table.find_one({"bot_id": bot.id})["donation"]["description"]

# ADMIN_USER_MODE = {'Donate': "",
#                    'Send a message': "",
#                    "User view": ""}

def help_button(update, context):
    if users_table.find_one({"user_id": update.effective_user.id, "bot_id": context.bot.id}).get(
            "blocked", False):
        update.effective_message.reply_text(context.bot.lang_dict["blocked_user"])
        return ConversationHandler.END
    if if_admin(update=update, context=context.bot):
        HELPABLE = helpable_dict(context.bot)["ADMIN_HELPABLE"]
    else:
        HELPABLE = helpable_dict(context.bot)["VISITOR_HELPABLE"]
    query = update.callback_query
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    back_button_match = re.match(r"back_from_button", query.data)
    chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
    if chatbot:
        if 'welcomeMessage' in chatbot:
            if if_admin(update=update, context=context.bot):
                welcome_message = context.bot.lang_dict["welcome"]
            else:
                welcome_message = chatbot['welcomeMessage']
        else:
            welcome_message = "Hello"
    else:
        welcome_message = "Hello"
    try:
        if mod_match:

            module = mod_match.group(1)
            current_user_mode = user_mode_table.find_one({"bot_id": context.bot.id,
                                                          "user_id": update.effective_user.id})
            if if_admin(update=update, context=context.bot):
                if current_user_mode:
                    if current_user_mode.get("user_mode"):
                        text = help_strings(context, update)[module]["visitor_help"]
                        commands_keyboard = help_strings(context, update)[module][
                            "visitor_keyboard"]
                    else:
                        text = help_strings(context, update)[module]["admin_help"]
                        commands_keyboard = help_strings(context, update)[module]["admin_keyboard"]
                else:
                    text = help_strings(context, update)[module]["admin_help"]
                    commands_keyboard = help_strings(context, update)[module]["admin_keyboard"]
            # elif module == "donate":
            #     chatbot_info = chatbots_table.find_one(
            #         {"bot_id": context.bot.id})
            #     if "description" in chatbot_info.get("donate", {}):
            #         text = chatbot_info["donate"]["description"]
            #     else:
            #         text = help_strings(context, update)[module]["admin_help"]
            #     commands_keyboard = help_strings(context, update)[module]["admin_keyboard"]
            else:
                text = help_strings(context, update)[module]["visitor_help"]
                commands_keyboard = help_strings(context, update)[module]["visitor_keyboard"]
            pairs = commands_keyboard

            # if len(commands_keyboard) % 2 == 1:
            #     pairs.append((commands_keyboard[-1],))
            pairs.append(
                [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                      callback_data="help_back")]
            )
            query.message.reply_text(text=text,
                                     reply_markup=InlineKeyboardMarkup(pairs))

        elif prev_match:
            query.message.reply_text(HELP_STRINGS.format(welcome_message),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(HELPABLE, "help", context.bot.id)))
        elif next_match:
            query.message.reply_text(HELP_STRINGS.format(welcome_message),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(HELPABLE, "help", context.bot.id)))

        elif back_match or back_button_match:
            context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                       message_id=update.callback_query.message.message_id)
            delete_messages(update, context)
            get_help(update, context)
            return ConversationHandler.END


        else:
            query.message.reply_text(text=HELP_STRINGS.format(welcome_message),
                                     reply_markup=InlineKeyboardMarkup(
                                         paginate_modules(HELPABLE, "help", context.bot.id)))
            return ConversationHandler.END
        # ensure no spiny white circle
        context.bot.answer_callback_query(query.id)
        try:
            query.message.delete()
        except BadRequest:
            pass
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


def get_help(update, context):
    try:
        delete_messages(update, context)
    except BadRequest:
        pass
    if users_table.find_one({"user_id": update.effective_user.id, "bot_id": context.bot.id}).get(
            "blocked", False):
        update.effective_message.reply_text("You've been blocked from this chatbot")
        return ConversationHandler.END
    chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
    register_chat(update, context)
    chat = update.effective_chat
    current_user_mode = user_mode_table.find_one({"bot_id": context.bot.id,
                                                  "user_id": update.effective_user.id})

    if chatbot:
        if 'welcomeMessage' in chatbot:
            if if_admin(update=update, context=context.bot):
                welcome_message = "Hi! Here is your bot menu. You can configure your bot as you wish"
                # TODO change to multlilingual
            else:
                welcome_message = chatbot['welcomeMessage']
        else:
            welcome_message = "Hello"
    else:
        welcome_message = "Hello"
    if if_admin(update, context):
        if current_user_mode:
            if current_user_mode.get("user_mode") is True:
                send_admin_user_mode(context.bot, chat.id, HELP_STRINGS.format(welcome_message))
            else:
                send_admin_help(context.bot, chat.id, HELP_STRINGS.format(welcome_message))
        else:

            user_mode_table.insert({"bot_id": context.bot.id,
                                    "user_id": update.effective_user.id,
                                    "user_mode": False})
            send_admin_help(context.bot, chat.id, HELP_STRINGS.format(welcome_message))
    else:
        send_visitor_help(context.bot, chat.id, HELP_STRINGS.format(welcome_message))


def on_stupid_strings(update, context):
    get_help(update, context)


class WelcomeBot(object):
    @staticmethod
    def start(update, context):
        chat_id, txt = initiate_chat_id(update)
        if chat_id < 0:
            print("Group")
            context.bot.send_message(chat_id=chat_id, text=context.bot.lang_dict["hello_group"],
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(
                                             text=context.bot.lang_dict["menu_button"],
                                             url="https://telegram.me/{}".format(
                                                 context.bot.username))]]
                                     ))
            groups_table.update({"group_id": chat_id, "bot_id": context.bot.id},
                                {"group_id": chat_id, "bot_id": context.bot.id,
                                 "group_name": update.message.chat.title},
                                upsert=True)
            return ConversationHandler.END
        register_chat(update, context)
        if "survey_" in txt:
            context.bot.send_message(chat_id=chat_id, text=context.bot.lang_dict["survey_str_20"],
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(
                                             text=context.bot.lang_dict["start_button"],
                                             callback_data="{}".format(
                                                 str(txt.replace("/start ", ""))
                                             ))]]
                                     ))
        elif "registration" in txt:
            register_admin(update, context)
            get_help(update, context)
        elif "pay_donation" in txt:
            context.bot.send_message(chat_id=chat_id, text=context.bot.lang_dict["donate_button"],
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(
                                             text=context.bot.lang_dict["donate_button"],
                                             callback_data="pay_donation")]]
                                     ))
        else:
            if if_admin(update=update, context=context.bot):
                context.bot.send_message(chat_id,
                                         context.bot.lang_dict["start_help"].format(
                                             context.bot.first_name))
            get_help(update, context)

        return ConversationHandler.END


currency_limits_dict = {"RUB": {"min": 66.93, "max": 669329.91},
                        "USD": {"min": 1, "max": 10000},
                        "EUR": {"min": 0.89, "max": 8938.05},
                        "GBP": {"min": 0.77, "max": 7738.05},
                        "KZT": {"min": 380.86, "max": 3808642.90},
                        "UAH": {"min": 24.70, "max": 247047.94},
                        "RON": {"min": 4.30, "max": 43007.99},
                        "PLN": {"min": 3.84, "max": 38415.50}}
