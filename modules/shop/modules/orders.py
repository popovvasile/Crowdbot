from telegram import (Update)
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
from modules.shop.components.product import Product
from .welcome import Welcome
from modules.shop.helper.helper import clear_user_data


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class OrdersHandler(object):
    @catch_request_exception
    def orders(self, update: Update, context: CallbackContext):
        set_page_key(update, context)
        resp = requests.get(f"{conf['API_URL']}/orders",
                            params={"page": context.user_data["page"],
                                    "per_page": 3})
        pagin = APIPaginatedPage(resp)
        pagin.start(update, context,
                    strings["orders_title"],
                    strings["no_orders"])
        for order in pagin.data["orders_data"]:
            Order(order).send_short_template(update, context)
        pagin.send_pagin(update, context)
        return ORDERS

    @catch_request_exception
    def confirm_to_done(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        set_page_key(update, context, "item_page")
        if update.callback_query.data.startswith("to_done"):
            order_id = int(update.callback_query.data.split("/")[1])
            context.user_data["order"] = Order(order_id)
        context.user_data["order"].send_full_template(
            update, context,
            strings["confirm_to_done"],
            keyboards["confirm_to_done"])
        return CONFIRM_TO_DONE

    @catch_request_exception
    def finish_to_done(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context)
        context.user_data["order"].change_status({"new_status": True})
        update.callback_query.answer(strings["moved_to_done_blink"])
        return self.back_to_orders(update, context)

    @catch_request_exception
    def confirm_cancel_order(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        set_page_key(update, context, "item_page")
        if update.callback_query.data.startswith("cancel_order"):
            order_id = int(update.callback_query.data.split("/")[1])
            context.user_data["order"] = Order(order_id)
        context.user_data["order"].send_full_template(
            update, context,
            strings["confirm_cancel"],
            keyboards["confirm_cancel"])
        return CONFIRM_CANCEL

    @catch_request_exception
    def finish_cancel(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context)
        context.user_data["order"].change_status({"new_status": False})
        update.callback_query.answer(strings["order_canceled_blink"])
        return self.back_to_orders(update, context)

    @catch_request_exception
    def confirm_to_trash(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        set_page_key(update, context, "item_page")
        order_id = int(update.callback_query.data.split("/")[1])
        context.user_data["order"] = Order(order_id)
        context.user_data["order"].send_full_template(
            update, context,
            strings["confirm_to_trash_new"],
            keyboards["confirm_to_trash"])
        return CONFIRM_TO_TRASH

    @catch_request_exception
    def finish_to_trash(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context)
        context.user_data["order"].change_status({"new_trash_status": True})
        update.callback_query.answer(strings["moved_to_trash_blink"])
        return self.back_to_orders(update, context)

    @catch_request_exception
    def edit(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        set_page_key(update, context, "item_page")
        if update.callback_query.data.startswith("edit"):
            try:
                order_id = update.callback_query.data.split("/")[1]
                context.user_data["order"] = Order(order_id)
            except IndexError:
                context.user_data["order"].refresh()
        context.user_data["order"].send_full_template(
            update, context,
            strings["edit_menu"],
            keyboards["edit_keyboard"],
            delete_kb=True)
        return EDIT

    @catch_request_exception
    def remove_item(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        item_id = update.callback_query.data.split("/")[1]
        context.user_data["order"].remove_item(item_id)
        update.callback_query.answer(strings["item_removed_blink"])
        return self.edit(update, context)

    @catch_request_exception
    def add_item(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        set_page_key(update, context, "choose_product_page")
        resp = requests.get(
            f"{conf['API_URL']}/admin_products",
            params={"page": context.user_data["choose_product_page"],
                    "per_page": 3,
                    "status": "not_sold"})
        pagin = APIPaginatedPage(resp)
        pagin.start(update, context,
                    f'{strings["choose_products_title"]}'
                    f'\n{context.user_data["order"].template}',
                    strings["no_products"])
        for product in pagin.data["products_data"]:
            product = Product(product)
            add_kb = product.add_keyboard(context.user_data["order"])
            product.send_short_template(update, context, kb=add_kb)
        pagin.send_pagin(update, context)
        return CHOOSE_PRODUCT

    @catch_request_exception
    def finish_adding_item(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        item_data = update.callback_query.data.split("/")
        item = dict(
            article=item_data[1],
            size=item_data[2]
        )
        context.user_data["order"].add_item(item)
        return self.edit(update, context)

    def back_to_orders(self, update, context):
        page = context.user_data.get("page")
        clear_user_data(context)
        context.user_data["page"] = page
        return self.orders(update, context)


ORDERS, CONFIRM_TO_PROCESS, CONFIRM_TO_DONE, \
    CONFIRM_CANCEL, CONFIRM_TO_TRASH, EDIT, \
    CHOOSE_PRODUCT = range(7)


ORDERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(OrdersHandler().orders,
                                       pattern=r"orders")],
    states={
        ORDERS: [CallbackQueryHandler(OrdersHandler().orders,
                                      pattern="^[0-9]+$"),
                 CallbackQueryHandler(OrdersHandler().confirm_to_done,
                                      pattern=r"to_done"),
                 CallbackQueryHandler(OrdersHandler().confirm_to_trash,
                                      pattern=r"to_trash"),
                 CallbackQueryHandler(OrdersHandler().confirm_cancel_order,
                                      pattern=r"cancel_order"),
                 CallbackQueryHandler(OrdersHandler().edit,
                                      pattern=r"edit")],

        CONFIRM_TO_DONE: [CallbackQueryHandler(OrdersHandler().finish_to_done,
                                               pattern=r"finish_to_done"),
                          CallbackQueryHandler(OrdersHandler().confirm_to_done,
                                               pattern="^[0-9]+$"),
                          CallbackQueryHandler(OrdersHandler().edit,
                                               pattern=r"edit")],

        CONFIRM_CANCEL: [CallbackQueryHandler(OrdersHandler().finish_cancel,
                                              pattern=r"finish_cancel"),
                         CallbackQueryHandler(OrdersHandler().confirm_cancel_order,
                                              pattern="^[0-9]+$")],

        CONFIRM_TO_TRASH: [CallbackQueryHandler(OrdersHandler().finish_to_trash,
                                                pattern=r"finish_to_trash")],

        EDIT: [CallbackQueryHandler(OrdersHandler().add_item,
                                    pattern=r"add_to_order"),
               CallbackQueryHandler(OrdersHandler().remove_item,
                                    pattern=r"remove_item"),
               CallbackQueryHandler(OrdersHandler().edit,
                                    pattern="^[0-9]+$")],

        CHOOSE_PRODUCT: [CallbackQueryHandler(OrdersHandler().finish_adding_item,
                                              pattern=r"finish_add_to_order"),
                         CallbackQueryHandler(OrdersHandler().add_item,
                                              pattern="^[0-9]+$")]
    },
    fallbacks=[CallbackQueryHandler(OrdersHandler().back_to_orders,
                                    pattern=r"back_to_orders"),
               CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu")]
)
