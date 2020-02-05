import logging
from pprint import pprint

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackQueryHandler
from bson.objectid import ObjectId

from helper_funcs.helper import get_help, back_to_modules
from helper_funcs.misc import delete_messages, get_obj
from helper_funcs.pagination import Pagination
from database import (products_table, carts_table, chatbots_table,
                      categories_table)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


class UserProductsHandler(object):
    def categories_menu(self, update, context):
        delete_messages(update, context, True)
        categories_buttons = [
            InlineKeyboardButton(text=x["name"],
                                 callback_data=f"category/{x['_id']}")
            for x in categories_table.find({"bot_id": context.bot.id})]

        if categories_buttons:
            categories_reply_markup = InlineKeyboardMarkup([
                categories_buttons[x:x+2]
                for x in range(0, len(categories_buttons), 2)]
                + [[InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="back_to_module_shop")]])

            context.user_data["to_delete"].append(
                context.bot.send_message(chat_id=update.effective_chat.id,
                                         text="Choose category",
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

        if update.callback_query.data.startswith("category"):
            context.user_data["category_id"] = ObjectId(
                update.callback_query.data.split("/")[1])

        filters = {"in_trash": False,
                   "sold": False,
                   "bot_id": context.bot.id}
        if context.user_data.get("category_id"):
            filters["category_id"] = context.user_data["category_id"]

        all_products = products_table.find(filters).sort([["_id", -1]])
        self.send_products_layout(update, context, all_products)
        return ConversationHandler.END

    @staticmethod
    def send_products_layout(update, context, all_products):
        # Title
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict[
                    "shop_admin_products_title"].format(all_products.count()),
                parse_mode=ParseMode.MARKDOWN))
        # Products list buttons
        buttons = [[InlineKeyboardButton(
                        text="Cart",
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
                product_buttons = [[]]

                # Create product template
                if len(product["description"]) > 150:
                    description = product["description"][:150] + "..."
                    product_buttons[0].append(
                        InlineKeyboardButton(
                            text="View",
                            callback_data=f"view_product/{product['_id']}"))
                else:
                    description = product["description"]
                    if len(product["images"]) > 1:
                        product_buttons[0].append(
                            InlineKeyboardButton(
                                text="View",
                                callback_data=f"view_product/{product['_id']}"
                            ))

                category = categories_table.find_one(
                    {"_id": product["category_id"]})["name"]

                product_template = (
                    "*Article:* `{}`"
                    "\n*Name:* `{}`"
                    "\n*Category:* `{}`"
                    "\n*Description:* `{}`"
                    "\n*Price:* `{} {}`").format(
                        product.get("article"),
                        product["name"],
                        category,
                        description,
                        product["price"], shop["currency"])
                if not product.get("unlimited"):
                    product_template += (
                        f"\n*Quantity:* `{product['quantity']}`")

                if any(cart_product["product_id"] == product["_id"]
                       for cart_product in cart.get("products", list())):
                    product_buttons[0].append(
                        InlineKeyboardButton(
                            text="Remove from the cart",
                            callback_data=f"remove_from_cart/{product['_id']}"
                        ))
                    product_template += "\n\n✅ Product already in the cart"
                else:
                    product_buttons[0].append(
                        InlineKeyboardButton(
                            text="Add",
                            callback_data=f"add_to_cart/{product['_id']}"))

                # Send short product template
                if len(product["images"]) > 0:
                    context.user_data["to_delete"].append(
                        context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=product["images"][0],
                            caption=product_template,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=InlineKeyboardMarkup(product_buttons)))
                else:
                    context.user_data["to_delete"].append(
                        context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=product_template,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=InlineKeyboardMarkup(product_buttons)))
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
            carts_table.update_one(
                {"bot_id": context.bot.id,
                 "user_id": update.effective_user.id},
                {"$push": {"products": {"product_id": product_id,
                                        "quantity": 1}}},
                upsert=True)
            update.callback_query.answer(f"{product['name']} Added to cart")
            if len(product["images"]) > 0:
                update.effective_message.edit_caption(
                    caption=update.effective_message.caption_markdown
                    + "\n\n✅ Product already in the cart",
                    parse_mode=ParseMode.MARKDOWN)

            else:
                update.effective_message.edit_text(
                    text=update.effective_message.text_markdown
                    + "\n\n✅ Product already in the cart",
                    parse_mode=ParseMode.MARKDOWN)
            update.effective_message.edit_reply_markup(
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text="Remove from the cart",
                        callback_data=f"remove_from_cart/{product_id}")]]))
        else:
            update.callback_query.answer("No product")
            return self.back_to_products(update, context)
        return ConversationHandler.END

    @staticmethod
    def remove_from_cart(update, context):
        product_id = ObjectId(update.callback_query.data.split("/")[1])
        product = products_table.find_one({"_id": product_id}) or {}
        carts_table.update_one(
            {"bot_id": context.bot.id, "user_id": update.effective_user.id},
            {"$pull": {"products": {"product_id": product_id}}})
        update.callback_query.answer((product.get("name") or "")
                                     + " Removed from cart")
        if len(product["images"]) > 0:
            update.effective_message.edit_caption(
                caption=update.effective_message.caption_markdown.replace(
                    "\n\n✅ Product already in the cart", ""),
                parse_mode=ParseMode.MARKDOWN)
        else:
            update.effective_message.edit_text(
                text=update.effective_message.text_markdown.replace(
                    "\n\n✅ Product already in the cart", ""),
                parse_mode=ParseMode.MARKDOWN)
        update.effective_message.edit_reply_markup(
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    text="Add",
                    callback_data=f"add_to_cart/{product_id}")]]))
        return ConversationHandler.END

    def back_to_products(self, update, context):
        delete_messages(update, context, True)
        page = context.user_data["page"]
        context.user_data.clear()
        context.user_data["page"] = page
        return self.products(update, context)

    def back_to_categories(self, update, context):
        delete_messages(update, context, True)
        context.user_data.clear()
        return self.categories_menu(update, context)


