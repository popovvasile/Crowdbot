from collections import OrderedDict

from telegram import InlineKeyboardButton

from helper_funcs.auth import if_admin
from database import (chatbots_table, users_messages_to_admin_table,
                      user_mode_table, carts_table)


def help_strings(context, update):
    help_dict = OrderedDict()
    string_d_str = context.bot.lang_dict
    admins_keyboard = [

        InlineKeyboardButton(context.bot.lang_dict["donations"],
                             callback_data="donations_menu"),
    ]
    admins_keyboard += [InlineKeyboardButton(text=context.bot.lang_dict["shop"],
                                             callback_data="shop_start")]

    # if "donate" in payment_token:
    #     admins_keyboard += [InlineKeyboardButton(text=context.bot.lang_dict["donations"],
    #                                              callback_data="donation_menu")]

    #     help_dict["shop"] = dict(
    #         mod_name=string_d_str["add_product_button"],
    #         admin_keyboard=admins_keyboard,
    #         admin_help=string_d_str["add_menu_buttons_help"],
    #         visitor_keyboard=[InlineKeyboardButton(text=string_d_str["shop"],
    #                                                callback_data="products")],
    #         visitor_help=string_d_str["add_menu_buttons_help_visitor"]
    #     )
    # else:
    shop = chatbots_table.find_one({"bot_id": context.bot.id}).get("shop", {})
    cart = carts_table.find_one({"bot_id": context.bot.id,
                                 "user_id": update.effective_user.id}) or {}
    cart_items_count = len(cart.get("products", list()))

    help_dict["shop"] = dict(
        mod_name=string_d_str["add_product_button"],
        admin_keyboard=admins_keyboard,
        admin_help=string_d_str["add_menu_buttons_help"],
        visitor_help=shop.get("description", ""),
        visitor_keyboard=[
            InlineKeyboardButton(text="Catalog",
                                 callback_data="open_shop"),
            InlineKeyboardButton(text="My Orders",
                                 callback_data="my_orders"),
            InlineKeyboardButton(text="🛒 Cart"
                                      + (f" ({cart_items_count})"
                                         if cart_items_count else ""),
                                 callback_data="cart")])
    help_dict["channels_groups"] = dict(
        mod_name='Channels',
        # start 'Channels' message
        admin_help=string_d_str["channels_str_1"],
        # and keyboard for start message
        admin_keyboard=[InlineKeyboardButton(text=string_d_str["channels"],
                                             callback_data='channels'),
                        InlineKeyboardButton(text=string_d_str["groups"],
                                             callback_data='groups')]
    )

    help_dict["settings"] = dict(
        mod_name=string_d_str["add_menu_module_button"],
        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["buttons_button"],
                                 callback_data="buttons"),
            InlineKeyboardButton(text=string_d_str["edit_menu_text"],
                                 callback_data="edit_bot_description"),
            InlineKeyboardButton(text=string_d_str["user_mode_module"],
                                 callback_data="turn_user_mode_on"),
            InlineKeyboardButton(text=string_d_str["payment_configure_button"],
                                 callback_data="payments_config"),
            InlineKeyboardButton(text=string_d_str["admins_btn_str"],
                                 callback_data="admins"),
            InlineKeyboardButton(text=string_d_str["statistic_btn_str"],
                                 callback_data="statistic")],
        admin_help=string_d_str["add_menu_buttons_help"]
    )

    help_dict["polls"] = dict(
        admin_keyboard=[
            InlineKeyboardButton(text=string_d_str["polls_mode_str"],
                                 callback_data="polls"),
            InlineKeyboardButton(text=string_d_str["survey_mode_str"],
                                 callback_data="surveys"),
        ],
        mod_name=string_d_str["polls_module_str"],
        admin_help=string_d_str["polls_help_admin"]
    )
    # Get unread messages count.
    new_messages_count = users_messages_to_admin_table.find(
        {"bot_id": context.bot.id, "is_new": True}).count()
    current_user_mode = user_mode_table.find_one(
        {"bot_id": context.bot.id, "user_id": update.effective_user.id})
    if if_admin(update, context) and not current_user_mode.get("user_mode"):
        messages_mode = string_d_str["users_module"]
    else:
        messages_mode = string_d_str["send_message_module_str"]
    help_dict["users"] = dict(
        mod_name=messages_mode,
        admin_help=string_d_str["users_help_admin"],

        admin_keyboard=[
            # TODO Send messages ==> to users, to donators, to customers
            InlineKeyboardButton(text=string_d_str["messages"]
                                 + (f" ({new_messages_count})"
                                    if new_messages_count else ""),
                                 callback_data="admin_messages"),
            InlineKeyboardButton(text=string_d_str["users_module"],
                                 callback_data="users_layout")
        ],
        visitor_help=string_d_str["send_message_user"],
        visitor_keyboard=[
            InlineKeyboardButton(
                text=string_d_str["send_message_button_to_admin"],
                callback_data="send_message_to_admin"),
            InlineKeyboardButton(
                text=string_d_str["send_message_button_to_admin_anonim"],
                callback_data="send_message_to_admin_anonim")]
    )

    return help_dict


def helpable_dict(bot):
    # Get unread messages count.
    new_messages_count = users_messages_to_admin_table.find(
        {"bot_id": bot.id, "is_new": True}).count()
    # Create unread messages string
    new_messages_str = (f" ({new_messages_count})"
                        if new_messages_count else "")
    admin_rus = OrderedDict()
    admin_rus["📱 Группы и каналы"] = "channels"
    admin_rus["❓ Опросы"] = "polls"
    admin_rus[f"✉️ Пользователи и Сообщения {new_messages_str}"] = "users"
    admin_rus["🛠 Настройки бота"] = "settings"
    admin_rus["📱 Группы и каналы"] = "channels_groups"
    admin_rus["Магазин и платежи"] = "shop"

    admin_eng = OrderedDict()
    admin_eng["📱 Groups and Channels"] = "channels_groups"
    admin_eng["❓ Polls and Surveys"] = "polls"
    admin_eng[f"✉️ Users & Messages {new_messages_str}"] = "users"
    admin_eng["🛠 Bot and Menu Settings"] = "settings"
    admin_eng["💰 Shop and Payments"] = "shop"

    lang_dicts = {"ENG": dict(
        ALL_MODULES=[],
        ADMIN_HELPABLE=admin_eng,
        ADMIN_USER_MODE={"💸 Donate ": "donation_payment",
                         "✉️ Message": "users",
                         "Admin view": "user_mode",
                         "Shop": "shop"},
        VISITOR_HELPABLE={"💸 Donate ": "donation_payment",
                          "✉️ Message": "users",
                          "💰 Shop": "shop"},

    ),
        "RUS": dict(
            ALL_MODULES=[],
            ADMIN_HELPABLE=admin_rus,
            ADMIN_USER_MODE={
                "Режим админа": "user_mode",
                "💸 Задонатить": "donation_payment",
                "✉️ Сообщения": "users",
                "Магазин": "shop"},
            VISITOR_HELPABLE={"💸💸 Задонатить": "donation_payment",
                              "✉️ Сообщения": "users",
                              "Магазин": "shop_user_menu"},
        ),
    }
    # "channels", "donation_enable", "donation_payment", "donations_send_promotion",
    # "donations_edit_delete_results", "manage_button", "settings", "menu_description",
    # "messages", "polls", "surveys_answer", "surveys_create", "user_mode"
    chatbot = chatbots_table.find_one({"bot_id": bot.id})

    return lang_dicts[chatbot["lang"]]
