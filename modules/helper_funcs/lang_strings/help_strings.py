from collections import OrderedDict

from telegram import InlineKeyboardButton
from database import chatbots_table
from modules.helper_funcs.lang_strings.strings import string_dict


def help_strings(bot):
    help_dict = OrderedDict()
    help_dict["channels"] = dict(
        mod_name='Channels',
        # start 'Channels' message
        admin_help=string_dict(bot)["channels_str_1"],
        # and keyboard for start message
        admin_keyboard=[InlineKeyboardButton(string_dict(bot)["my_channels"], callback_data='my_channels'),
                        InlineKeyboardButton(string_dict(bot)["add_channel"], callback_data='add_channel')]
    )
    help_dict["menu_buttons"] = dict(
        mod_name=string_dict(bot)["add_menu_module_button"],
        admin_keyboard=[InlineKeyboardButton(text=string_dict(bot)["create_button"],
                                             callback_data="create_button"),
                        InlineKeyboardButton(text=string_dict(bot)["edit_button_button"],
                                             callback_data="edit_button"),
                        InlineKeyboardButton(text=string_dict(bot)["delete_button"],
                                             callback_data="delete_button"),
                        InlineKeyboardButton(text=string_dict(bot)["edit_menu_text"],
                                             callback_data="edit_bot_description")],

        admin_help=string_dict(bot)["add_menu_buttons_help"]
    )
    help_dict["surveys"] = dict(
        mod_name=string_dict(bot)["survey_mode_str"],
        admin_help=string_dict(bot)["survey_help_admin"],

        admin_keyboard=[
            InlineKeyboardButton(text=string_dict(bot)["create_button_str"], callback_data="create_survey"),
            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"], callback_data="delete_survey"),
            InlineKeyboardButton(text=string_dict(bot)["send_button"], callback_data="send_survey_to_users"),
            InlineKeyboardButton(text=string_dict(bot)["results_button"], callback_data="surveys_results")
        ]

    )
    help_dict["messages"] = dict(
        mod_name=string_dict(bot)["send_message_module_str"],
        visitor_help=string_dict(bot)["send_message_user"],
        visitor_keyboard=[InlineKeyboardButton(text=string_dict(bot)["send_message_button_1"],
                                               callback_data="send_message_to_admin")],

        admin_help=string_dict(bot)["send_message_admin"],

        admin_keyboard=[
            InlineKeyboardButton(text=string_dict(bot)["send_message_button_1"],
                                 callback_data="send_message_to_users"),
            InlineKeyboardButton(text=string_dict(bot)["send_message_button_2"],
                                 callback_data="inbox_message"),
            InlineKeyboardButton(text=string_dict(bot)["send_message_button_3"],
                                 callback_data="show_message_categories"),
        ]
    )
    help_dict["donation_payment"] = dict(
        mod_name=string_dict(bot)["pay_donation_mode_str"],
        admin_help=string_dict(bot)["pay_donation_str_admin"],

        visitor_help=string_dict(bot)["pay_donation_mode_str"],

        admin_keyboard=[
            InlineKeyboardButton(text=string_dict(bot)["configure_button"],
                                 callback_data="configure_donation"),
            InlineKeyboardButton(text=string_dict(bot)["ask_donation_button"],
                                 callback_data="send_donation_to_users"),
            # InlineKeyboardButton(text=string_dict(bot)["donate_button"], callback_data="pay_donation"),

        ],

        visitor_keyboard=[
            InlineKeyboardButton(text=string_dict(bot)["donate_button"], callback_data="pay_donation")]
    )

    help_dict["polls"] = dict(
        admin_keyboard=[
            InlineKeyboardButton(text=string_dict(bot)["create_button_str"], callback_data="create_poll"),
            InlineKeyboardButton(text=string_dict(bot)["send_button"], callback_data="send_poll_to_users"),
            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"], callback_data="delete_poll"),
            InlineKeyboardButton(text=string_dict(bot)["results_button"], callback_data="poll_results")],
        mod_name=string_dict(bot)["polls_module_str"],
        admin_help=string_dict(bot)["polls_help_admin"]
    )

    help_dict["user_mode"] = dict(
        mod_name=string_dict(bot)["user_mode_str"],
        admin_help=string_dict(bot)["user_mode_help_admin"],
        admin_keyboard=[
            InlineKeyboardButton(text=string_dict(bot)["user_mode_str"], callback_data="turn_user_mode_on")]
    )

    help_dict["users"] = dict(
        mod_name=string_dict(bot)["users_module"],
        admin_help=string_dict(bot)["users_help_admin"],
        admin_keyboard=[
            InlineKeyboardButton(text=string_dict(bot)["show_user_categories_button"],
                                 callback_data="show_user_categories"),
            InlineKeyboardButton(text=string_dict(bot)["send_user_category_question_button"],
                                 callback_data="send_user_category_question")]
    )

    return help_dict


def helpable_dict(bot):
    admin_rus = OrderedDict()
    admin_rus["✉️ Сообщения"] = "messages"
    admin_rus["📱 Каналы"] = "channels"
    admin_rus["❔ Открытые опросы"] = "surveys"
    admin_rus["❓ Опросы"] = "polls"
    admin_rus["💸 Донаты"] = "donation_payment"
    # admin_rus["Пользователи"] = "users"
    admin_rus["👤 Режим юзера"] = "user_mode"
    admin_rus["🛠 Настройки"] = "menu_buttons"

    admin_eng = OrderedDict()
    admin_eng["✉️ Messages"] = "messages"
    admin_eng["📱 Channels"] = "channels"
    admin_eng['❔ Surveys'] = "surveys"
    admin_eng["❓ Polls"] = "polls"
    admin_eng["💸 Donations"] = "donation_payment"
    # admin_eng["Users"] = "users"
    admin_eng["👤 User view"] = "user_mode"
    admin_eng["🛠 Settings"] = "menu_buttons"


    lang_dicts = {"ENG": dict(
        ALL_MODULES=[],
        ADMIN_HELPABLE=admin_eng,
        ADMIN_USER_MODE={"💸 Donations ": "donation_payment",
                         "✉️ Messages": "messages",
                         "Admin view": "user_mode"},
        VISITOR_HELPABLE={}

    ),
        "RUS": dict(
            ALL_MODULES=[],
            ADMIN_HELPABLE=admin_rus,
            ADMIN_USER_MODE={
                "Режим админа": "user_mode",
                "💸 Донаты ": "donation_payment",
                "✉️ Сообщения": "messages",},
            VISITOR_HELPABLE={}

        ),
    }
    # "channels", "donation_enable", "donation_payment", "donations_send_promotion",
    # "donations_edit_delete_results", "manage_button", "menu_buttons", "menu_description",
    # "messages", "polls", "surveys_answer", "surveys_create", "user_mode"
    chatbot = chatbots_table.find_one({"bot_id": bot.id})

    return lang_dicts[chatbot["lang"]]