class UserOrdersHandler(object):
    def orders(self, update, context):
        return ConversationHandler.END


class CartHelper(object):
    @staticmethod
    def validate_cart_item(cart, product) -> dict:
        """Check if the product exist and check product quantity

        * when cart opened from main menu button("Cart")
        * when change quantity

        :param cart: ObjectId or string _id of the cart or cart dict
        :param product: ObjectId or string _id of the product or product dict
        :return: empty dict if product doesn't exist, sold of deleted
            or dict with data if item exist and correct
        """
        cart = get_obj(carts_table, cart)
        product = get_obj(products_table, product)

        if not product or product["in_trash"] or product["sold"]:
            carts_table.update_one(
                {"_id": cart["_id"]},
                {"$pull": {"products": {"product_id": product["_id"]}}})
            return dict()

        cart_item = next((i for i in cart["products"]
                          if i["product_id"] == product["_id"]), None)
        if not cart_item:
            return dict()
        # If cart item quantity bigger than product
        # set cart item quantity to maximum count
        if (not product.get("unlimited")
                and cart_item["quantity"] > int(product["quantity"])):
            cart_item["quantity"] = int(product["quantity"])
            carts_table.find_and_modify(
                {"_id": cart["_id"], "products.product_id": product["_id"]},
                {"$set": {"products.$.quantity": int(product["quantity"])}})
        cart_item["product"] = product
        return cart_item

    @staticmethod
    def cart_item_template(cart_item, currency) -> str:
        """
        :param cart_item: {
            "product_id": ObjectId,  # Object id of the product
            "quantity": int,  # Cart product quantity
            "product": dict  # Product document
        }
        :param currency: shop currency
        """
        # Create product template
        if len(cart_item["product"]["description"]) > 150:
            description = cart_item["product"]["description"][:150] + "..."
        else:
            description = cart_item["product"]["description"]
        category_name = categories_table.find_one(
            {"_id": cart_item["product"]["category_id"]})["name"]

        template = (
            "*Article:* `{}`"
            "\n*Name:* `{}`"
            "\n*Category:* `{}`"
            "\n*Description:* `{}`"
            "\n*Price:* `{} {}`").format(
                cart_item["product"].get("article"),
                cart_item["product"]["name"],
                category_name,
                description,
                float(cart_item["product"]["price"]) * cart_item["quantity"],
                currency)
        if not cart_item["product"].get("unlimited"):
            template += f"\n*In stock:* `{cart_item['product']['quantity']}`"
        template += f"\n*Your quantity*: `{cart_item['quantity']}`"
        return template

    @staticmethod
    def cart_item_markup(cart_item):
        """Keyboard for the cart item.
        Product must exist in the cart and quantity must be correct

        :param cart_item: {
            "product_id": ObjectId,  # Object id of the product
            "quantity": int,  # Cart quantity
            "product": dict  # product document
        }
        :return: InlineKeyboardMarkup
        """
        product_buttons = [[]]
        if cart_item["quantity"] > 1:
            product_buttons[0].append(
                InlineKeyboardButton(
                    text="➖",
                    callback_data=f"reduce_quantity/"
                                  f"{cart_item['product_id']}"))
        product_buttons[0].append(
            InlineKeyboardButton(
                text="Remove",
                callback_data=f"list_cart_remove/{cart_item['product_id']}"))

        plus_button = InlineKeyboardButton(
            text="➕",
            callback_data=f"increase_quantity/{cart_item['product_id']}")
        if cart_item["product"].get("unlimited"):
            product_buttons[0].append(plus_button)
        elif cart_item["quantity"] < int(cart_item["product"]["quantity"]):
            product_buttons[0].append(plus_button)

        if (len(cart_item["product"]["description"]) > 150
                or len(cart_item["product"]["images"]) > 1):
            product_buttons.append(
                [InlineKeyboardButton(
                    text="View",
                    callback_data=f"view_product/{cart_item['product_id']}")])
        return InlineKeyboardMarkup(product_buttons)


