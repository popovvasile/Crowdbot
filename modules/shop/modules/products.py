import logging

from telegram import Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, MessageHandler, Filters)

from helper_funcs.pagination import Pagination
from modules.shop.helper.helper import clear_user_data
from modules.shop.helper.keyboards import (
    keyboards, back_kb, back_btn, create_keyboard)
from modules.shop.modules.welcome import Welcome
from modules.shop.components.product import Product
from database import products_table, categories_table
from helper_funcs.pagination import set_page_key
from helper_funcs.misc import delete_messages


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductsHandler:
    @staticmethod
    def product_keyboard(context, product_obj):
        """Create keyboard for product in "item list" and "trash list" """
        reply_markup = [[]]
        if product_obj.in_trash:
            reply_markup[0].append(
                InlineKeyboardButton(
                    text=context.bot.lang_dict["shop_admin_restore_btn"],
                    callback_data=f"restore_product/{product_obj._id}"))
            return InlineKeyboardMarkup(reply_markup)
        reply_markup[0].append(
            InlineKeyboardButton(
                text=context.bot.lang_dict["shop_admin_edit_btn"],
                callback_data=f"edit_product/{product_obj._id}"))
        if not product_obj.order_ids:
            reply_markup[0].append(
                InlineKeyboardButton(
                    text=context.bot.lang_dict["shop_admin_to_trash_btn"],
                    callback_data=f"to_trash/{product_obj._id}"))
        return InlineKeyboardMarkup(reply_markup)

    def products(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        # Set current page integer in the user_data.
        if update.callback_query.data.startswith("item_list_pagination"):
            context.user_data["page"] = int(
                update.callback_query.data.replace(
                    "item_list_pagination_", ""))
        if not context.user_data.get("page"):
            context.user_data["page"] = 1

        all_products = products_table.find({
            "in_trash": False, "bot_id": context.bot.id}).sort([["_id", -1]])
        return self.products_layout(
            update, context, all_products, PRODUCTS)

    @classmethod
    def products_layout(cls, update, context, all_products, state):
        """This Method works for the admin item list and for the item trash"""
        # Send Title
        title = context.bot.lang_dict["shop_admin_products_title"].format(
            all_products.count())
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=title,
                parse_mode=ParseMode.MARKDOWN))

        if all_products.count() == 0:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_no_products"],
                    reply_markup=back_kb(
                        "back_to_main_menu", context=context)))
        else:
            pagination = Pagination(all_products,
                                    page=context.user_data["page"])
            for product in pagination.content:
                prod_obj = Product(context=context, obj=product)
                text = prod_obj.admin_short_template
                reply_markup = cls.product_keyboard(context, prod_obj)
                prod_obj.send_short_template(
                    update, context, text=text, reply_markup=reply_markup)

            pagination.send_keyboard(
                update, context,
                [[back_btn("back_to_main_menu", context=context)]],
                page_prefix="item_list_pagination")
        return state

    def edit(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if (update.callback_query and
                update.callback_query.data.startswith("edit_product")):
            product_id = update.callback_query.data.split("/")[1]
            context.user_data["product"] = Product(context, product_id)
            # TODO fix NoneType when creating the Product object

        text = (context.user_data["product"].admin_full_template + "\n"
                + context.bot.lang_dict["shop_admin_edit_product_menu"])
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                context.bot.lang_dict["shop_admin_set_discount_btn"],
                callback_data='change_discount'),
             InlineKeyboardButton(
                 context.bot.lang_dict["shop_admin_set_price_btn"],
                 callback_data="change_price")],
            [InlineKeyboardButton(
                context.bot.lang_dict["shop_admin_set_description_btn"],
                callback_data="change_description"),
             InlineKeyboardButton(
                 context.bot.lang_dict["shop_admin_set_name_btn"],
                 callback_data="change_name")],
            [InlineKeyboardButton(
                "Content",
                callback_data="change_images"),
             InlineKeyboardButton(
                 context.bot.lang_dict["shop_admin_set_category_btn"],
                 callback_data="change_category")],
            [InlineKeyboardButton(
                context.bot.lang_dict["shop_admin_set_quantity_btn"],
                callback_data="change_quantity")],
            [InlineKeyboardButton(
                context.bot.lang_dict["back_button"],
                callback_data="back_to_products_btn")]])

        context.user_data["product"].send_full_template(
            update, context, text=text, reply_markup=reply_markup)
        return EDIT

    def description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        text = (context.user_data["product"].admin_short_template
                + "\n" + context.bot.lang_dict["shop_admin_set_description"])
        context.user_data["product"].send_short_template(
            update, context, text=text,
            reply_markup=keyboards(context)["back_to_edit"])
        return DESCRIPTION

    def finish_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].update(
            {"description": update.message.text})
        return self.edit(update, context)

    def name(self, update: Update, context: CallbackContext, msg=None):
        delete_messages(update, context, True)
        text = (context.user_data["product"].admin_short_template
                + "\n\n" + context.bot.lang_dict["shop_admin_change_name"])
        context.user_data["product"].send_short_template(
            update, context, text=text,
            reply_markup=keyboards(context)["back_to_edit"])
        if msg:
            context.bot.send_message(
                update.effective_chat.id,
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
        text = (context.user_data["product"].admin_short_template
                + "\n" + context.bot.lang_dict["shop_admin_set_price"])
        context.user_data["product"].send_short_template(
            update, context, text=text,
            reply_markup=keyboards(context)["back_to_edit"])
        return PRICE

    def finish_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].update(
            {"price": int(update.message.text)})
        return self.edit(update, context)

    def discount_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        text = (context.user_data["product"].admin_short_template + "\n"
                + context.bot.lang_dict["shop_admin_set_discount_price"])

        context.user_data["product"].send_short_template(
            update, context, text=text,
            reply_markup=keyboards(context)["back_to_edit"])
        return DISCOUNT_PRICE

    def finish_discount_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].update(
            {"discount_price": int(update.message.text)})
        return self.edit(update, context)

    # TODO edit files
    # TODO modify edit for multiple photos
    def images(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["product"].send_admin_full_template(
            update, context, context.bot.lang_dict["shop_admin_adding_product_start"],
            keyboards(context)["back_to_products"])
        return IMAGES

    def finish_images(self, update: Update, context: CallbackContext):
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
            text = (context.user_data["product"].admin_short_template + "\n\n"
                    + context.bot.lang_dict["shop_admin_set_category"])
            context.user_data["product"].send_short_template(
                update, context, text=text, reply_markup=keyboard)
        else:
            buttons = [[
                InlineKeyboardButton(
                    text=context.bot.lang_dict["back_button"],
                    callback_data="back_to_main_menu")]]
            reply_markup = InlineKeyboardMarkup(buttons)
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="You didn't set any categories yet."
                     "\nPlease write a new category",
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
                    "bot_id": context.bot.id}).inserted_id
                context.user_data["product"].update({"category": category_id})
        return self.edit(update, context)

    def confirm_to_trash(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        product_id = update.callback_query.data.split("/")[1]
        context.user_data["product"] = Product(context, product_id)

        text = (
            context.user_data["product"].admin_short_template + "\n\n"
            + context.bot.lang_dict["shop_admin_confirm_to_trash_product"])

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                context.bot.lang_dict["shop_admin_to_trash_yes"],
                callback_data="finish_to_trash"),
             InlineKeyboardButton(
                 text=context.bot.lang_dict["back_button"],
                 callback_data="back_to_products")]])

        context.user_data["product"].send_short_template(
            update, context, text=text, reply_markup=reply_markup)
        return CONFIRM_TO_TRASH

    def finish_to_trash(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context, True)
        context.user_data["product"].update({"in_trash": True})
        update.callback_query.answer(
            context.bot.lang_dict["shop_admin_moved_to_trash_blink"])
        return self.back_to_products(update, context)

    def quantity(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        text = (context.user_data["product"].short_admin_template
                + "\n\n" + context.bot.lang_dict["shop_admin_set_quantity"])
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text=context.bot.lang_dict["shop_admin_set_unlimited"],
                callback_data='quantity_unlimited')],
            [InlineKeyboardButton(
                 text=context.bot.lang_dict["back_button"],
                 callback_data="back_to_edit")]])

        context.user_data["product"].send_short_template(
            update, context, text=text, reply_markup=reply_markup)
        return SET_QUANTITY

    def finish_quantity(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.message:
            context.user_data["product"].update(
                {"quantity": int(update.message.text),
                 "unlimited": False})
        elif update.callback_query.data == 'quantity_unlimited':
            context.user_data["product"].update(
                {"quantity": 0,
                 "unlimited": True})
        return self.edit(update, context)

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
                                        pattern=r"item_list_pagination"),
                   CallbackQueryHandler(ProductsHandler().edit,
                                        pattern=r"edit_product"),
                   CallbackQueryHandler(ProductsHandler().confirm_to_trash,
                                        pattern=r"to_trash")],

        EDIT: [CallbackQueryHandler(ProductsHandler().discount_price,
                                    pattern="change_discount"),
               CallbackQueryHandler(ProductsHandler().price,
                                    pattern="change_price"),
               CallbackQueryHandler(ProductsHandler().quantity,
                                    pattern="change_quantity"),
               CallbackQueryHandler(ProductsHandler().description,
                                    pattern="change_description"),
               CallbackQueryHandler(ProductsHandler().name,
                                    pattern="change_name"),
               CallbackQueryHandler(ProductsHandler().category,
                                    pattern="change_category"),
               CallbackQueryHandler(ProductsHandler().images,
                                    pattern="change_images"),
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

        DESCRIPTION: [MessageHandler(Filters.text,
                                     ProductsHandler().finish_description)],

        NAME: [MessageHandler(Filters.text,
                              ProductsHandler().finish_name)],

        PRICE: [MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                               ProductsHandler().finish_price),
                MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                               ProductsHandler().finish_price),
                MessageHandler(Filters.regex(r"^((?!@).)*$"),
                               ProductsHandler().price)
                ],

        DISCOUNT_PRICE: [
                MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                               ProductsHandler().finish_discount_price),
                MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                               ProductsHandler().finish_discount_price),
                MessageHandler(Filters.regex(r"^((?!@).)*$"),
                               ProductsHandler().discount_price)
        ],

        SET_QUANTITY: [MessageHandler(Filters.regex("^[0-9]+$"),
                                      ProductsHandler().finish_quantity),
                       CallbackQueryHandler(ProductsHandler().finish_quantity,
                                            pattern=r'quantity_unlimited')],
    },
    fallbacks=[CallbackQueryHandler(Welcome.back_to_main_menu,
                                    pattern=r"back_to_main_menu"),
               CallbackQueryHandler(ProductsHandler().back_to_products,
                                    pattern="back_to_products"),
               CallbackQueryHandler(ProductsHandler().edit,
                                    pattern=r"back_to_edit")]
)
