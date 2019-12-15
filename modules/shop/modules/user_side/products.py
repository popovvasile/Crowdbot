import logging

from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, MessageHandler, Filters,
                          CommandHandler)

from helper_funcs.misc import delete_messages
from helper_funcs.pagination import Pagination
from modules.shop.helper.keyboards import back_kb, back_btn
from modules.shop.components.product import Product
from database import products_table
from helper_funcs.pagination import set_page_key
from modules.shop.modules.welcome import Welcome


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def users_shop_menu(update, context):
    delete_messages(update, context, True)
    users_menu_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="Магазин",
                              callback_data="open_shop"),
         InlineKeyboardButton(text="Мои покупки",
                              callback_data="users_layout")],
        [back_btn("back_to_main_menu", context=context)]
    ])
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Тут магаз",
                             reply_markup=users_menu_keyboard)
    return ConversationHandler.END


class UserProductsHandler(object):
    def products(self, update, context):
        delete_messages(update, context, True)
        set_page_key(update, context, "open_shop")
        all_products = products_table.find(
            {"in_trash": False, "sold": False}).sort([["_id", 1]])
        return self.products_layout(
            update, context, all_products, PRODUCTS)

    @staticmethod
    def products_layout(update, context, all_products, state):
        # Title
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["shop_admin_products_title"].format(all_products.count()),
                parse_mode=ParseMode.MARKDOWN))

        if all_products.count() == 0:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_no_products"],
                    reply_markup=back_kb("back_to_main_menu", context=context)))
        else:
            pagination = Pagination(
                all_products, page=context.user_data["page"], per_page=5)
            for product in pagination.content:
                Product(context, product).send_customer_template(update, context)
            pagination.send_keyboard(
                update, context, [[back_btn("back_to_main_menu", context)]])
        return state


class UserOrdersHandler(object):
    def orders(self, update, context):
        return ConversationHandler.END


PRODUCTS = range(1)

START_USER_SHOP = CommandHandler(callback=users_shop_menu, command="shop")

USERS_PRODUCTS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=UserProductsHandler().products,
                                       pattern=r"open_shop")],
    states={
        PRODUCTS: [CallbackQueryHandler(callback=UserProductsHandler().products,
                                        pattern="^[0-9]+$")]
    },
    fallbacks=[CallbackQueryHandler(callback=Welcome.back_to_main_menu,
                                    pattern=r"back_to_main_menu"),
               # CallbackQueryHandler(ProductsHandler().back_to_products,
               #                      pattern="back_to_products"),
               # CallbackQueryHandler(ProductsHandler().edit,
               #                      pattern=r"back_to_edit")
               ]
)

USERS_ORDERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=UserOrdersHandler().orders,
                                       pattern=r"users_orders")],
    states={
        PRODUCTS: [CallbackQueryHandler(callback=UserOrdersHandler().orders,
                                        pattern="^[0-9]+$")]
    },
    fallbacks=[CallbackQueryHandler(callback=Welcome.back_to_main_menu,
                                    pattern=r"back_to_main_menu"),
               # CallbackQueryHandler(ProductsHandler().back_to_products,
               #                      pattern="back_to_products"),
               # CallbackQueryHandler(ProductsHandler().edit,
               #                      pattern=r"back_to_edit")
               ]
)
