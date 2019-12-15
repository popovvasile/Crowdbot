from telegram import Update
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

from helper_funcs.misc import delete_messages
from modules.shop.helper.helper import clear_user_data
from modules.shop.helper.decorator import catch_request_exception
from modules.shop.helper.pagination import APIPaginatedPage, set_page_key
import requests
import logging
from config import conf
from modules.shop.components.wholesale_order import WholesaleOrder
from .welcome import Welcome


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class WholesaleOrdersHandler(object):
    @catch_request_exception
    def wholesale_orders(self, update: Update, context: CallbackContext):
        set_page_key(update, context)
        resp = requests.get(f"{conf['API_URL']}/wholesale_orders",
                            params={"page": context.user_data["page"],
                                    "per_page": 3})
        pagin = APIPaginatedPage(resp)
        pagin.start(update, context,
                    context.bot.lang_dict["shop_admin_orders_title"],
                    context.bot.lang_dict["shop_admin_no_orders"])
        for order in pagin.data["data"]:
            WholesaleOrder(order).send_template(update, context)
        pagin.send_pagin(update, context)
        return WHOLESALE_ORDERS

    @catch_request_exception
    def change_status(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context)
        order_id = int(update.callback_query.data.split("/")[1])
        if update.callback_query.data.startswith("to_done"):
            json = {"new_status": True}
            blink = context.bot.lang_dict["shop_admin_moved_to_done_blink"]
        elif update.callback_query.data.startswith("to_trash"):
            json = {"new_trash_status": True}
            blink = context.bot.lang_dict["shop_admin_moved_to_trash_blink"]
        elif update.callback_query.data.startswith("cancel_order"):
            json = {"new_status": False}
            blink = context.bot.lang_dict["shop_admin_order_canceled_blink"]
        else:
            return self.wholesale_orders(update, context)
        WholesaleOrder(order_id).change_status(json)
        update.callback_query.answer(blink)
        return self.wholesale_orders(update, context)

    """"@catch_request_exception
    def move_to_done(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(
            update.effective_chat.id, "typing")
        delete_messages(update, context)
        order_id = update.callback_query.data.split("/")[1]
        WholesaleOrder(order_id=order_id).change_status({"new_status": True})
        update.callback_query.answer(context.bot.lang_dict["shop_admin_moved_to_done_blink"])
        return self.wholesale_orders(update, context)

    @catch_request_exception
    def move_to_trash(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(
            update.effective_chat.id, "typing")
        delete_messages(update, context)
        order_id = update.callback_query.data.split("/")[1]
        WholesaleOrder(order_id=order_id).change_status(
            {"new_trash_status": True})
        update.callback_query.answer(context.bot.lang_dict["shop_admin_moved_to_trash_blink"])
        return self.wholesale_orders(update, context)

    @catch_request_exception
    def cancel_order(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(
            update.effective_chat.id, "typing")
        delete_messages(update, context)
        order_id = update.callback_query.data.split("/")[1]
        WholesaleOrder(order_id=order_id).change_status({"new_status": True})
        update.callback_query.answer(context.bot.lang_dict["shop_admin_moved_to_trash_blink"])
        return self.wholesale_orders(update, context)"""

    def back_to_wholesale_orders(self, update: Update, context: CallbackContext):
        page = context.user_data.get("page")
        clear_user_data(context)
        context.user_data["page"] = page
        return self.wholesale_orders(update, context)


WHOLESALE_ORDERS = range(1)


WHOLESALE_ORDERS_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(WholesaleOrdersHandler().wholesale_orders,
                             pattern=r"wholesale_orders")],
    states={
        WHOLESALE_ORDERS: [
            CallbackQueryHandler(WholesaleOrdersHandler().wholesale_orders,
                                 pattern='^[0-9]+$'),
            CallbackQueryHandler(WholesaleOrdersHandler().change_status,
                                 pattern=r"to_done"),
            CallbackQueryHandler(WholesaleOrdersHandler().change_status,
                                 pattern=r"to_trash"),
            CallbackQueryHandler(WholesaleOrdersHandler().change_status,
                                 pattern=r"cancel_order")]
    },
    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu")]
)
