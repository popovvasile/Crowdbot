import logging

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (ConversationHandler, CallbackQueryHandler)

from helper_funcs.helper import get_help
from helper_funcs.misc import delete_messages
from helper_funcs.pagination import Pagination
from modules.shop.helper.keyboards import back_kb, back_btn
from modules.shop.components.product import Product
from database import products_table
from helper_funcs.pagination import set_page_key


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class UserProductsHandler(object):
    def products(self, update, context):
        delete_messages(update, context, True)
        set_page_key(update, context, "open_shop")
        all_products = products_table.find(
            {"in_trash": False, "sold": False, "bot_id": context.bot.id}).sort([["_id", 1]])
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
                    reply_markup=back_kb("help_module(shop)", context=context)))
        else:
            pagination = Pagination(
                all_products, page=context.user_data["page"], per_page=5)
            for product in pagination.content:
                Product(context, product).send_customer_template(update, context)
            pagination.send_keyboard(
                update, context, [[back_btn("help_module(shop)", context)]])
        return state

    @staticmethod
    def product_menu(update, context):
        product_id = update.callback_query.data.replace("product_menu/", "")
        context.bot.send_message(update.callback_query.message.chat.id,
                                 text=context.bot.lang_dict["online_offline_payment"],
                                 reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton(text=context.bot.lang_dict["online_buy"],
                                                            callback_data="online_buy/{}".format(product_id))],
                                      [InlineKeyboardButton(text=context.bot.lang_dict["offline_buy"],
                                                            callback_data="offline_buy/{}".format(product_id))],
                                      [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                            callback_data="help_back")],
                                      ]))


class UserOrdersHandler(object):
    def orders(self, update, context):
        return ConversationHandler.END


PRODUCTS = range(1)

PRODUCT_ASK_IF_ONLINE = CallbackQueryHandler(callback=UserProductsHandler.product_menu,
                                             pattern=r"product_menu")

USERS_PRODUCTS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=UserProductsHandler().products,
                                       pattern=r"open_shop")],
    states={
        PRODUCTS: [CallbackQueryHandler(callback=UserProductsHandler().products,
                                        pattern="^[0-9]+$")]
    },
    fallbacks=[CallbackQueryHandler(get_help, pattern=r"help_")]
)

USERS_ORDERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=UserOrdersHandler().orders,
                                       pattern=r"my_orders")],
    states={
        PRODUCTS: [CallbackQueryHandler(callback=UserOrdersHandler().orders,
                                        pattern="^[0-9]+$")]
    },
    fallbacks=[CallbackQueryHandler(get_help, pattern=r"help_")]
)
