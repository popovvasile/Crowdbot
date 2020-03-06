import logging
from pprint import pprint

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackQueryHandler
from bson.objectid import ObjectId

from helper_funcs.helper import get_help, back_to_modules
from helper_funcs.misc import delete_messages, get_obj
from helper_funcs.pagination import Pagination
from modules.shop.components.product import (Product,
                                             MAX_TEMP_DESCRIPTION_LENGTH)
from database import (products_table, carts_table, chatbots_table,
                      categories_table, orders_table)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

view_button_str = "🔎 View"
add_button_str = "➕ Add"
remove_button_str = "❌ Remove"


class UserProductsHelper(object):
    # TODO put this logic to the components/product -> class AdminProduct

    """All "short" templates must be passed to send_short_template() method.
    And all "full" templates must be passed to send_full_template() method.
    """

    @staticmethod
    def product_markup(cart, product):
        """Keyboard for the product in product list.

        :param cart: mongo document of the cart
        :param product: mongo document of the product

        :return: InlineKeyboardMarkup
        """
        buttons = []
        content_len = len(product["content"])

        if any(cart_product["product_id"] == product["_id"]
               for cart_product in cart.get("products", list())):
            buttons.append(
                [InlineKeyboardButton(
                    text=remove_button_str,
                    callback_data=f"remove_from_cart/{product['_id']}")])
        else:
            buttons.append(
                [InlineKeyboardButton(
                    text=add_button_str,
                    callback_data=f"add_to_cart/{product['_id']}")])

        if (len(product["description"]) > MAX_TEMP_DESCRIPTION_LENGTH
                or content_len > 1):
            buttons.append(
                [InlineKeyboardButton(
                    text=view_button_str + (f" ({content_len} files)"
                                            if content_len else ""),
                    callback_data=f"view_product_from_catalog/"
                    f"{product['_id']}")])
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def short_product_template(cart, product, currency):
        """Short customer text representation of the product.

        :param product: mongo document of the product
        :param cart: mongo document of the cart
        :param currency: currency of the shop

        :return: str
        """
        if len(product["description"]) > MAX_TEMP_DESCRIPTION_LENGTH:
            description = (
                    product["description"][:MAX_TEMP_DESCRIPTION_LENGTH] + "...")
        else:
            description = product["description"]

        category = categories_table.find_one(
            {"_id": product["category_id"]})["name"]
        if "discount_price" in product:
            template = ("<b>Article:</b>      {}"
                        "\n<b>Name:</b>       {}"
                        "\n<b>Category:</b>   {}"
                        '\n<b>New Price:</b> <b><u>{} {}</u></b>'
                        "\n<b>Old Price:</b> <s>{} {}</s>"
                        "\n<b>Description:</b>  {}").format(
                product.get("article"),
                product["name"],
                category,
                product["discount_price"], currency,
                product["price"], currency,
                description)
        else:
            template = ("<b>Article:</b>{}"
                        "\n<b>Name:</b>{}"
                        "\n<b>Category:</b> {}"
                        "\n<b>Price:</b> <b>{} {}</b>"
                        "\n<b>Description:</b> {}").format(
                product.get("article"),
                product["name"],
                category,
                product["price"], currency,
                description)

        if not product["unlimited"]:
            template += f"\n<b>Quantity:<b> `{product['quantity']}`"

        # Check if the product exist in the cart
        if any(cart_product["product_id"] == product["_id"]
               for cart_product in cart.get("products", list())):
            template += "\n\n✅ Product already in the cart"
        # Check if the product exist in the not done order
        # product_in_order = orders_table.find_one(
        #     {""})

        return template

    @staticmethod
    def full_product_template(cart, product, currency):
        """Full customer text representation of the product.

        :param product: mongo document of the product
        :param cart: mongo document of the cart
        :param currency: currency of the shop

        :return: str
        """
        category = categories_table.find_one(
            {"_id": product["category_id"]})["name"]

        if "discount_price" in product:
            template = ("*Article:* `{}`"
                        "\n*Name:* `{}`"
                        "\n*Category:* `{}`"
                        "\n*New Price:* `{} {}`"
                        "\n*Old Price:* `{} {}`").format(
                product.get("article"),
                product["name"],
                category,
                product["discount_price"], currency,
                product["price"], currency,
                )
        else:
            template = ("*Article:* `{}`"
                        "\n*Name:* `{}`"
                        "\n*Category:* `{}`"
                        "\n*Price:* `{} {}`").format(
                product.get("article"),
                product["name"],
                category,
                product["price"], currency,
                )

        if len(product["description"]) < MAX_TEMP_DESCRIPTION_LENGTH:
            template += "\n*Description:* `{}`".format(product["description"])

        if not product["unlimited"]:
            template += f"\n*Quantity:* `{product['quantity']}`"

        if any(cart_product["product_id"] == product["_id"]
               for cart_product in cart.get("products", list())):
            template += "\n\n✅ Product already in the cart"
        return template


