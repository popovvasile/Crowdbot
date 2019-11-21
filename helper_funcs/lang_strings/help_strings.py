from collections import OrderedDict

from telegram import InlineKeyboardButton
from database import chatbots_table
from helper_funcs.lang_strings.strings import string_dict


def help_strings(bot):
    help_dict = OrderedDict()
    string_d_str = string_dict(bot)
    help_dict["channels"] = dict(  # TODO change to Groups and Channels
        mod_name='Channels',
        # start 'Channels' message
        admin_help=string_d_str["channels_str_1"],
        # and keyboard for start message
        admin_keyboard=[InlineKeyboardButton(string_d_str["my_channels"], callback_data='my_channels'),
                        InlineKeyboardButton(string_d_str["my_groups"], callback_data='my_groups')]
    )
    help_dict["shop"] = dict(
        mod_name=string_d_str["add_product_button"],
        admin_keyboard=[InlineKeyboardButton(text=string_d_str["products"],
                                             callback_data="products"),
                        InlineKeyboardButton(text=string_d_str["add_product_button"],
                                             callback_data="create_product"),
                        InlineKeyboardButton(text=string_d_str["edit_product"],
                                             callback_data="edit_product"),
                        InlineKeyboardButton(text=string_d_str["delete_product"],
                                             callback_data="delete_product"),
                        InlineKeyboardButton(text=string_d_str["payment_configure_button"],
                                             callback_data="configure_donation"),
                        InlineKeyboardButton(text=string_dict(bot)["ask_donation_button"],
                                             callback_data="send_donation_to_users"),
                        InlineKeyboardButton(text=string_dict(bot)["payments_statistics_str"],
                                             callback_data="payments_statistics"),
                        InlineKeyboardButton(text=string_dict(bot)["orders_str"],
                                             callback_data="orders_and_purchases")

                        ],
        admin_help=string_d_str["add_menu_buttons_help"],
        visitor_keyboard=[InlineKeyboardButton(text=string_d_str["products"],
                                               callback_data="products")],
        visitor_help=string_d_str["add_menu_buttons_help_visitor"]
    )
    help_dict["menu_buttons"] = dict(  # TODO "add admins" functionality
        mod_name=string_d_str["add_menu_module_button"],
        admin_keyboard=[InlineKeyboardButton(text=string_d_str["create_button"],
                                             callback_data="create_button"),
                        InlineKeyboardButton(text=string_d_str["edit_button_button"],
                                             callback_data="edit_button"),
                        InlineKeyboardButton(text=string_d_str["delete_button"],
                                             callback_data="delete_button"),
                        InlineKeyboardButton(text=string_d_str["edit_menu_text"],
                                             callback_data="edit_bot_description"),
                        InlineKeyboardButton(text=string_d_str["user_mode_module"],
                                             callback_data="turn_user_mode_on"),
                        InlineKeyboardButton(text=string_d_str["payment_configure_button"],
                                             callback_data="configure_donation"),
                        ],

        admin_help=string_d_str["add_menu_buttons_help"]
    )

    help_dict["polls"] = dict(  # TODO unite with surveys
        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["polls_mode_str"], callback_data="polls"),
            InlineKeyboardButton(text=string_d_str["survey_mode_str"], callback_data="surveys"),

            # InlineKeyboardButton(text=string_d_str["create_button_str"], callback_data="create_poll"),
            # InlineKeyboardButton(text=string_d_str["send_button"], callback_data="send_poll_to_channel"),
            # InlineKeyboardButton(text=string_d_str["delete_button_str"], callback_data="delete_poll"),
            # InlineKeyboardButton(text=string_d_str["results_button"], callback_data="poll_results"),
            #
            # InlineKeyboardButton(text=string_d_str["create_button_str"], callback_data="create_survey"),
            # InlineKeyboardButton(text=string_d_str["delete_button_str"], callback_data="delete_survey"),
            # InlineKeyboardButton(text=string_d_str["send_button"], callback_data="send_survey_to_channel"),
            # InlineKeyboardButton(text=string_d_str["results_button"], callback_data="surveys_results")
        ],
        mod_name=string_d_str["polls_module_str"],
        admin_help=string_d_str["polls_help_admin"]
    )

    help_dict["users"] = dict(  # TODO add stats and everything related tom messages
        mod_name=string_d_str["users_module"],
        admin_help=string_d_str["users_help_admin"],
        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["send_message_button_1"],
                                 callback_data="send_message_to_users"),
            InlineKeyboardButton(text=string_d_str["send_message_button_2"],
                                 callback_data="inbox_message"),
            InlineKeyboardButton(text=string_d_str["send_message_button_5"],
                                 callback_data="send_message_to_donators"),
            InlineKeyboardButton(text=string_d_str["users_module"],
                                 callback_data="users_list"),
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
    admin_rus["🛠 Настройки бота"] = "menu_buttons"
    admin_rus["📱 Группы и каналы"] = "channels"
    admin_rus["Магазин и платежи"] = "shop"
    admin_rus["✉️ Пользователи и Сообщения"] = "users"

    admin_eng = OrderedDict()
    admin_eng["📱 Groups and Channels"] = "channels"
    admin_eng["❓ Polls and Surveys"] = "polls"
    admin_eng["✉️ Users & Messages"] = "users"
    admin_eng["🛠 Bot and Menu Settings"] = "menu_buttons"
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
    # "donations_edit_delete_results", "manage_button", "menu_buttons", "menu_description",
    # "messages", "polls", "surveys_answer", "surveys_create", "user_mode"
    chatbot = chatbots_table.find_one({"bot_id": bot.id})

    return lang_dicts[chatbot["lang"]]
