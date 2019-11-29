from telegram import Update
from telegram.ext import (CommandHandler, ConversationHandler,
                          CallbackQueryHandler, CallbackContext)

from modules.shop.helper.helper import delete_messages, clear_user_data
import requests
from requests.exceptions import ConnectionError
import logging
from modules.shop.helper.strings import strings
from modules.shop.helper.keyboards import start_keyboard
from config import conf

logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Welcome(object):
    @staticmethod
    def start(update: Update, context: CallbackContext):
        delete_messages(update, context)
        print(update.effective_user.id)
        if context.context.user_data.get("msg_to_send"):
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(
                    update.effective_chat.id,
                    context.context.user_data["msg_to_send"]))
        try:
            orders_quantity = requests.get(
                f"{conf['API_URL']}/orders_quantity")
        except ConnectionError:
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(
                    update.effective_chat.id,
                    strings["api_off"] + strings["try_later"]))
            return ConversationHandler.END
        if orders_quantity.status_code == 200:
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(
                    update.effective_chat.id,
                    strings["start_message"],
                    reply_markup=start_keyboard(orders_quantity.json())))
        else:
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(
                    update.effective_chat.id,
                    strings["something_gone_wrong"] + strings["try_later"]))
        return ConversationHandler.END

    @staticmethod
    def back_to_main_menu(update, context, msg_to_send=None):
        clear_user_data(context)
        if msg_to_send:
            context.context.user_data["msg_to_send"] = msg_to_send
        return Welcome.start(update, context)


START_SHOP_HANDLER = CallbackQueryHandler(pattern="shop_start", callback=Welcome().start,
                                          # filters=Filters.chat(conf["ADMINS"])
                                          )

BACK_TO_MAIN_MENU_HANDLER = CallbackQueryHandler(Welcome().back_to_main_menu,
                                                 pattern=r"back_to_main_menu")
