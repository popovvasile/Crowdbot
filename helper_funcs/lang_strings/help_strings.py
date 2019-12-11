from collections import OrderedDict

from telegram import InlineKeyboardButton
from database import chatbots_table, users_messages_to_admin_table
from helper_funcs.lang_strings.strings import string_dict


def help_strings(context):
    help_dict = OrderedDict()
    string_d_str = string_dict(context)
    payment_token = chatbots_table.find_one({"bot_id": context.bot.id})
    admins_keyboard = [
        InlineKeyboardButton(text=string_d_str["payment_configure_button"],
                             callback_data="payments_config"),
        InlineKeyboardButton(text=string_d_str["donation_statistic_btn_str"],
                             callback_data="donation_statistic")
    ]
    if "shop" in payment_token:
        admins_keyboard += [InlineKeyboardButton(text=string_dict(context)["shop"],
                                                 callback_data="shop_start"),
                            InlineKeyboardButton(string_dict(context)["donations"],
                                                 callback_data="donations_config"),
                            InlineKeyboardButton(text=string_dict(context)["payments_statistics_str"],
                                                 callback_data="payments_statistics"),
 ]

        help_dict["shop"] = dict(
            mod_name=string_d_str["add_product_button"],
            admin_keyboard=admins_keyboard,
            admin_help=string_d_str["add_menu_buttons_help"],
            visitor_keyboard=[InlineKeyboardButton(text=string_d_str["shop"],
                                                   callback_data="products")],
            visitor_help=string_d_str["add_menu_buttons_help_visitor"]
        )
    else:
        help_dict["shop"] = dict(
            mod_name=string_d_str["add_product_button"],
            admin_keyboard=admins_keyboard,
            admin_help=string_d_str["add_menu_buttons_help"],
        )
    help_dict["channels"] = dict(
        mod_name='Channels',
        # start 'Channels' message
        admin_help=string_d_str["channels_str_1"],
        # and keyboard for start message
        admin_keyboard=[InlineKeyboardButton(string_d_str["channels"], callback_data='channels'),
                        InlineKeyboardButton(string_d_str["groups"], callback_data='groups')]
    )

    help_dict["settings"] = dict(
        # TODO "add admins" functionality
        mod_name=string_d_str["add_menu_module_button"],
        admin_keyboard=[InlineKeyboardButton(text=string_d_str["buttons_button"],
                                             callback_data="buttons"),
                        InlineKeyboardButton(text=string_d_str["edit_menu_text"],
                                             callback_data="edit_bot_description"),
                        InlineKeyboardButton(text=string_d_str["user_mode_module"],
                                             callback_data="turn_user_mode_on"),
                        InlineKeyboardButton(text=string_d_str["payment_configure_button"],
                                             callback_data="payments_config"),
                        InlineKeyboardButton(text=string_d_str["admins_btn_str"],
                                             callback_data="admins"),
                        InlineKeyboardButton(text=string_d_str["add_admin_btn_str"],
                                             callback_data="start_add_admins")],
        admin_help=string_d_str["add_menu_buttons_help"]
    )

    help_dict["polls"] = dict(  # TODO unite with surveys
        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["polls_mode_str"], callback_data="polls"),
            InlineKeyboardButton(text=string_d_str["survey_mode_str"], callback_data="surveys"),
        ],
        mod_name=string_d_str["polls_module_str"],
        admin_help=string_d_str["polls_help_admin"]
    )
    not_read_messages_count = users_messages_to_admin_table.find(
        {"bot_id": context.bot.id, "is_new": True}).count() or ""
    help_dict["users"] = dict(  # TODO add stats and everything related tom messages
        mod_name=string_d_str["users_module"],
        admin_help=string_d_str["users_help_admin"],

        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["messages"] +
                                 f" {not_read_messages_count}",
                                 callback_data="admin_messages"),
            InlineKeyboardButton(text=string_d_str["users_module"],
                                 callback_data="users_list"),  # TODO User statistics
            # TODO Send messages ==> to users, to donators, to customers
            InlineKeyboardButton(text=string_d_str["user_mode_module"],
                                 callback_data="turn_user_mode_on"),
            InlineKeyboardButton(text=string_d_str["send_message_button_6"],
                                 callback_data="blocked_users_list"),
        ]
    )

    help_dict["messages"] = dict(  # TODO visitors only
        mod_name=string_d_str["send_message_module_str"],
        visitor_help=string_d_str["send_message_user"],
        visitor_keyboard=[InlineKeyboardButton(text=string_d_str["send_message_button_to_admin"],
                                               callback_data="send_message_to_admin"),
                          InlineKeyboardButton(text=string_d_str["send_message_button_to_admin_anonim"],
                                               callback_data="send_message_to_admin_anonim")
                          ],
    )

    return help_dict


def helpable_dict(bot):
    admin_rus = OrderedDict()
    admin_rus["❓ Опросы"] = "polls"
    admin_rus["🛠 Настройки бота"] = "settings"
    admin_rus["📱 Группы и каналы"] = "channels"
    admin_rus["Магазин и платежи"] = "shop"
    admin_rus["✉️ Пользователи и Сообщения"] = "users"

    admin_eng = OrderedDict()
    admin_eng["📱 Groups and Channels"] = "channels"
    admin_eng["❓ Polls and Surveys"] = "polls"
    admin_eng["✉️ Users & Messages"] = "users"
    admin_eng["🛠 Bot and Menu Settings"] = "settings"
    admin_eng["💰 Shop and Payments"] = "shop"

    lang_dicts = {"ENG": dict(
        ALL_MODULES=[],
        ADMIN_HELPABLE=admin_eng,
        ADMIN_USER_MODE={"💸 Donate ": "donation_payment",
                         "✉️ Message": "messages",
                         "Admin view": "user_mode"},
        VISITOR_HELPABLE={"💸 Donate ": "donation_payment",
                          "✉️ Message": "messages"},

    ),
        "RUS": dict(
            ALL_MODULES=[],
            ADMIN_HELPABLE=admin_rus,
            ADMIN_USER_MODE={
                "Режим админа": "user_mode",
                "💸 Задонатить": "donation_payment",
                "✉️ Сообщения": "messages"},
            VISITOR_HELPABLE={"💸💸 Задонатить": "donation_payment",
                              "✉️ Сообщения": "messages"},

        ),
    }
    # "channels", "donation_enable", "donation_payment", "donations_send_promotion",
    # "donations_edit_delete_results", "manage_button", "settings", "menu_description",
    # "messages", "polls", "surveys_answer", "surveys_create", "user_mode"
    chatbot = chatbots_table.find_one({"bot_id": bot.id})

    return lang_dicts[chatbot["lang"]]
