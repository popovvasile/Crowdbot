from telegram import InlineKeyboardButton
from database import chatbots_table
from modules.helper_funcs.lang_strings.strings import string_dict


def help_strings(bot):
    help_dict = {"ENG": {
        "menu_buttons": dict(
            mod_name=string_dict(bot)["add_menu_module_button"],
            admin_keyboard=[InlineKeyboardButton(text=string_dict(bot)["create_button"],
                                                     callback_data="create_button"),
                                InlineKeyboardButton(text=string_dict(bot)["delete_button"],
                                                     callback_data="delete_button"),
                                InlineKeyboardButton(text=string_dict(bot)["edit_button_button"],
                                                     callback_data="edit_button"),
                                InlineKeyboardButton(text=string_dict(bot)["edit_menu_text"],
                                                     callback_data="edit_bot_description")],

            admin_help=string_dict(bot)["add_menu_buttons_help"]
        ),
        "surveys": dict(
            mod_name=string_dict(bot)["survey_mode_str"],
            admin_help=string_dict(bot)["survey_help_admin"],

            admin_keyboard=[
                InlineKeyboardButton(text=string_dict(bot)["create_button"], callback_data="create_survey"),
                InlineKeyboardButton(text=string_dict(bot)["delete_button"], callback_data="delete_survey"),
                InlineKeyboardButton(text=string_dict(bot)["send_button"], callback_data="send_survey"),
                InlineKeyboardButton(text=string_dict(bot)["results_button"], callback_data="surveys_results")
            ]

        ),
        "messages": dict(
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
            ]
        ),
        "donation_payment": dict(
            mod_name=string_dict(bot)["pay_donation_mode_str"],
            admin_help=string_dict(bot)["pay_donation_str_admin"],

            visitor_help=string_dict(bot)["pay_donation_mode_str"],

            admin_keyboard=[
                InlineKeyboardButton(text=string_dict(bot)["donate_button"], callback_data="pay_donation"),
                InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                     callback_data="allow_donation"),
                InlineKeyboardButton(text=string_dict(bot)["configure_button"],
                                     callback_data="configure_donation"),
                InlineKeyboardButton(text=string_dict(bot)["ask_donation_button"],
                                     callback_data="send_donation_to_users")],
            visitor_keyboard=[
                InlineKeyboardButton(text=string_dict(bot)["donate_button"], callback_data="pay_donation")],

        ),
        "polls": dict(
            admin_keyboard=[
                InlineKeyboardButton(text=string_dict(bot)["create_button"], callback_data="create_poll"),
                InlineKeyboardButton(text=string_dict(bot)["delete_button"], callback_data="delete_poll"),
                InlineKeyboardButton(text=string_dict(bot)["send_button"], callback_data="send_poll"),
                InlineKeyboardButton(text=string_dict(bot)["results_button"], callback_data="poll_results"),

            ],

            mod_name=string_dict(bot)["polls_module_str"],

            admin_help=string_dict(bot)["polls_help_admin"]),
        "user_mode": dict(
            mod_name=string_dict(bot)["user_mode_str"],
            admin_help=string_dict(bot)["user_mode_help_admin"],
            admin_keyboard=[
                InlineKeyboardButton(text=string_dict(bot)["user_mode_str"], callback_data="turn_user_mode_on")]

        )
    }}

    chatbot = chatbots_table.find_one({"bot_id": bot.id})
    return help_dict[chatbot["lang"]]
