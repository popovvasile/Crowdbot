import logging

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, MessageHandler, Filters)

from modules.shop.helper.helper import clear_user_data
from helper_funcs.pagination import Pagination

from modules.shop.helper.keyboards import (
    keyboards, back_kb, back_btn, create_keyboard)
from modules.shop.modules.welcome import Welcome
from modules.shop.components.product import Product
from database import products_table, categories_table
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
            "in_trash": False, "bot_id": context.bot.id}).sort([["_id", 1]])
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
                prod_obj = Product(context=context, obj=product)
                prod_obj.send_full_template(
                    update, context, kb=prod_obj.admin_keyboard, text=prod_obj.description)
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

    def images(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_adding_product_start"],
            keyboards(context)["back_to_products"])
        return IMAGES

    def finish_images(self, update: Update, context: CallbackContext):  # TODO modify for multiple photos
        delete_messages(update, context, True)
        context.user_data["product"].update(
            {"images": [update.message.photo[-1].file_id]})
        return self.edit(update, context)

    def category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        category_list = categories_table.find({"bot_id": context.bot.id})
        if category_list.count() > 0:
            keyboard = create_keyboard(
                [InlineKeyboardButton(text=i["name"],
                                      callback_data=f"category_{i['_id']}")
                 for i in category_list],
                [back_btn("back_to_main_menu_btn", context)])
            context.user_data["product"].send_adding_product_template(
                update, context, context.bot.lang_dict["shop_admin_set_category"], keyboard)

        else:
            buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="back_to_main_menu")]]
            reply_markup = InlineKeyboardMarkup(
                buttons)
            context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                                     text="You didn't set any categories yet.\n"
                                          "Please write a new category",
                                     reply_markup=reply_markup)
        return CATEGORY

    def finish_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.callback_query:
            context.user_data["product"].update(
                {"category_id": update.callback_query.data.replace("category_", "")})
        else:
            if update.message:
                category_id = categories_table.insert_one({
                    "name": update.message.text,
                    "query_name": update.message.text,
                    "bot_id": context.bot.id
                }).inserted_id
                context.user_data["product"].update(
                    {"category": category_id})
        return self.edit(update, context)

    def payment(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Do you want to make this product with online payment, offline payment or both?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Online payment",
                                      callback_data="set_payment_online")],
                [InlineKeyboardButton("Offline payment",
                                      callback_data="set_payment_offline")],
                [InlineKeyboardButton("Both options",
                                      callback_data="set_payment_both")],
                [back_btn("back_to_main_menu_btn", context=context)]
            ]))
        return PAYMENT

    def finish_payment(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if "online" in update.callback_query.data:
            context.user_data["product"].update(dict(online_payment=True))
            context.user_data["product"].update(dict(offline_payment=False))
        elif "offline" in update.callback_query.data:
            context.user_data["product"].update(dict(online_payment=False))
            context.user_data["product"].update(dict(offline_payment=True))
        elif "both" in update.callback_query.data:
            context.user_data["product"].update(dict(online_payment=True))
            context.user_data["product"].update(dict(offline_payment=True))
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
 DISCOUNT_PRICE, IMAGES, CATEGORY, PAYMENT, CONFIRM_TO_TRASH, SIZES_MENU,
 SIZE_QUANTITY, SET_SIZE, SET_QUANTITY,
 CONFIRM_ADD_SIZES) = range(15)


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
                                    pattern="change_name"),
               CallbackQueryHandler(ProductsHandler().category,
                                    pattern="change_category"),
               CallbackQueryHandler(ProductsHandler().images,
                                    pattern="change_images"),
               CallbackQueryHandler(ProductsHandler().payment,
                                    pattern="change_payment"),
               ],

        CONFIRM_TO_TRASH: [CallbackQueryHandler(
                                ProductsHandler().finish_to_trash,
                                pattern=r"finish_to_trash")],
        CATEGORY: [MessageHandler(Filters.text,
                                  ProductsHandler().finish_category),
                   CallbackQueryHandler(
                       ProductsHandler().finish_category,
                       pattern=r"category_")
                   ],
        IMAGES: [MessageHandler(Filters.photo,
                                ProductsHandler().finish_images)],
        PAYMENT: [CallbackQueryHandler(
            ProductsHandler().finish_payment,
            pattern=r"set_payment_")],

        DESCRIPTION: [MessageHandler(Filters.text,
                                     ProductsHandler().finish_description)],

        NAME: [MessageHandler(Filters.text,
                              ProductsHandler().finish_name)],

        PRICE: [MessageHandler(Filters.regex("^[0-9]+$"),
                               ProductsHandler().finish_price)],

        DISCOUNT_PRICE: [MessageHandler(
            Filters.regex("^[0-9]+$"),
            ProductsHandler().finish_discount_price)],

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
