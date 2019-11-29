from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from modules.shop.helper.strings import strings, emoji


def start_keyboard(orders_quantity):
    orders_btn_text = \
        strings["orders_btn"] + \
        (f' {orders_quantity["new_orders_quantity"]}'
         if orders_quantity["new_orders_quantity"] != 0 else "")

    wholesale_orders_btn_text = \
        strings["wholesale_orders_btn"] + \
        (f' {orders_quantity["new_wholesale_orders_quantity"]}'
         if orders_quantity["new_wholesale_orders_quantity"] != 0 else "")

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["add_product_btn"],
                              callback_data="add_product")],
        [InlineKeyboardButton(orders_btn_text,
                              callback_data="orders"),
         InlineKeyboardButton(wholesale_orders_btn_text,
                              callback_data="wholesale_orders")],
        # [InlineKeyboardButton(strings["add_brand_btn"],
        # callback_data="add_brand"),
        #  InlineKeyboardButton(strings["add_category_btn"],
        #  callback_data="add_category")],
        [InlineKeyboardButton(strings["products_btn"],
                              callback_data="products"),
         InlineKeyboardButton(strings["brands_btn"],
                              callback_data="brands")],
        # [InlineKeyboardButton(strings["manage_admins_btn"],
        #                       callback_data="manage_admins")],
        [InlineKeyboardButton(strings["trash_btn"],
                              callback_data="trash")]])


sizes_list = ['XS', 'S', 'M', 'L', 'XL', 'XXL',
              # 'XXXL'
              ]


def sizes_ls(to_remove: list = None):
    return [i for i in sizes_list if i not in to_remove] \
        if to_remove else sizes_list


# Sizes Checkboxes
def sizes_checkboxes(selected_sizes, to_remove=None,
                     back_data="back_to_main_menu",
                     continue_data="set_price"):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(f"{emoji['white_check_mark']} {i}",
                               callback_data=i)]
         if i in selected_sizes else
         [InlineKeyboardButton(f"{emoji['black_square_button']} {i}",
                               callback_data=i)]
         for i in sizes_ls(to_remove)] +
        ([[back_btn(back_data)]]
         if len(selected_sizes) == 0 else
         [[InlineKeyboardButton(strings["continue_btn"],
                                callback_data=continue_data)],
          [back_btn(back_data)]]))


def show_sizes(context):
    return "\n".join(
        [f"{i['size']} - {i['count']}"
         for i in context.user_data["sizes"]])


def create_keyboard(buttons, extra_buttons):
    pairs = list(zip(buttons[::2], buttons[1::2]))
    if len(buttons) % 2 == 1:
        pairs.append((buttons[-1],))
    pairs.extend([extra_buttons])
    return InlineKeyboardMarkup(pairs)


def back_btn(callback_data: str):
    return InlineKeyboardButton(
        strings["back_btn"], callback_data=callback_data)


def back_kb(callback_data: str):
    return InlineKeyboardMarkup([[back_btn(callback_data)]])


keyboards = dict(
    back_to_main_menu_keyboard=InlineKeyboardMarkup([
        [back_btn("back_to_main_menu_btn")]
    ]),
    back_to_products=InlineKeyboardMarkup([
        [back_btn("back_to_products_btn")]
    ]),
    back_to_brands=InlineKeyboardMarkup([
        [back_btn("back_to_brands_btn")]
    ]),
    confirm_add_product=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["add_product_btn"],
                              callback_data="send_product")],
        [back_btn("back_to_main_menu_btn")]
    ]),
    continue_back_kb=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["continue_btn"],
                              callback_data="continue"),
         back_btn("back_to_main_menu_btn")]
    ]),
    # confirm_to_process=InlineKeyboardMarkup(
    #     [[InlineKeyboardButton(strings["to_process_yes"],
    #     callback_data="finish_to_process"),
    #       InlineKeyboardButton(strings["back_btn"],
    #       callback_data="back_to_orders")]]
    # ),
    confirm_to_done=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["to_done_yes"],
                              callback_data="finish_to_done")],
        # [InlineKeyboardButton(strings["add_product_btn"],
        #                       callback_data="add_product_to_order")],
        [InlineKeyboardButton(strings["edit_btn"],
                              callback_data=f"edit")],
        [back_btn("back_to_orders_btn")]
    ]),
    confirm_to_trash=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["to_trash_yes"],
                              callback_data="finish_to_trash"),
         back_btn("back_to_orders_btn")]
    ]),
    confirm_to_trash_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["to_trash_yes"],
                                  callback_data="finish_to_trash"),
             back_btn("back_to_products_btn")]
        ]),
    confirm_cancel=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["cancel_yes"],
                              callback_data="finish_cancel"),
         back_btn("back_to_orders_btn")]
    ]),
    edit_keyboard=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["add_product_btn"],
                              callback_data="add_to_order")],
        [back_btn("back_to_orders_btn")]
    ]),
    trash_main=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["orders_btn"],
                              callback_data="trashed_orders"),
         InlineKeyboardButton(strings["wholesale_orders_btn"],
                              callback_data="trashed_wholesale")],
        [InlineKeyboardButton(strings["products_btn"],
                              callback_data="trashed_products")],
        [back_btn("back_to_main_menu_btn")]
    ]),
    edit_product=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["set_discount_btn"],
                              callback_data='change_discount'),
         InlineKeyboardButton(strings["set_price_btn"],
                              callback_data="change_price")],
        [InlineKeyboardButton(strings["set_description_btn"],
                              callback_data="change_description"),
         InlineKeyboardButton(strings["set_name_btn"],
                              callback_data="change_name")],
        [InlineKeyboardButton(strings["sizes_menu_btn"],
                              callback_data="sizes_menu")],
        [back_btn("back_to_products_btn")]
        # [InlineKeyboardButton(strings[""])]
    ]),
    edit_brand=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["set_price_btn"],
                              callback_data="change_brand_price")],
        [back_btn("back_to_brands_btn")]
    ]),
    confirm_adding_sizes=InlineKeyboardMarkup([
        [InlineKeyboardButton(strings["add_size_btn"],
                              callback_data="finish_add_sizes")],
        [back_btn("back_to_products")]
    ])
)
