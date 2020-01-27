import logging
from pprint import pprint

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackQueryHandler
from bson.objectid import ObjectId

from helper_funcs.helper import get_help, back_to_modules
from helper_funcs.misc import delete_messages
from helper_funcs.pagination import Pagination
from database import (products_table, carts_table, chatbots_table,
                      categories_table)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

"""Where we are creating product template:
        * Cart(increase, decrease)
        * Shop
"""

class UserProductsHandler(object):
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

        all_products = products_table.find(
            {"in_trash": False,
             "sold": False,
             "bot_id": context.bot.id}).sort([["_id", -1]])
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
                        callback_data="back_to_module_shop")]]

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
                    # product_buttons[0].append(
                    #     InlineKeyboardButton(
                    #         text="View",
                    #         callback_data=f"view_product/{product['_id']}"))
                else:
                    description = product["description"]
                    # if len(product["images"]) > 1:
                    #     product_buttons[0].append(
                    #         InlineKeyboardButton(
                    #             text="View",
                    #             callback_data=f"view_product/{product['_id']}"
                    #         ))

                category = categories_table.find_one(
                    {"_id": product["category_id"]})["name"]

                product_template = ("*Article:* `{}`"
                                    "\n*Name:* `{}`"
                                    "\n*Category:* `{}`"
                                    "\n*Description:* `{}`"
                                    "\n*Price:* `{} {}`"
                                    "\n*Quantity:* `{}`").format(
                    product.get("article"),
                    product["name"],
                    category,
                    description,
                    product["price"], shop["currency"],
                    "Here must be quantity or None if quantity unlimited")

                # if product["_id"] in cart.get("product", list()):
                if any(cart_product["product_id"] == product["_id"]
                       for cart_product in cart.get("products", list())):
                    product_buttons[0].append(
                        InlineKeyboardButton(
                            text="Remove from the cart",
                            callback_data=f"remove_from_cart/{product['_id']}"
                        ))
                    product_template += "\n\nProduct already in the cart"
                    # product_reply_markup = InlineKeyboardMarkup([
                    #     [InlineKeyboardButton(
                    #         text="Remove from the cart",
                    #         callback_data=f"remove_from_cart/"
                    #                       f"{product['_id']}")]])
                else:
                    product_buttons[0].append(
                        InlineKeyboardButton(
                            text="Add",
                            callback_data=f"add_to_cart/{product['_id']}"))
                    # product_reply_markup = InlineKeyboardMarkup([
                    #     [InlineKeyboardButton(
                    #         text="Add",
                    #         callback_data=f"add_to_cart/{product['_id']}")]])

                # Send short product template
                context.user_data["to_delete"].append(
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=product["images"][0],
                        caption=product_template,
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
            update.effective_message.edit_caption(
                caption=update.effective_message.caption_markdown
                + "\n\nProduct already in the cart",
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
        update.effective_message.edit_caption(
            caption=update.effective_message.caption_markdown.replace(
                "\n\nProduct already in the cart", ""),
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
    # def back(self, update, context):
    #     delete_messages(update, context, True)
    #     context.user_data.clear()
    #     get_help(update, context)
    #     return ConversationHandler.END

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


class UserOrdersHandler(object):
    def orders(self, update, context):
        return ConversationHandler.END


class Cart(object):
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

            # cart_products = list()
        # else:
        #     cart_products = cart["products"]

        # Remove all sold and deleted products when first clicked on cart btn
        cart_products = cart["products"][:]
        if update.callback_query.data == "cart":
            for cart_product in cart["products"]:
                product = products_table.find_one(
                    {"_id": cart_product["product_id"]})
                if not product:
                    cart_products.remove(cart_product)
            if cart_products != cart["products"]:
                carts_table.update_one({"user_id": update.effective_user.id,
                                        "bot_id": context.bot.id},
                                       {"$set": {"products": cart_products}})

        if not len(cart_products):
            update.callback_query.answer("Your cart is empty")
            update.callback_query.data = "back_to_module_shop"
            return back_to_modules(update, context)

        self.send_cart_products_layout(update, context, cart_products)
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
            shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]

            for cart_product in pagination.content:
                product = products_table.find_one(
                    {"_id": cart_product["product_id"]})
                if not product:
                    continue
                # Create product reply markup
                product_buttons = [[
                    # InlineKeyboardButton(
                    #     text="➖",
                    #     callback_data=f"reduce_quantity/{product['_id']}"),
                    # InlineKeyboardButton(
                    #     text="Remove",
                    #     callback_data=f"cart_list_remove/{product['_id']}"),
                    # InlineKeyboardButton(
                    #     text="➕",
                    #     callback_data=f"add_quantity/{product['_id']}")
                ]]
                if cart_product["quantity"] > 1:
                    product_buttons[0].append(
                        InlineKeyboardButton(
                            text="➖",
                            callback_data=f"reduce_quantity/"
                                          f"{product['_id']}"))
                product_buttons[0].append(
                    InlineKeyboardButton(
                        text="Remove",
                        callback_data=f"list_cart_remove/{product['_id']}"))
                product_buttons[0].append(
                    InlineKeyboardButton(
                        text="➕",
                        callback_data=f"increase_quantity/{product['_id']}"))

                # Create product template
                if len(product["description"]) > 150:
                    description = product["description"][:150] + "..."
                    # product_buttons.append(
                    #     [InlineKeyboardButton(
                    #         text="View",
                    #         callback_data=f"view_product/{product['_id']}")])
                else:
                    description = product["description"]
                    # if len(product["images"]) > 1:
                    #     product_buttons.append(
                    #         [InlineKeyboardButton(
                    #             text="View",
                    #             callback_data=f"view_product/"
                    #                           f"{product['_id']}")])

                category = categories_table.find_one(
                    {"_id": product["category_id"]})["name"]

                product_template = ("*Article:* `{}`"
                                    "\n*Name:* `{}`"
                                    "\n*Category:* `{}`"
                                    "\n*Description:* `{}`"
                                    "\n*Price:* `{} {}`"
                                    "\n*In stock:* `{}`"
                                    "\n*Your quantity*: `{}`").format(
                    product.get("article"),
                    product["name"],
                    category,
                    description,
                    product["price"], shop["currency"],
                    "Here must be quantity or None if quantity unlimited",
                    cart_product["quantity"])

                # Send short product template
                context.user_data["to_delete"].append(
                    context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=product["images"][0],
                        caption=product_template,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=InlineKeyboardMarkup(product_buttons)))
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

    def increase_quantity(self, update, context):
        product_id = ObjectId(update.callback_query.data.split("/")[1])
        product = products_table.find_one({"_id": product_id})
        if product:
            cart = carts_table.find_one({"bot_id": context.bot.id,
                                         "user_id": update.effective_user.id})
            cart_quantity = next(i for i in cart["products"]
                                 if i["product_id"] == product_id)["quantity"]
            if cart_quantity < product.get("quantity", 500):
                # Increase product quantity
                new_quantity = cart_quantity + 1
                carts_table.find_and_modify(
                    {"_id": cart["_id"], "products.product_id": product_id},
                    {"$set": {"products.$.quantity": new_quantity}})
                update.effective_message.edit_caption(
                    caption=update.effective_message.caption_markdown.replace(
                        f"\n*Your quantity*: `{cart_quantity}`",
                        f"\n*Your quantity*: `{new_quantity}`"),
                    parse_mode=ParseMode.MARKDOWN)
                # Create product reply markup
                product_buttons = [[]]
                if new_quantity > 1:
                    product_buttons[0].append(
                        InlineKeyboardButton(
                            text="➖",
                            callback_data=f"reduce_quantity/"
                                          f"{product['_id']}"))
                product_buttons[0].append(
                    InlineKeyboardButton(
                        text="Remove",
                        callback_data=f"list_cart_remove/{product['_id']}"))
                product_buttons[0].append(
                    InlineKeyboardButton(
                        text="➕",
                        callback_data=f"increase_quantity/{product['_id']}"))

                # Create product template
                if len(product["description"]) > 150:
                    pass
                    # product_buttons.append(
                    #     [InlineKeyboardButton(
                    #         text="View",
                    #         callback_data=f"view_product/{product['_id']}")])
                else:
                    pass
                    # if len(product["images"]) > 1:
                    #     product_buttons.append(
                    #         [InlineKeyboardButton(
                    #             text="View",
                    #             callback_data=f"view_product/"
                    #                           f"{product['_id']}")])
                update.effective_message.edit_reply_markup(
                    reply_markup=InlineKeyboardMarkup(product_buttons))
            elif cart_quantity > product["quantity"]:
                # Set max quantity
                pass
            elif cart_quantity == product["quantity"]:
                update.callback_query.answer("It is max available quantity")
                # EDIT MARKUP
        else:
            # If the are no product document - remove product from cart
            carts_table.update_one(
                {"bot_id": context.bot.id,
                 "user_id": update.effective_user.id},
                {"$pull": {"products": {"product_id": product_id}}})
            update.callback_query.answer("No product")
            return self.back_to_cart(update, context)
        return ConversationHandler.END

    def reduce_quantity(self, update, context):
        pass

    def remove_from_cart(self, update, context):
        product_id = ObjectId(update.callback_query.data.split("/")[1])
        product = products_table.find_one({"_id": product_id}) or {}
        carts_table.update_one(
            {"bot_id": context.bot.id, "user_id": update.effective_user.id},
            {"$pull": {"products": {"product_id": product_id}}})
        update.callback_query.answer((product.get("name") or "")
                                     + " Removed from cart")
        return self.back_to_cart(update, context)

    def back_to_cart(self, update, context):
        delete_messages(update, context, True)
        page = context.user_data["page"]
        context.user_data.clear()
        context.user_data["page"] = page
        return self.cart(update, context)


PRODUCTS = range(1)

# PRODUCT_ASK_IF_ONLINE = CallbackQueryHandler(
#     callback=UserProductsHandler.product_menu,
#     pattern=r"product_menu")

"""SHOP"""
USERS_PRODUCTS_LIST_HANDLER = CallbackQueryHandler(
    pattern="^(open_shop|user_products_pagination)",
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

INCREASE_QUANTITY = CallbackQueryHandler(
    pattern=r"increase_quantity",
    callback=Cart().increase_quantity)


USERS_ORDERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=UserOrdersHandler().orders,
                                       pattern=r"my_orders")],
    states={
        PRODUCTS: [CallbackQueryHandler(callback=UserOrdersHandler().orders,
                                        pattern="^[0-9]+$")]
    },
    fallbacks=[CallbackQueryHandler(get_help, pattern=r"help_")]
)
