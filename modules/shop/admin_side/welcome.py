import logging

from telegram import Update
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

from modules.shop.helper.helper import clear_user_data
from modules.shop.helper.keyboards import start_keyboard
from database import orders_table
from helper_funcs.misc import delete_messages


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class Welcome(object):
    @staticmethod
    def start(update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if context.user_data.get("msg_to_send"):
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    context.user_data["msg_to_send"]))

        orders_quantity = {
            "new_orders_quantity":
                orders_table.find({"status": False,
                                   "in_trash": False}).count(),}
        context.user_data["to_delete"].append(
            context.bot.send_message(
                update.effective_chat.id,
                context.bot.lang_dict["shop_admin_start_message"],
                reply_markup=start_keyboard(orders_quantity, context)))
        return ConversationHandler.END

    @staticmethod
    def back_to_main_menu(update, context, msg_to_send=None):
        clear_user_data(context)
        if msg_to_send:
            context.user_data["msg_to_send"] = msg_to_send
        return Welcome.start(update, context)


START_SHOP_HANDLER = CallbackQueryHandler(pattern="shop_start",
                                          callback=Welcome.start)


BACK_TO_MAIN_MENU_HANDLER = CallbackQueryHandler(Welcome.back_to_main_menu,
                                                 pattern=r"back_to_main_menu")