class UserProductsHandler(UserProductsHelper):
    def categories_menu(self, update, context):

        delete_messages(update, context, True)
        categories_list_ids = [x["category_id"]
                               for x in products_table.find({"bot_id": context.bot.id})]
        categories_list = [categories_table.find_one({"_id": x})
                           for x in set(categories_list_ids)]
        categories_buttons = [
            InlineKeyboardButton(text=x["name"],
                                 callback_data=f"catalog/{x['_id']}")
            for x in categories_list]

        if categories_buttons:
            categories_reply_markup = InlineKeyboardMarkup(
                [categories_buttons[x:x + 2]for x in range(0, len(categories_buttons),2)]
                + [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="back_to_module_shop")]])

            context.user_data["to_delete"].append(
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text=context.bot.lang_dict["shop_user_choose_category"],
                                         reply_markup=categories_reply_markup))
        else:
            return self.products(update, context)
        return ConversationHandler.END

    def products(self, update, context):
        delete_messages(update, context, True)
        context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                     action="typing")
        # Set current page integer in the user_data.
        if update.callback_query.data.startswith("user_products_pagination"):
            context.user_data["page"] = int(
                update.callback_query.data.replace(
                    "user_products_pagination_", ""))
        if not context.user_data.get("page"):
            context.user_data["page"] = 1

        if update.callback_query.data.startswith("catalog"):
            context.user_data["category_id"] = ObjectId(
                update.callback_query.data.split("/")[1])

        # filters = {
        #     "in_trash": False,
        #     "sold": False,
        #     "bot_id": context.bot.id,
        #     "$or": [{'unlimited': True}, {"quantity": {"$gt": 0}}]
        # }

        # if context.user_data.get("category_id"):
        #     filters["category_id"] = context.user_data["category_id"]

        filters = {"$or": [
            {"in_trash": False,
             "bot_id": context.bot.id,
             'unlimited': True},
            {"in_trash": False,
             "bot_id": context.bot.id,
             "quantity": {"$gt": 0}}
        ]}

        if context.user_data.get("category_id"):
            filters["$or"][0]["category_id"] = (
                context.user_data["category_id"])
            filters["$or"][1]["category_id"] = (
                context.user_data["category_id"])
        pprint(filters)
        all_products = products_table.find(
            filters).sort([["last_modify_timestamp", -1]])
        self.send_products_layout(update, context, all_products)
        return ConversationHandler.END

    def send_products_layout(self, update, context, all_products):
        # Title
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict[
                    "shop_admin_products_title"].format(all_products.count()),
                parse_mode=ParseMode.MARKDOWN))
        # Products list buttons
        buttons = [[InlineKeyboardButton(
            text="🛒 Cart",
            callback_data="cart"),
            InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="back_to_categories")]]

        if all_products.count():
            # Create page content and send it
            pagination = Pagination(all_products,
                                    page=context.user_data["page"])
            shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
            cart = carts_table.find_one(
                {"bot_id": context.bot.id,
                 "user_id": update.effective_user.id}) or {}

            for product in pagination.content:
                # Send short product template
                reply_markup = self.product_markup(cart, product)
                template = self.short_product_template(cart, product,
                                                       shop["currency"])
                product_obj = Product(context, product)
                product_obj.send_short_template(
                    update, context, text=template, reply_markup=reply_markup)

            # Send main buttons
            pagination.send_keyboard(update, context,
                                     page_prefix="user_products_pagination",
                                     buttons=buttons)
        else:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_no_products"],
                    reply_markup=InlineKeyboardMarkup(buttons)))

    def add_to_cart(self, update, context):
        product_id = ObjectId(update.callback_query.data.split("/")[1])
        product = products_table.find_one({"_id": product_id})
        if product:
            cart = carts_table.find_and_modify(
                {"bot_id": context.bot.id,
                 "user_id": update.effective_user.id},
                {"$push": {"products": {"product_id": product_id,
                                        "quantity": 1}}},
                upsert=True, new=True)
            update.callback_query.answer(f"{product['name']} Added to cart")

            shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
            template = self.short_product_template(cart, product,
                                                   shop["currency"])
            if len(product["content"]) > 0:
                update.effective_message.edit_caption(
                    caption=template, parse_mode=ParseMode.MARKDOWN)
            else:
                update.effective_message.edit_text(
                    text=template, parse_mode=ParseMode.MARKDOWN)

            update.effective_message.edit_reply_markup(
                reply_markup=self.product_markup(cart, product))
        else:
            update.callback_query.answer("No product")
            return self.back_to_products(update, context)
        return ConversationHandler.END

    def remove_from_cart(self, update, context):
        product_id = ObjectId(update.callback_query.data.split("/")[1])
        product = products_table.find_one({"_id": product_id}) or {}
        cart = carts_table.find_and_modify(
            {"bot_id": context.bot.id, "user_id": update.effective_user.id},
            {"$pull": {"products": {"product_id": product_id}}}, new=True)
        update.callback_query.answer((product.get("name") or "")
                                     + " Removed from cart")

        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        template = self.short_product_template(cart, product,
                                               shop["currency"])
        if len(product["content"]) > 0:
            update.effective_message.edit_caption(
                caption=template, parse_mode=ParseMode.MARKDOWN)
        else:
            update.effective_message.edit_text(
                text=template, parse_mode=ParseMode.MARKDOWN)

        update.effective_message.edit_reply_markup(
            reply_markup=self.product_markup(cart, product))
        return ConversationHandler.END

    def view_product(self, update, context):
        """When product description is too long
        or there a few files in the product - "View" button
        """
        delete_messages(update, context, True)
        cart = carts_table.find_one({"user_id": update.effective_user.id,
                                     "bot_id": context.bot.id}) or {}
        product_id = ObjectId(update.callback_query.data.split("/")[1])
        product = products_table.find_one({"_id": product_id})
        if not product:
            return self.back_to_products(update, context)
        prod_obj = Product(context, product)
        currency = chatbots_table.find_one(
            {"bot_id": context.bot.id})["shop"]["currency"]
        template = self.full_product_template(cart, product, currency)
        back_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                  callback_data="back_to_customer_shop")]])
        prod_obj.send_full_template(
            update, context, text=template, reply_markup=back_button)

        return ConversationHandler.END

    def back_to_products(self, update, context):
        delete_messages(update, context, True)
        page = context.user_data["page"]
        category_id = context.user_data.get("category_id")
        context.user_data.clear()
        context.user_data["page"] = page
        context.user_data["category_id"] = category_id
        return self.products(update, context)

    def back_to_categories(self, update, context):
        delete_messages(update, context, True)
        context.user_data.clear()
        return self.categories_menu(update, context)


"""SHOP"""
PRODUCTS_CATEGORIES = CallbackQueryHandler(
    pattern="open_shop",
    callback=UserProductsHandler().categories_menu)

USERS_PRODUCTS_LIST_HANDLER = CallbackQueryHandler(
    pattern="^(catalog|user_products_pagination)",
    callback=UserProductsHandler().products)

ADD_TO_CART = CallbackQueryHandler(
    pattern=r"add_to_cart",
    callback=UserProductsHandler().add_to_cart)

REMOVE_FROM_CART = CallbackQueryHandler(
    pattern=r"remove_from_cart",
    callback=UserProductsHandler().remove_from_cart)

VIEW_PRODUCT = CallbackQueryHandler(
    pattern=r"view_product_from_catalog",
    callback=UserProductsHandler().view_product)

"""BACKS"""
BACK_TO_CATEGORIES = CallbackQueryHandler(
    pattern=r"back_to_categories",
    callback=UserProductsHandler().back_to_categories)

BACK_TO_CUSTOMER_SHOP = CallbackQueryHandler(
    pattern=r"back_to_customer_shop",
    callback=UserProductsHandler().back_to_products)
