import time


# In Linux or UNIX:
# time python yourprogram.py


def dict_test():
    keyboards = []
    """buttons = dict(
        back_to_main_menu_btn=InlineKeyboardButton(
            strings["back_btn"], callback_data="back_to_main_menu"),
        back_to_orders_btn=InlineKeyboardButton(
            strings["back_btn"], callback_data="back_to_orders"),
        back_to_products_btn=InlineKeyboardButton(
            strings["back_btn"], callback_data="back_to_products"),
        back_to_brands_btn=InlineKeyboardButton(
            strings["back_btn"], callback_data="back_to_brands")
    )

    keyboards = dict(
        back_to_main_menu_keyboard=InlineKeyboardMarkup([
            [buttons["back_to_main_menu_btn"]]
        ]),
        back_to_products=InlineKeyboardMarkup([
            [buttons["back_to_products_btn"]]
        ]),
        back_to_brands=InlineKeyboardMarkup([
            [buttons["back_to_brands_btn"]]
        ]),
        confirm_add_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["add_product_btn"], callback_data="send_product")],
            [buttons["back_to_main_menu_btn"]]
        ]),
        continue_back_kb=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["continue_btn"], callback_data="continue"),
             buttons["back_to_main_menu_btn"]]
        ]),
        # confirm_to_process=InlineKeyboardMarkup(
        #     [[InlineKeyboardButton(strings["to_process_yes"], callback_data="finish_to_process"),
        #       InlineKeyboardButton(strings["back_btn"], callback_data="back_to_orders")]]
        # ),
        confirm_to_done=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["to_done_yes"], callback_data="finish_to_done")],
            # [InlineKeyboardButton(strings["add_product_btn"],
            #                       callback_data="add_product_to_order")],
            [InlineKeyboardButton(strings["edit_btn"], callback_data=f"edit")],
            [buttons["back_to_orders_btn"]]
        ]),
        confirm_to_trash=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["to_trash_yes"], callback_data="finish_to_trash"),
             buttons["back_to_orders_btn"]]
        ]),
        confirm_to_trash_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["to_trash_yes"], callback_data="finish_to_trash"),
             buttons["back_to_orders_btn"]]
        ]),
        confirm_cancel=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["cancel_yes"], callback_data="finish_cancel"),
             buttons["back_to_orders_btn"]]
        ]),
        edit_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["add_product_btn"], callback_data="add_to_order")],
            [buttons["back_to_orders_btn"]]
        ]),
        trash_main=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["orders_btn"], callback_data="trashed_orders"),
             InlineKeyboardButton(strings["wholesale_orders_btn"], callback_data="trashed_wholesale")],
            [InlineKeyboardButton(strings["products_btn"], callback_data="trashed_products")],
            [buttons["back_to_main_menu_btn"]]
        ]),
        edit_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["set_discount_btn"], callback_data='change_discount'),
             InlineKeyboardButton(strings["set_price_btn"], callback_data="change_price")],
            [InlineKeyboardButton(strings["set_description_btn"], callback_data="change_description"),
             InlineKeyboardButton(strings["set_name_btn"], callback_data="change_name")],
            [buttons["back_to_products_btn"]]
            # [InlineKeyboardButton(strings[""])]
        ]),
        edit_brand=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["set_price_btn"], callback_data="change_brand_price")],
            [buttons["back_to_brands_btn"]]
        ]),
    )"""
    ls = []
    for i in range(5):
        a = [i for i in keyboards]
        ls.append(a)
    return ls


def func_test():
    keyboards = []
    """
    def back_btn(callback_data: str):
        return InlineKeyboardButton(
            strings["back_btn"], callback_data=callback_data)
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
            [InlineKeyboardButton(strings["add_product_btn"], callback_data="send_product")],
            [back_btn("back_to_main_menu_btn")]
        ]),
        continue_back_kb=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["continue_btn"], callback_data="continue"),
             back_btn("back_to_main_menu_btn")]
        ]),
        # confirm_to_process=InlineKeyboardMarkup(
        #     [[InlineKeyboardButton(strings["to_process_yes"], callback_data="finish_to_process"),
        #       InlineKeyboardButton(strings["back_btn"], callback_data="back_to_orders")]]
        # ),
        confirm_to_done=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["to_done_yes"], callback_data="finish_to_done")],
            # [InlineKeyboardButton(strings["add_product_btn"],
            #                       callback_data="add_product_to_order")],
            [InlineKeyboardButton(strings["edit_btn"], callback_data=f"edit")],
            [back_btn("back_to_orders_btn")]
        ]),
        confirm_to_trash=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["to_trash_yes"], callback_data="finish_to_trash"),
             back_btn("back_to_orders_btn")]
        ]),
        confirm_to_trash_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["to_trash_yes"], callback_data="finish_to_trash"),
             back_btn("back_to_products_btn")]
        ]),
        confirm_cancel=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["cancel_yes"], callback_data="finish_cancel"),
             back_btn("back_to_orders_btn")]
        ]),
        edit_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["add_product_btn"], callback_data="add_to_order")],
            [back_btn("back_to_orders_btn")]
        ]),
        trash_main=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["orders_btn"], callback_data="trashed_orders"),
             InlineKeyboardButton(strings["wholesale_orders_btn"], callback_data="trashed_wholesale")],
            [InlineKeyboardButton(strings["products_btn"], callback_data="trashed_products")],
            [back_btn("back_to_main_menu_btn")]
        ]),
        edit_product=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["set_discount_btn"], callback_data='change_discount'),
             InlineKeyboardButton(strings["set_price_btn"], callback_data="change_price")],
            [InlineKeyboardButton(strings["set_description_btn"], callback_data="change_description"),
             InlineKeyboardButton(strings["set_name_btn"], callback_data="change_name")],
            [back_btn("back_to_products_btn")]
            # [InlineKeyboardButton(strings[""])]
        ]),
        edit_brand=InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["set_price_btn"], callback_data="change_brand_price")],
            [back_btn("back_to_brands_btn")]
        ]),
    )"""
    ls = []
    for i in range(5):
        a = [i for i in keyboards]
        ls.append(a)
    return ls


def test():
    # print(Order(order_id=3).all_items_exists)

    print("DICT")
    start_time = time.time()
    dict_test()
    print(time.time() - start_time)

    print("FUNC")
    start_time = time.time()
    func_test()
    print(time.time() - start_time)


if __name__ == "__main__":

    test()