class Cart(CartHelper):
    def cart(self, update, context):
        delete_messages(update, context, True)
        context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                     action="typing")
        # Set current page integer in the user_data.
        if update.callback_query.data.startswith("user_cart_pagination"):
            context.user_data["page"] = int(
                update.callback_query.data.replace("user_cart_pagination_",
                                                   ""))
        if not context.user_data.get("page"):
            context.user_data["page"] = 1
        # Get cart products
        cart = carts_table.find_one({"user_id": update.effective_user.id,
                                     "bot_id": context.bot.id})
        if not cart:
            inserted_id = carts_table.insert_one(
                {"user_id": update.effective_user.id,
                 "bot_id": context.bot.id,
                 "products": list()}).inserted_id
            cart = carts_table.find_one({"_id": inserted_id})
        # when cart opened from main menu button check all cart products
        elif update.callback_query.data == "cart":
            for cart_item in cart["products"]:
                self.validate_cart_item(cart, cart_item["product_id"])
            cart = carts_table.find_one({"user_id": update.effective_user.id,
                                         "bot_id": context.bot.id})

        # Back to the shop menu if cart is empty
        if not len(cart["products"]):
            update.callback_query.answer("Your cart is empty")
            update.callback_query.data = "back_to_module_shop"
            return back_to_modules(update, context)
        # Send page content
        self.send_cart_products_layout(update, context, cart["products"])
        return ConversationHandler.END

    def send_cart_products_layout(self, update, context, cart_products):
        # Title
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict[
                    "shop_admin_products_title"].format(len(cart_products)),
                parse_mode=ParseMode.MARKDOWN))
        # Products list buttons
        buttons = [[InlineKeyboardButton(
                        text=context.bot.lang_dict["back_button"],
                        callback_data="back_to_module_shop")]]

        if len(cart_products):
            buttons.insert(0, [InlineKeyboardButton(
                                   text="Make Order",
                                   callback_data="make_order")])
            # Create page content and send it
            pagination = Pagination(cart_products,
                                    page=context.user_data["page"])
            currency = chatbots_table.find_one(
                {"bot_id": context.bot.id})["shop"]["currency"]

            for cart_item in pagination.content:
                product = products_table.find_one(
                    {"_id": cart_item["product_id"]})
                if not product:
                    continue
                # Create product reply markup and send short product template
                cart_item["product"] = product
                reply_markup = self.cart_item_markup(cart_item)
                template = self.cart_item_template(cart_item, currency)
                if len(product["images"]) > 0:
                    context.user_data["to_delete"].append(
                        context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=product["images"][0],
                            caption=template,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=reply_markup))
                else:
                    context.user_data["to_delete"].append(
                        context.bot.send_message(
                            chat_id=update.effective_chat.id,
                            text=template,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=reply_markup))
            # Send main buttons
            pagination.send_keyboard(update, context,
                                     page_prefix="user_cart_pagination",
                                     buttons=buttons)
        else:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_no_products"],
                    reply_markup=InlineKeyboardMarkup(buttons)))

    def change_quantity(self, update, context):
        operation, product_id = update.callback_query.data.split("/")
        cart = carts_table.find_one({"bot_id": context.bot.id,
                                     "user_id": update.effective_user.id})
        cart_item = self.validate_cart_item(cart, product_id)

        if cart_item:
            if (operation == "increase_quantity"
                    and cart_item["quantity"] <
                    int(cart_item["product"]["quantity"])):
                # new_quantity = cart_item["quantity"] + 1
                cart_item["quantity"] += 1
            elif operation == "reduce_quantity" and cart_item["quantity"] > 1:
                # new_quantity = cart_item["quantity"] - 1
                cart_item["quantity"] -= 1
            else:
                return self.back_to_cart(update, context)

            carts_table.find_and_modify(
                {"_id": cart["_id"],
                 "products.product_id": cart_item["product_id"]},
                {"$set": {"products.$.quantity": cart_item["quantity"]}})

            currency = chatbots_table.find_one(
                {"bot_id": context.bot.id})["shop"]["currency"]
            if update.effective_message.caption_markdown:
                update.effective_message.edit_caption(
                    caption=self.cart_item_template(cart_item, currency),
                    parse_mode=ParseMode.MARKDOWN)
            else:
                update.effective_message.edit_text(
                    text=self.cart_item_template(cart_item, currency),
                    parse_mode=ParseMode.MARKDOWN)

            update.effective_message.edit_reply_markup(
                reply_markup=self.cart_item_markup(cart_item))
        else:
            return self.back_to_cart(update, context)

    def remove_from_cart(self, update, context):
        product_id = ObjectId(update.callback_query.data.split("/")[1])
        product = products_table.find_one({"_id": product_id}) or {}
        carts_table.update_one(
            {"bot_id": context.bot.id, "user_id": update.effective_user.id},
            {"$pull": {"products": {"product_id": product_id}}})
        update.callback_query.answer((product.get("name") or "")
                                     + " Removed from cart")
        return self.back_to_cart(update, context)

    def make_order(self, update, context):
        delete_messages(update, context, True)
        # Prepare cart items for order
        cart = carts_table.find_one({"bot_id": context.bot.id,
                                     "user_id": update.effective_user.id})
        cart_items = list()
        for cart_item in cart["products"]:
            cart_item = self.validate_cart_item(cart, cart_item["product_id"])
            if cart_item:
                cart_items.append(cart_item)
        if not cart_items:
            return self.back_to_cart(update, context)
        # Create order template
        shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
        order_template = "*Your Order*\n\n"
        order_price = 0
        for cart_item in cart_items:
            item_price = (float(cart_item["product"]["price"])
                          * cart_item["quantity"])
            order_price += item_price
            order_template += (
                "{} - `{}`\n"
                " x{} - `{}` {}\n\n").format(
                    cart_item["product"].get("article"),
                    cart_item["product"]["name"],
                    cart_item["quantity"],
                    item_price,
                    shop["currency"])
        order_template += f"*Order Price:* `{order_price}` {shop['currency']}"
        # Save order data. Need to check order data on each step??
        context.user_data["order"] = dict()
        context.user_data["order"]["items"] = cart_items
        context.user_data["order"]["total_price"] = order_price
        context.user_data["order"]["currency"] = shop['currency']
        # Create reply markup
        buttons = []
        if shop["shop_type"] == "offline":
            buttons.append(
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["offline_buy"],
                    callback_data=f"offline_buy")])
        elif shop["shop_type"] == "online":
            buttons.append(
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["online_buy"],
                    callback_data=f"online_buy")])
        buttons.append(
            [InlineKeyboardButton(
                text=context.bot.lang_dict["back_button"],
                callback_data="back_to_cart")])
        # Send order template
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=order_template,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(buttons)))
        return ConversationHandler.END

    def back_to_cart(self, update, context):
        delete_messages(update, context, True)
        page = context.user_data.get("page", 1)
        context.user_data.clear()
        context.user_data["page"] = page
        return self.cart(update, context)


