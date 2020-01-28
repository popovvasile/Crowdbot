from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from database import chatbots_table


def start_keyboard(orders_quantity, context):
    chatbot = chatbots_table.find_one({"bot_id": context.bot.id})

    orders_btn_text = (
            context.bot.lang_dict["shop_admin_orders_btn"] +
            (f' {orders_quantity["new_orders_quantity"]}'
             if orders_quantity["new_orders_quantity"] != 0 else ""))

    if chatbot.get("shop_enabled") is True:
        keyboard = [
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_add_product_btn"],
                                  callback_data="add_product")],
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_categories_btn"],
                                  callback_data="categories")],
            [InlineKeyboardButton(orders_btn_text,
                                  callback_data="orders")],
            [InlineKeyboardButton(text=context.bot.lang_dict["user_mode_module"],
                                  callback_data="turn_user_mode_on")],
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_products_btn"],
                                  callback_data="products")],
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_trash_btn"],
                                  callback_data="trash")],
            [InlineKeyboardButton(text=context.bot.lang_dict["configure_button"],
                                  callback_data="shop_config")],
            [InlineKeyboardButton(text="Back", callback_data="help_module(shop)")]]
    elif "shop" in chatbot:
        keyboard = [[InlineKeyboardButton(text=context.bot.lang_dict["allow_shop_button"],
                                          callback_data="change_shop_config")],

                    [InlineKeyboardButton(text="Back", callback_data="help_module(shop)")]
                    ]
    else:
        keyboard = [[InlineKeyboardButton(text=context.bot.lang_dict["allow_shop_button"],
                                          callback_data='allow_shop')],
                    [InlineKeyboardButton(text="Back", callback_data="help_module(shop)")]]
    return InlineKeyboardMarkup(keyboard)


def create_keyboard(buttons, extra_buttons):
    pairs = list(zip(buttons[::2], buttons[1::2]))
    if len(buttons) % 2 == 1:
        pairs.append((buttons[-1],))
    pairs.extend([extra_buttons])
    return InlineKeyboardMarkup(pairs)


def back_btn(callback_data: str, context):
    return InlineKeyboardButton(
        context.bot.lang_dict["shop_admin_back_btn"], callback_data=callback_data)


def back_kb(callback_data: str, context):
    return InlineKeyboardMarkup([[back_btn(callback_data, context)]])


def keyboards(context):
    keyboards = dict(
        back_to_main_menu_keyboard=InlineKeyboardMarkup([
            [back_btn("back_to_main_menu_btn", context=context)]
        ]),
        back_to_products=InlineKeyboardMarkup([
            [back_btn("back_to_products_btn", context=context)]
        ]),
        back_to_brands=InlineKeyboardMarkup([
            [back_btn("back_to_brands_btn", context=context)]
        ]),
        confirm_add_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_confirm_btn"],
                                  callback_data="confirm_product")],
            [back_btn("back_to_main_menu_btn", context=context)]
        ]),
        continue_back_kb=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_continue_btn"],
                                  callback_data="continue"),
             back_btn("back_to_main_menu_btn", context=context)]
        ]),
        # confirm_to_process=InlineKeyboardMarkup(
        #     [[InlineKeyboardButton(context.bot.lang_dict["shop_admin_to_process_yes"],
        #     callback_data="finish_to_process"),
        #       InlineKeyboardButton(context.bot.lang_dict["shop_admin_back_btn"],
        #       callback_data="back_to_orders")]]
        # ),
        confirm_to_done=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_to_done_yes"],
                                  callback_data="finish_to_done")],
            # [InlineKeyboardButton(context.bot.lang_dict["shop_admin_add_product_btn"],
            #                       callback_data="add_product_to_order")],
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_edit_btn"],
                                  callback_data=f"edit")],
            [back_btn("back_to_orders_btn", context=context)]
        ]),
        confirm_to_trash=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_to_trash_yes"],
                                  callback_data="finish_to_trash"),
             back_btn("back_to_orders_btn", context=context)]
        ]),
        confirm_to_trash_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_to_trash_yes"],
                                  callback_data="finish_to_trash"),
             back_btn("back_to_products_btn", context=context)]
        ]),
        confirm_cancel=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_cancel_yes"],
                                  callback_data="finish_cancel"),
             back_btn("back_to_orders_btn", context=context)]
        ]),
        edit_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_add_product_btn"],
                                  callback_data="add_to_order")],
            [back_btn("back_to_orders_btn", context=context)]
        ]),
        trash_main=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_orders_btn"],
                                  callback_data="trashed_orders")],
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_products_btn"],
                                  callback_data="trashed_products")],
            [back_btn("back_to_main_menu_btn", context=context)]
        ]),
        edit_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_set_discount_btn"],
                                  callback_data='change_discount'),
             InlineKeyboardButton(context.bot.lang_dict["shop_admin_set_price_btn"],
                                  callback_data="change_price")],
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_set_description_btn"],
                                  callback_data="change_description"),
             InlineKeyboardButton(context.bot.lang_dict["shop_admin_set_name_btn"],
                                  callback_data="change_name")],
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_set_images_btn"],  # TODO 4 new buttons
                                  callback_data="change_images"),
             InlineKeyboardButton(context.bot.lang_dict["shop_admin_set_category_btn"],
                                  callback_data="change_category")],
            [InlineKeyboardButton(context.bot.lang_dict["shop_admin_set_online_btn"],
                                  callback_data="change_payment")],
            [back_btn("back_to_products_btn", context=context)]
            # [InlineKeyboardButton(strings[""])]
        ]),

    )
    return keyboards
