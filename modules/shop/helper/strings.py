# Telegram emoji. Original names
emoji = dict(
    trash="🗑",
    recycle="♻️",
    white_check_mark="✅",
    hammer_and_wrench="🛠",
    x="❌",
    black_square_button="🔲",
    confused="😕",
    arrow_down="⬇️",
    arrow_right="➡️",
    money_with_wings="💸",
    gift_heart="💝",
    page_with_curl="📃",
    ticket="🎫",
    shirt="👔",
    ballot_box="🗳",
    plus="➕",
    gear="⚙️"
)

strings = dict(
    # MAIN MENU
    start_message="👋 Добро пожаловать в админку",
    add_product_btn=f"{emoji['plus']} Добавить товар",
    # delete_product_btn="➖ Удалить товар",
    orders_btn="📩 Заказы",
    # add_brand_btn="👚 Добавить бренд",
    brands_btn=f"{emoji['shirt']} Бренды",
    # add_category_btn="👜 Добавить категорию",
    products_btn="🗳 Товары",
    trash_btn="🗑 Корзина",
    manage_admins_btn=f"{emoji['gear']} Управлять админам",
    size_quantity="\n\n _Выбери количество_ *{}* _размера_",
    # ADDING PRODUCT
    adding_product_start="Отправьте изображение товара",
    send_more_photo="Отправь ещe изображение или продолжай"
                    "\nДобавлено {} файлов",
    continue_btn=f"Продолжить {emoji['arrow_right']}",
    set_brand="Выберите бренд товара",
    set_category="Выберете категерию товара",
    set_sizes="Укажите размеры товара",
    set_price=f"{emoji['money_with_wings']} *Укажите цену товара*",
    price_is_not_int="Цена должна быть целым числом."
                     "\nПришлите цену товара",
    set_description="\n_Напишите описание товара_",
    confirm_add_product="Добавить товар в магазин?",
    adding_product_finished="🤘 Товар успешно добавлен",

    # ORDERS HANDLER
    no_orders="Ещё нет ни одного заказа",
    orders_title="*Список заказов*"
                 "\n_Количество заказов:_ `{}`"
                 f"\n{emoji['white_check_mark']} - "
                 f"_Отметить заказ как выполненный. "
                 "Товар с заказа будет убран с "
                 "магазина и отмечен как проданый_"
                 f"\n{emoji['trash']} - _Удалить заказ_"
                 f"\n{emoji['x']} - _Отменить выполненный заказ."
                 f"Товар с заказа будет возвращён на полки магазина_",
    order_temp="*Id Заказа:* `{}`"
               "\n*Время:* `{}`"
               "\n*Статус заказа:* `{}`"
               "\n\n*Имя:* `{}`"
               "\n*Номер:* `{}`"
               "\n*Цена:* `{}`"
               "\n\n*Товар:\n*"
               "{}",
    order_status_new="🔴 Новый",
    # order_status_false="♻️️ В процессе",
    order_status_true=f"{emoji['white_check_mark']} Выполненный",
    all_products_exist="👌🏿 Все продукты в наличии",
    some_product_not_exist="📛 Некоторых товаров уже нет в наличии",
    empty_order="⚠️ Пустой заказ",
    # product_status_true="В наличии ✅",
    # product_status_false="Нет в наличии ⛔",
    # to_process_btn="♻",
    to_done_btn=emoji["white_check_mark"],
    to_trash_btn=emoji['trash'],
    cancel_btn=emoji["x"],
    edit_btn=emoji["hammer_and_wrench"],
    # confirm_to_process="*Уверены что хотите поместить данный заказ "
    #                    "в обработку??*"
    #                    "\n_Весь товар с заказа будет убран с магазина и
    #                    будет ожидать своего покупателя."
    #                    "\nВы сможете в дальнейшем отменить данный
    #                    заказ и товар вернёться на полки"
    #                    " интернет магазина_",
    # to_process_yes="♻ В Обратобку",
    confirm_to_done="*Уверены что хотите отметить данный заказ "
                    "как выполненный??*"
                    "\n_Товар с заказа будет убран с магазина "
                    "и отмечен как проданный."
                    "\nВы сможете в дальнейшем отменить данный заказ "
                    "и товар вернёться на полки"
                    " интернет магазина_",
    to_done_yes=f"{emoji['white_check_mark']} В Выполненные",
    confirm_to_trash_new="*Уверены что хотите удалить данный заказ??*"
                         "\n_Данный заказ является новым и не обработаным."
                         "\nУдаление данного заказа "
                         "не влечёт никаких изменений."
                         "\nУбедитесь что клиент точно отказался от покупки_",
    # confirm_to_trash_process="*Уверены что хотите отменить данный заказ??*"
    #                      "\n_Данный заказ находится в обработке."
    #                      "\nВесь товар будет возвращён
    #                      на полки интернет магазина."
    #                      "\nУбедитесь что клиент точно
    #                      отказался от покупки_",
    # confirm_to_trash_done="*Уверены что хотите отменить данный заказ??*"
    #                       "\n_Данный заказ находится в выполненых."
    #                       "\nВесь товар будет возвращён
    #                       на полки интернет магазина.",
    to_trash_yes="🗑 В Корзину",
    confirm_cancel="*Уверены что хотите отменить данный заказ??*"
                         "\n_Данный заказ является выполненным."
                         "\nОтмена данного заказа вернёт товар на "
                         "полки магазина и переместит заказ в Новые."
                         "\nУбедитесь что клиент точно отказался от покупки_",
    cancel_yes=f"{emoji['x']} Отменить",
    edit_menu="*Заказ не может быть завершён пока в "
              "нём присутствуют проданные товары.*"
              f"\n{emoji['x']} - _Убрать товар из заказа_",
    # EDIT ORDER
    choose_products_title="*Выбирите товар для добавления в заказ*"
                          "\n_Количество товаров:_ `{}`",

    # PRODUCTS HANDLER
    no_products="В магазине ещё нет товаров",
    products_title="*Список товаров*"
                   "\n_Количество товаров:_ `{}`",
    product_template="*Артикул Товара:* `{}`"
                     "\n*Наличие:* `{}`"
                     "\n*Бренд:* `{}`"
                     "\n*Категория:* `{}`"
                     "\n*Цена:* `{}`"
                     "\n*Размеры*: \n{}",
    full_product_template="*Артикул Товара:* `{}`"
                          "\n*Наличие:* `{}`"
                          "\n*Имя*: `{}`"
                          "\n*Бренд:* `{}`"
                          "\n*Категория:* `{}`"
                          "\n*Описание*: `{}`"
                          "\n*Цена:* `{}`"
                          "\n*Скидочная цена:* `{}`"
                          "\n*Размеры*: \n{}",
    product_temp_for_order_item="*Артикул Товара:* `{}`"
                                "\n*На складе:*\n `{}`"
                                "\n*Бренд:* `{}`"
                                "\n*Категория:* `{}`"
                                "\n*Цена:* `{}`"
                                "\n*Размер*: \n{}",
    confirm_to_trash_product="*Уверены что хотите удалить данный товар??*"
                             "\n_С данным товаром отсутсвуют заказы._",
    # EDIT PRODUCT
    edit_product_menu="\n_Тут можно редактировать товар_",
    set_discount_btn=f"{emoji['gift_heart']} Скидка",
    set_price_btn=f"{emoji['money_with_wings']} Цена",
    set_description_btn=f"{emoji['page_with_curl']} Описание",
    set_name_btn=f"{emoji['ticket']} Имя",

    change_name="*Введите новое имя для товара*",
    name_length_error="*В имени должно быть не больше 1000 символов в длину*",
    description_below=f"Описание ниже {emoji['arrow_down']}",
    set_discount_price=f"{emoji['gift_heart']} "
                       f"*Укажите скидочную цену для товара*",
    sizes_menu_title="\n*Здесь вы можете управлять размерами*",
    product_size_temp="*Размер:* `{}` | *Количество*: `{}`",
    sizes_menu_btn=f"{emoji['ballot_box']} Размеры",
    add_size_btn=f"{emoji['plus']} Добавить размер",
    set_new_sizes="\n*Укажите новые размеры*",
    # BRANDS
    brands_title="*Список брендов*"
                 "\n_Количество брендов:_ `{}`",
    no_brands="_Пакажи мнэ брэнд, ааааа хачу_",
    edit_brand_menu="\n_Тут можно редактировать бренд_",
    brand_template="*Имя:* `{}`"
                   "\n*Цена:* `{}`",
    set_brand_price=f"{emoji['money_with_wings']} "
                    f"*Укажите цену за кг бренда*",

    # TRASH
    trash_start=f"{emoji['trash']} *Тут хранятся удалённые вещи*",
    trash_orders_title=f"{emoji['trash']} *Список удалённых заказов*"
                       "\n_Количество заказов:_ `{}`",
    restore_btn=f"{emoji['recycle']} Восстановить",

    # BLINKS
    # moved_to_process_blink="♻ Заказ успешно помещён в обработку",
    moved_to_done_blink=f"{emoji['white_check_mark']} "
                        f"Заказ успешно помещён в выполненные",
    moved_to_trash_blink="🗑 Заказ успешно помещён в корзину",
    order_canceled_blink=f"{emoji['x']} Заказ успешно отменён",
    item_removed_blink="Товар успешно удалён из заказа",
    item_added_blink=f"{emoji['white_check_mark']} "
                     f"Товар успешно добавлен в заказ",
    order_restored_blink=f"{emoji['recycle']} Заказ восстановлён",
    product_restored_blink=f"{emoji['white_check_mark']} "
                           f"Товар снова в продаже",
    size_removed_blink="Размер удалён",
    sizes_added_blink=f"{emoji['white_check_mark']} "
                      f"Размеры успешно добавлены",
    # description_changed_blink=f"{emoji['white_check_mark']} "
    #                            "Описание успешно изменено",
    # EXCEPTIONS
    api_off=f"{emoji['confused']} Апи сейчас не работает - "
            f"обратитесь в поддержку",
    exception_in_adding_product=f"{emoji['confused']} "
                                f"Обнаружен сбой при обработке изображения. "
                                f"Обратитесь к Юре",
    image_exception=f"{emoji['confused']} "
                    f"Не удалось отправить изображение товара."
                    "\n_Проверьте товар в магазине по артикулу_",
    image_brand_exception=f"{emoji['confused']} "
                          f"Не удалось отправить лого бренда."
                           "\n_Проверьте лого бренда в магазине_",
    something_gone_wrong=f"{emoji['confused']} Видимо что-то пошло не так."
                         "\nОбратитесь в поддержку",
    timed_out=f"{emoji['confused']} Превышено время ожидания",
    try_later="\nПопробуйте начать позже -> /start",
    # PAGINATION
    current_page="*Текущая траница:* `{}`",
    # BACK BUTTON
    back_btn="🔙 Назад",
)


def boolmoji(boolean: bool):
    emoji_yes = "✅"
    emoji_no = '🔲'
    # emoji_no = '☑️'
    return emoji_yes if boolean else emoji_no


def ordermoji(order):
    new_order_emoji = "🔴"
    # processed_order_emoji = "♻️"
    done_order_emoji = "✅"

    """if order["status"] == -1:
        return new_order_emoji
    elif order["status"] == 0:
        return processed_order_emoji
    elif order["status"] == 1:
        return done_order_emoji"""
    if order["status"] is False:
        return new_order_emoji
    elif order["status"] is True:
        return done_order_emoji