PRODUCTS = range(1)

# PRODUCT_ASK_IF_ONLINE = CallbackQueryHandler(
#     callback=UserProductsHandler.product_menu,
#     pattern=r"product_menu")

# @staticmethod
# def product_menu(update, context):
#     product_id = update.callback_query.data.replace("product_menu/", "")
#     context.bot.send_message(update.callback_query.message.chat.id,
#                              text=context.bot.lang_dict["online_offline_payment"],
#                              reply_markup=InlineKeyboardMarkup(
#                                  [[InlineKeyboardButton(text=context.bot.lang_dict["online_buy"],
#                                                         callback_data="online_buy/{}".format(product_id))],
#                                   [InlineKeyboardButton(text=context.bot.lang_dict["offline_buy"],
#                                                         callback_data="offline_buy/{}".format(product_id))],
#                                   [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
#                                                         callback_data="help_back")],
#                                   ]))

"""SHOP"""
PRODUCTS_CATEGORIES = CallbackQueryHandler(
    pattern="open_shop",
    callback=UserProductsHandler().categories_menu)

USERS_PRODUCTS_LIST_HANDLER = CallbackQueryHandler(
    pattern="^(category|user_products_pagination)",
    callback=UserProductsHandler().products)

ADD_TO_CART = CallbackQueryHandler(
    pattern=r"add_to_cart",
    callback=UserProductsHandler().add_to_cart)

