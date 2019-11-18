from collections import OrderedDict

from telegram import InlineKeyboardButton
from database import chatbots_table
from modules.helper_funcs.lang_strings.strings import string_dict


def help_strings(bot):
    help_dict = OrderedDict()
    string_d_str = string_dict(bot)
    help_dict["channels"] = dict(
        mod_name='Channels',
        # start 'Channels' message
        admin_help=["channels_str_1"],
        # and keyboard for start message
        admin_keyboard=[InlineKeyboardButton(string_d_str["my_channels"], callback_data='my_channels'),
                        InlineKeyboardButton(string_d_str["add_channel"], callback_data='add_channel')]
    )
    help_dict["groups"] = dict(
        mod_name='Groups',
        # start 'Channels' message
        admin_help=string_d_str["groups_str_1"],
        # and keyboard for start message
        admin_keyboard=[InlineKeyboardButton(string_d_str["my_groups"], callback_data='my_groups'),
                        InlineKeyboardButton(string_d_str["add_group"], callback_data='add_group')]
    )
    help_dict["shop"] = dict(
        mod_name=string_d_str["add_product_button"],
        admin_keyboard=[InlineKeyboardButton(text=string_d_str["add_product_button"],
                                             callback_data="create_product"),
                        InlineKeyboardButton(text=string_d_str["edit_product"],
                                             callback_data="edit_product"),
                        InlineKeyboardButton(text=string_d_str["delete_product"],
                                             callback_data="delete_product"),
                        InlineKeyboardButton(text=string_d_str["products"],
                                             callback_data="products"),
                        ],
        admin_help=string_d_str["add_menu_buttons_help"],
        visitor_keyboard=[InlineKeyboardButton(text=string_d_str["products"],
                                               callback_data="products")],
        visitor_help=string_d_str["add_menu_buttons_help_visitor"]
    )
    help_dict["menu_buttons"] = dict(
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
    help_dict["surveys"] = dict(
        mod_name=string_d_str["survey_mode_str"],
        admin_help=string_d_str["survey_help_admin"],

        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["create_button_str"], callback_data="create_survey"),
            InlineKeyboardButton(text=string_d_str["delete_button_str"], callback_data="delete_survey"),
            InlineKeyboardButton(text=string_d_str["send_button"], callback_data="send_survey_to_channel"),
            InlineKeyboardButton(text=string_d_str["results_button"], callback_data="surveys_results")
        ]

    )
    help_dict["messages"] = dict(
        mod_name=string_d_str["send_message_module_str"],
        visitor_help=string_d_str["send_message_user"],
        visitor_keyboard=[InlineKeyboardButton(text=string_d_str["send_message_button_to_admin"],
                                               callback_data="send_message_to_admin"),
                          InlineKeyboardButton(text=string_d_str["send_message_button_to_admin_anonim"],
                                               callback_data="send_message_to_admin_anonim")
                          ],


        admin_help=string_d_str["send_message_admin"],

        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["send_message_button_1"],
                                 callback_data="send_message_to_users"),
            InlineKeyboardButton(text=string_d_str["send_message_button_2"],
                                 callback_data="inbox_message"),
            # InlineKeyboardButton(text=string_d_str["send_message_button_4"],
            #                      callback_data="send_message_only_to_admins"),
            InlineKeyboardButton(text=string_d_str["send_message_button_5"],
                                 callback_data="send_message_to_donators"),
            InlineKeyboardButton(text=string_d_str["send_message_button_6"],
                                 callback_data="blocked_users_list")
        ]
    )
    help_dict["donation_payment"] = dict(
        mod_name=string_d_str["pay_donation_mode_str"],
        admin_help=string_d_str["pay_donation_str_admin"],

        visitor_help=string_d_str["pay_donation_mode_str"],

        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["ask_donation_button"],
                                 callback_data="send_donation_to_users"),
            # InlineKeyboardButton(text=string_d_str["donate_button"], callback_data="pay_donation"),

        ],

        visitor_keyboard=[
            InlineKeyboardButton(text=string_d_str["donate_button"], callback_data="pay_donation")]
    )

    help_dict["polls"] = dict(
        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["create_button_str"], callback_data="create_poll"),
            InlineKeyboardButton(text=string_d_str["send_button"], callback_data="send_poll_to_channel"),
            InlineKeyboardButton(text=string_d_str["delete_button_str"], callback_data="delete_poll"),
            InlineKeyboardButton(text=string_d_str["results_button"], callback_data="poll_results")],
        mod_name=string_d_str["polls_module_str"],
        admin_help=string_d_str["polls_help_admin"]
    )

    help_dict["user_mode"] = dict(
        mod_name=string_d_str["user_mode_str"],
        admin_help=string_d_str["user_mode_help_admin"],
        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["user_mode_str"], callback_data="turn_user_mode_on")]
    )

    help_dict["users"] = dict(
        mod_name=string_d_str["users_module"],
        admin_help=string_d_str["users_help_admin"],
        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["show_user_categories_button"],
                                 callback_data="show_user_categories"),
            InlineKeyboardButton(text=string_d_str["send_user_category_question_button"],
                                 callback_data="send_user_category_question")]
    )

    return help_dict


def helpable_dict(bot):
    admin_rus = OrderedDict()
    admin_rus["✉️ Сообщения"] = "messages"
    admin_rus["📱 Каналы"] = "channels"
    admin_rus["📱 Группы"] = "groups"

    admin_rus["❔ Открытые опросы"] = "surveys"
    admin_rus["❓ Опросы"] = "polls"
    admin_rus["💸 Донаты"] = "donation_payment"
    admin_rus[" Магазин"] = "shop"

    # admin_rus["Пользователи"] = "users"
    # admin_rus["👤 Режим юзера"] = "user_mode"
    admin_rus["🛠 Настройки"] = "menu_buttons"

    admin_eng = OrderedDict()
    admin_eng["✉️ Messages"] = "messages"
    admin_eng["📱 Channels"] = "channels"
    admin_eng["📱 Groups"] = "groups"

    admin_eng['❔ Surveys'] = "surveys"
    admin_eng["❓ Polls"] = "polls"
    admin_eng["Shop"] = "shop"
    admin_eng["💸 Donations"] = "donation_payment"
    # admin_eng["Users"] = "users"
    # admin_eng["👤 User view"] = "user_mode"
    admin_eng["🛠 Settings"] = "menu_buttons"

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