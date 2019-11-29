from config import conf
from telegram.ext import Updater
from modules.shop.modules.adding_product import ADD_PRODUCT_HANDLER
from modules.shop.modules.welcome import START_SHOP_HANDLER, BACK_TO_MAIN_MENU_HANDLER
from modules.shop.modules.orders import ORDERS_HANDLER
from modules.shop.modules.wholesale_orders import WHOLESALE_ORDERS_HANDLER
from modules.shop.modules.products import PRODUCTS_HANDLER
from modules.shop.modules.trash import (TRASH_START, ORDERS_TRASH,
                                WHOLESALE_TRASH, PRODUCTS_TRASH)
from modules.shop.modules.brands import BRANDS_HANDLER


def main():
    updater = Updater(conf["TOKEN"], use_context=True)
    dp = updater.dispatcher

    dp.add_handler(START_SHOP_HANDLER)
    dp.add_handler(ORDERS_TRASH)
    dp.add_handler(WHOLESALE_TRASH)
    dp.add_handler(PRODUCTS_TRASH)

    dp.add_handler(ADD_PRODUCT_HANDLER)
    dp.add_handler(ORDERS_HANDLER)
    dp.add_handler(WHOLESALE_ORDERS_HANDLER)
    dp.add_handler(PRODUCTS_HANDLER)
    dp.add_handler(TRASH_START)
    dp.add_handler(BRANDS_HANDLER)

    dp.add_handler(BACK_TO_MAIN_MENU_HANDLER)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