REMOVE_FROM_CART = CallbackQueryHandler(
    pattern=r"remove_from_cart",
    callback=UserProductsHandler().remove_from_cart)

"""CART"""
CART = CallbackQueryHandler(
    pattern="^(cart|user_cart_pagination)",
    callback=Cart().cart)

REMOVE_FROM_CART_LIST = CallbackQueryHandler(
    pattern=r"list_cart_remove",
    callback=Cart().remove_from_cart)

CHANGE_QUANTITY = CallbackQueryHandler(
    pattern=r"^(increase_quantity|reduce_quantity)",
    callback=Cart().change_quantity)

MAKE_ORDER = CallbackQueryHandler(
    pattern="make_order",
    callback=Cart().make_order)

"""BACKS"""
BACK_TO_CART = CallbackQueryHandler(
    pattern="back_to_cart",
    callback=Cart().back_to_cart)

BACK_TO_CATEGORIES = CallbackQueryHandler(
    pattern=r"back_to_categories",
    callback=UserProductsHandler().back_to_categories)

# USERS_ORDERS_HANDLER = ConversationHandler(
#     entry_points=[CallbackQueryHandler(callback=UserOrdersHandler().orders,
#                                        pattern=r"my_orders")],
#     states={
#         PRODUCTS: [CallbackQueryHandler(callback=UserOrdersHandler().orders,
#                                         pattern="^[0-9]+$")]
#     },
#     fallbacks=[CallbackQueryHandler(get_help, pattern=r"help_")]
# )
