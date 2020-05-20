from collections import OrderedDict

from telegram import InlineKeyboardButton

from helper_funcs.auth import if_admin
from modules.shop.helper.keyboards import start_keyboard
from database import (chatbots_table, users_messages_to_admin_table,
                      user_mode_table, carts_table, orders_table)


def help_strings(context, update):
    help_dict = OrderedDict()
    string_d_str = context.bot.lang_dict
    admins_keyboard = start_keyboard(context, back_button=False, as_list=True)
    shop = chatbots_table.find_one({"bot_id": context.bot.id}).get("shop", {})
    cart = carts_table.find_one({"bot_id": context.bot.id,
                                 "user_id": update.effective_user.id}) or {}
    cart_button_text = context.bot.lang_dict["shop_cart"]
    cart_items_count = len(cart.get("products", list()))
    if cart_items_count:
        cart_button_text += f" ({cart_items_count})"

    user_keyboard_shop = [
        [InlineKeyboardButton(text=context.bot.lang_dict["shop_catalog"],
                              callback_data="open_shop")],
        [InlineKeyboardButton(text=context.bot.lang_dict["shop_my_orders"],
                              callback_data="my_orders")],
        [InlineKeyboardButton(text=cart_button_text,
                              callback_data="cart")]]
    if shop.get("shipping") is False:
        user_keyboard_shop += [
            [InlineKeyboardButton(text=context.bot.lang_dict["shop_contact_and_address"],
                                  callback_data="contacts_shop")]]
    help_dict["shop"] = dict(
        mod_name=string_d_str["shop_admin_add_product_btn"],
        admin_keyboard=admins_keyboard,
        admin_help=string_d_str["shop_admin_start_message"],
        visitor_help=shop.get("description", ""),
        visitor_keyboard=user_keyboard_shop)

    help_dict["settings"] = dict(
        mod_name=string_d_str["add_menu_module_button"],
        admin_keyboard=[
            [InlineKeyboardButton(text=string_d_str["lang_menu_button"],
                                  callback_data="langmenu")],
            [InlineKeyboardButton(text=string_d_str["edit_menu_text"],
                                  callback_data="edit_bot_description")],
            [InlineKeyboardButton(text=string_d_str["edit_bot_pic_btn"],
                                  callback_data="edit_bot_pic")],
            [InlineKeyboardButton(text=string_d_str["menu_buttons_settings"],
                                  callback_data="buttons")],
            [InlineKeyboardButton(text=string_d_str["admins_btn_str"],
                                  callback_data="admins")],
            [InlineKeyboardButton(text=string_d_str["statistic_btn_str"],
                                  callback_data="users_statistic")],
            [InlineKeyboardButton(text=string_d_str["notification_btn_str"],
                                  callback_data="notification_setting")]
        ],
        admin_help=string_d_str["add_menu_buttons_help"]
    )

    current_user_mode = user_mode_table.find_one(
        {"bot_id": context.bot.id,
         "user_id": update.effective_user.id})
    if if_admin(update, context) and not current_user_mode.get("user_mode"):
        messages_mode = string_d_str["users_module"]
    else:
        messages_mode = string_d_str["send_message_module_str"]

    new_messages_count = users_messages_to_admin_table.find(
        {"bot_id": context.bot.id,
         "is_new": True,
         "deleted": False}).count()
    messages_button_text = string_d_str["messages"]
    if new_messages_count:
        messages_button_text += f" ({new_messages_count})"
    help_dict["users"] = dict(
        mod_name=messages_mode,
        admin_help=string_d_str["users_help_admin"],
        admin_keyboard=[
            # TODO Send messages ==> to users, to donators, to customers
            [InlineKeyboardButton(text=messages_button_text,
                                  callback_data="admin_messages")],
            [InlineKeyboardButton(text=string_d_str["users_module"],
                                  callback_data="users_layout")]
        ]
    )

    return help_dict


def helpable_dict(bot):
    # Get unread messages count.
    new_messages_count = users_messages_to_admin_table.find(
        {"bot_id": bot.id,
         "is_new": True,
         "deleted": False}).count()
    # Create unread messages string
    new_messages_str = (f" ({new_messages_count})"
                        if new_messages_count else "")
    admin_rus = OrderedDict()

    admin_rus["💰 Магазин"] = "shop"
    admin_rus[f"✉️ Пользователи и Сообщения {new_messages_str}"] = "users"
    admin_rus["⚙ Настройки бота"] = "settings"

    admin_eng = OrderedDict()

    admin_eng["💰 Shop"] = "shop"
    admin_eng[f"✉️ Users & Messages {new_messages_str}"] = "users"
    admin_eng["⚙ Settings"] = "settings"

    lang_dicts = {"ENG": dict(
        ALL_MODULES=[],
        ADMIN_HELPABLE=admin_eng,
        ADMIN_USER_MODE={
            "✉️ Message": "users",
            "Admin view": "user_mode",
            "Shop": "shop"},
        VISITOR_HELPABLE={
            "✉️ Message": "users",
            "💰 Shop": "shop"},

    ),
        "RUS": dict(
            ALL_MODULES=[],
            ADMIN_HELPABLE=admin_rus,
            ADMIN_USER_MODE={
                "Режим админа": "user_mode",
                "✉️ Сообщения": "users",
                "Магазин": "shop"},
            VISITOR_HELPABLE={
                "✉️ Сообщения": "users",
                "Магазин": "shop_user_menu"},
        ),
    }
    # "channels", "donation_enable", "donation_payment", "donations_send_promotion",
    # "donations_edit_delete_results", "manage_button", "settings", "menu_description",
    # "messages", "surveys_answer", "surveys_create", "user_mode"
    chatbot = chatbots_table.find_one({"bot_id": bot.id})

    return lang_dicts[chatbot["lang"]]
