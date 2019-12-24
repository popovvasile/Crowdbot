import logging

from telegram import Update, ParseMode
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, MessageHandler, Filters)

from modules.shop.helper.helper import clear_user_data
from helper_funcs.pagination import Pagination

from modules.shop.helper.keyboards import (
    keyboards, back_kb, back_btn)
from modules.shop.modules.welcome import Welcome
from modules.shop.components.product import Product
from database import products_table
from helper_funcs.pagination import set_page_key
from helper_funcs.misc import delete_messages


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductsHandler:
    def products(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        set_page_key(update, context, "products")
        all_products = products_table.find({
            "in_trash": False}).sort([["_id", 1]])
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
                all_products, per_page=5)
            for product in pagination.content:
                Product(context=context, obj=product).send_admin_short_template(
                    update, context, kb=True)
            pagination.send_keyboard(
                update, context, [[back_btn("back_to_main_menu", context=context)]])
        return state

    def edit(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if (update.callback_query and
                update.callback_query.data.startswith("edit_product")):
            product_id = update.callback_query.data.split("/")[1]
            context.user_data["product"] = Product(context, product_id)
            # TODO fix NoneType when creating the Product object
        context.user_data["product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_edit_product_menu"],
            keyboards(context)["edit_product"])
        return EDIT

    def description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_set_description"],
            keyboards(context)["back_to_products"])
        return DESCRIPTION

    def finish_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].update(
            {"description": update.message.text})
        return self.edit(update, context)

    def name(self, update: Update, context: CallbackContext, msg=None):
        delete_messages(update, context, True)
        context.user_data["product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_change_name"],
            keyboards(context)["back_to_products"])
        if msg:
            context.bot.send_message(update.effective_chat.id,
                                     context.bot.lang_dict["shop_admin_name_length_error"])
        return NAME

    def finish_name(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if len(update.message.text) > 1000:
            return self.name(update, context, msg=True)
        context.user_data["product"].update({"name": update.message.text})
        return self.edit(update, context)

    def price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_set_price"],
            keyboards(context)["back_to_products"])
        return PRICE

    def finish_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].update(
            {"price": int(update.message.text)})
        return self.edit(update, context)

    def discount_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_set_discount_price"],
            keyboards(context)["back_to_products"])
        return DISCOUNT_PRICE

    def finish_discount_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].update(
            {"discount_price": int(update.message.text)})
        return self.edit(update, context)

    def confirm_to_trash(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        product_id = update.callback_query.data.split("/")[1]
        context.user_data["product"] = Product(context, product_id)
        context.user_data["product"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_confirm_to_trash_product"],
            keyboards(context)["confirm_to_trash_product"])
        return CONFIRM_TO_TRASH

    def finish_to_trash(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context, True)
        context.user_data["product"].update({"in_trash": True})
        update.callback_query.answer(context.bot.lang_dict["shop_admin_moved_to_trash_blink"])
        return self.back_to_products(update, context)

    def set_new_quantity(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)

        return SET_QUANTITY

    def back_to_products(self, update: Update, context: CallbackContext):
        page = context.user_data.get("page")
        clear_user_data(context)
        context.user_data["page"] = page
        return self.products(update, context)


(PRODUCTS, EDIT, DESCRIPTION, NAME,  PRICE,
 DISCOUNT_PRICE, CONFIRM_TO_TRASH, SIZES_MENU,
 SIZE_QUANTITY, SET_SIZE, SET_QUANTITY,
 CONFIRM_ADD_SIZES) = range(12)


PRODUCTS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(ProductsHandler().products,
                                       pattern=r"products")],
    states={
        PRODUCTS: [CallbackQueryHandler(ProductsHandler().products,
                                        pattern="^[0-9]+$"),
                   CallbackQueryHandler(ProductsHandler().edit,
                                        pattern=r"edit_product"),
                   CallbackQueryHandler(ProductsHandler().confirm_to_trash,
                                        pattern=r"to_trash")],

        EDIT: [CallbackQueryHandler(ProductsHandler().discount_price,
                                    pattern="change_discount"),
               CallbackQueryHandler(ProductsHandler().price,
                                    pattern="change_price"),
               CallbackQueryHandler(ProductsHandler().description,
                                    pattern="change_description"),
               CallbackQueryHandler(ProductsHandler().name,
                                    pattern="change_name")],

        CONFIRM_TO_TRASH: [CallbackQueryHandler(
                                ProductsHandler().finish_to_trash,
                                pattern=r"finish_to_trash")],

        DESCRIPTION: [MessageHandler(Filters.text,
                                     ProductsHandler().finish_description)],

        NAME: [MessageHandler(Filters.text,
                              ProductsHandler().finish_name)],

        PRICE: [MessageHandler(Filters.regex("^[0-9]+$"),
                               ProductsHandler().finish_price)],

        DISCOUNT_PRICE: [MessageHandler(
            Filters.regex("^[0-9]+$"),
            ProductsHandler().finish_discount_price)],

        SET_SIZE: [CallbackQueryHandler(ProductsHandler().set_new_quantity,
                                        pattern="set_quantity"),
                   CallbackQueryHandler(ProductsHandler().back_to_products,
                                        pattern="back_to_products")],

        SET_QUANTITY: [MessageHandler(Filters.regex("^[0-9]+$"),
                                      ProductsHandler().set_new_quantity)],
    },
    fallbacks=[CallbackQueryHandler(Welcome.back_to_main_menu,
                                    pattern=r"back_to_main_menu"),
               CallbackQueryHandler(ProductsHandler().back_to_products,
                                    pattern="back_to_products"),
               CallbackQueryHandler(ProductsHandler().edit,
                                    pattern=r"back_to_edit")]
)
