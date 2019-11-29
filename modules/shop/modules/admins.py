from telegram import Update
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext)
from modules.shop.helper.helper import delete_messages
import logging
from .welcome import Welcome

logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class AdminsHandler:
    def start(self, update: Update, context: CallbackContext):
        delete_messages(update, context)


ADMINS = range(1)


ADMINS_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(AdminsHandler().start,
                             pattern=r"manage_admins")],
    states={
        ADMINS: []
    },
    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu")]
)