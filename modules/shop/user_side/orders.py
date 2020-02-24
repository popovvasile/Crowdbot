import logging
from pprint import pprint

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler, CallbackQueryHandler
from bson.objectid import ObjectId

from helper_funcs.helper import get_help, back_to_modules
from helper_funcs.misc import delete_messages, get_obj
from helper_funcs.pagination import Pagination
from modules.shop.components.order import UserOrder
from modules.shop.user_side.cart import CartHelper
from database import (products_table, carts_table, chatbots_table,
                      categories_table, orders_table)


class UserOrdersHandler(object):
    def orders(self, update, context):
        delete_messages(update, context, True)
        context.bot.send_chat_action(chat_id=update.effective_chat.id,
                                     action="typing")
        # Set current page integer in the user_data.
        if update.callback_query.data.startswith("user_orders_pagination"):
            context.user_data["page"] = int(
                update.callback_query.data.replace("user_orders_pagination_",
                                                   ""))
        if not context.user_data.get("page"):
            context.user_data["page"] = 1

        # Get orders
        orders = orders_table.find(
            {"user_id": update.effective_user.id,
             "bot_id": context.bot.id}).sort([["_id", -1]])

        # Back to the shop menu if no order
        if not orders.count():
            update.callback_query.answer("There are no orders yet")
            update.callback_query.data = "back_to_module_shop"
            return back_to_modules(update, context)
        # Send page content
        self.send_orders_layout(update, context, orders)
        return ConversationHandler.END

    def send_orders_layout(self, update, context, orders):
        # Title
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="*Your Orders* - `{}`".format(orders.count()),
                parse_mode=ParseMode.MARKDOWN))
        # Orders list buttons
        buttons = [[InlineKeyboardButton(
            text=context.bot.lang_dict["back_button"],
            callback_data="back_to_module_shop")]]

        if orders.count():
            # Create page content and send it
            pagination = Pagination(orders, page=context.user_data["page"])

            for order in pagination.content:
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton(
                        text="Order Items",
                        callback_data=f"order_items/{order['_id']}")]])
                # template = ("\n*Order number:* `{}`"
                #             "\n*Order status:* `{}`"
                #             "\n*Order price:* `{}` {}"
                #             "\n*Your phone number:* `{}`").format(
                #                 order.get("article"),
                #                 order["status"],
                #                 order["total_price"], order["currency"],
                #                 order["phone_number"])
                # if order["shipping"]:
                #     template += f"\n*Delivery to* `{order['address']}`"
                # else:
                #     shop = chatbots_table.find_one(
                #         {"bot_id": context.bot.id})["shop"]
                #     template += f"\n*Pick up from* `{shop['address']}`"
                context.user_data["to_delete"].append(
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=UserOrder(context, order).template,
                        parse_mode=ParseMode.HTML,
                        reply_markup=reply_markup))
            # Send main buttons
            pagination.send_keyboard(update, context,
                                     page_prefix="user_orders_pagination",
                                     buttons=buttons)
        else:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="No Orders",
                    reply_markup=InlineKeyboardMarkup(buttons)))

    def order_items(self, update, context):
        delete_messages(update, context, True)
        order_id = ObjectId(update.callback_query.data.split("/")[1])
        order = orders_table.find_one({"_id": order_id})
        if not order:
            return self.orders(update, context)
        currency = chatbots_table.find_one(
            {"bot_id": context.bot.id})["shop"]["currency"]
        for order_item in order["items"]:
            text = CartHelper.short_cart_item_template(order_item, currency)


"""ORDERS"""
USERS_ORDERS_LIST_HANDLER = CallbackQueryHandler(
    pattern=r"^(my_orders|user_orders_pagination)",
    callback=UserOrdersHandler().orders)