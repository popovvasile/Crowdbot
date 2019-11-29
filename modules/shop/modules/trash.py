from telegram import ParseMode, Update
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext)
from modules.shop.helper.helper import delete_messages
from modules.shop.helper.decorator import catch_request_exception
from modules.shop.helper.pagination import APIPaginatedPage, set_page_key
import requests
import logging
from modules.shop.helper.strings import strings
from modules.shop.helper.keyboards import keyboards
from config import conf
from modules.shop.components.order import Order
from modules.shop.components.wholesale_order import WholesaleOrder
from modules.shop.components.product import Product
from .welcome import Welcome
from modules.shop.helper.helper import clear_user_data


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class TrashHandler(Welcome):
    def start_trash(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.context.user_data["to_delete"].append(
            context.context.bot.send_message(
                update.effective_chat.id,
                strings["trash_start"],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards["trash_main"]))
        return ConversationHandler.END

    @catch_request_exception
    def orders(self, update: Update, context: CallbackContext):
        set_page_key(update, context)
        resp = requests.get(f"{conf['API_URL']}/orders",
                            params={"page": context.context.user_data["page"],
                                    "per_page": 3,
                                    "show_trash": 1})
        pagin = APIPaginatedPage(resp)
        pagin.start(update, context,
                    strings["trash_orders_title"],
                    strings["no_orders"])
        for order in pagin.data["orders_data"]:
            Order(order).send_short_template(update, context)
        pagin.send_pagin(update, context, back_button_data="back_to_trash")
        return ORDERS

    @catch_request_exception
    def restore_order(self, update: Update, context: CallbackContext):
        context.context.bot.send_chat_action(update.effective_chat.id, "typing")
        order_id = int(update.callback_query.data.split("/")[1])
        Order(order_id).change_status({"new_trash_status": False})
        update.callback_query.answer(strings["order_restored_blink"])
        return self.back_to_orders(update, context)

    @catch_request_exception
    def wholesale_orders(self, update: Update, context: CallbackContext):
        set_page_key(update, context)
        resp = requests.get(f"{conf['API_URL']}/wholesale_orders",
                            params={"page": context.context.user_data["page"],
                                    "per_page": 3,
                                    "trash": True})
        pagin = APIPaginatedPage(resp)
        pagin.start(update, context,
                    strings["trash_orders_title"],
                    strings["no_orders"])
        for order in pagin.data["data"]:
            WholesaleOrder(order).send_template(update, context)
        pagin.send_pagin(update, context, back_button_data="back_to_trash")
        return WHOLESALE_ORDERS

    @catch_request_exception
    def restore_wholesale(self, update: Update, context: CallbackContext):
        context.context.bot.send_chat_action(update.effective_chat.id, "typing")
        order_id = int(update.callback_query.data.split("/")[1])
        WholesaleOrder(order_id).change_status({"new_trash_status": False})
        update.callback_query.answer(strings["order_restored_blink"])
        return self.back_to_wholesale_orders(update, context)

    def products(self, update: Update, context: CallbackContext):
        set_page_key(update, context)
        resp = requests.get(f"{conf['API_URL']}/admin_products",
                            params={"page": context.context.user_data["page"],
                                    "per_page": 3,
                                    "trash": True
                                    })
        pagin = APIPaginatedPage(resp)
        pagin.start(update, context,
                    strings["products_title"],
                    strings["no_products"])
        for product in pagin.data["products_data"]:
            Product(product).send_short_template(update, context, kb=True)
        pagin.send_pagin(update, context)
        return PRODUCTS

    def restore_product(self, update: Update, context: CallbackContext):
        context.context.bot.send_chat_action(
            update.effective_chat.id, "typing")
        order_id = int(update.callback_query.data.split("/")[1])
        Product(order_id).edit({"new_trash_status": False})
        update.callback_query.answer(strings["product_restored_blink"])
        return self.back_to_products(update, context)

    def back_to_orders(self, update, context):
        page = context.context.user_data.get("page")
        clear_user_data(context)
        context.context.user_data["page"] = page
        return self.orders(update, context)

    def back_to_wholesale_orders(self, update, context):
        page = context.context.user_data.get("page")
        clear_user_data(context)
        context.context.user_data["page"] = page
        return self.wholesale_orders(update, context)

    def back_to_products(self, update, context):
        page = context.context.user_data.get("page")
        clear_user_data(context)
        context.context.user_data["page"] = page
        return self.products(update, context)

    def back_to_trash(self, update, context):
        page = context.context.user_data.get("page")
        clear_user_data(context)
        context.context.user_data["page"] = page
        return self.start_trash(update, context)


ORDERS, WHOLESALE_ORDERS, PRODUCTS = range(3)


fallbacks = [CallbackQueryHandler(TrashHandler().back_to_main_menu,
                                  pattern=r"back_to_main_menu"),
             CallbackQueryHandler(TrashHandler().start_trash,
                                  pattern=r"back_to_trash")]


TRASH_START = CallbackQueryHandler(TrashHandler().start_trash,
                                   pattern=r"trash")


ORDERS_TRASH = ConversationHandler(
    entry_points=[CallbackQueryHandler(TrashHandler().orders,
                                       pattern=r"trashed_orders")],
    states={
        ORDERS: [CallbackQueryHandler(TrashHandler().orders,
                                      pattern=r"^[0-9]+$"),
                 CallbackQueryHandler(TrashHandler().restore_order,
                                      pattern=r"restore")]
    },
    fallbacks=fallbacks
)


WHOLESALE_TRASH = ConversationHandler(
    entry_points=[CallbackQueryHandler(TrashHandler().wholesale_orders,
                                       pattern=r"trashed_wholesale")],
    states={
        WHOLESALE_ORDERS: [
            CallbackQueryHandler(TrashHandler().wholesale_orders,
                                 pattern=r"^[0-9]+$"),
            CallbackQueryHandler(TrashHandler().restore_wholesale,
                                 pattern=r"restore_wholesale")],
    },
    fallbacks=fallbacks
)

PRODUCTS_TRASH = ConversationHandler(
    entry_points=[CallbackQueryHandler(TrashHandler().products,
                                       pattern=r"trashed_products")],
    states={
        PRODUCTS: [CallbackQueryHandler(TrashHandler().products,
                                        pattern=r"^[0-9]+$"),
                   CallbackQueryHandler(TrashHandler().restore_product,
                                        pattern=r"restore_product")],
    },
    fallbacks=fallbacks
)
