from bson.objectid import ObjectId
from telegram import (Update, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (ConversationHandler, CallbackQueryHandler, CallbackContext)

from helper_funcs.pagination import Pagination
from helper_funcs.misc import delete_messages
from modules.shop.helper.keyboards import keyboards, back_kb, back_btn
from modules.shop.helper.helper import clear_user_data
from modules.shop.components.order import AdminOrder
from modules.shop.components.product import Product
from modules.shop.admin_side.welcome import Welcome
from database import orders_table, products_table


class OrdersHandlerHelper(object):
    @staticmethod
    def order_reply_markup(context, order):
        kb = [[]]
        if order.in_trash:
            return None

        if order.status is False:
            if len(order.items):
                kb[0].append(
                    InlineKeyboardButton(
                        text=context.bot.lang_dict["done_button_short"],
                        callback_data=f"to_done/{order.id_}"))
        kb[0].append(
            InlineKeyboardButton(
                text=context.bot.lang_dict["cancel_button"],
                callback_data=f"cancel_order/{order.id_}"))
        return InlineKeyboardMarkup(kb)


class OrdersHandler(OrdersHandlerHelper):
    def orders(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        # Set current page integer in the user_data.
        if update.callback_query.data.startswith("admin_order_list_pagination"):
            context.user_data["page"] = int(
                update.callback_query.data.replace("admin_order_list_pagination_", ""))
        if not context.user_data.get("page"):
            context.user_data["page"] = 1

        all_orders = orders_table.find(
            {"bot_id": context.bot.id,
             "in_trash": False}).sort([["_id", -1], ["status", -1]])
        return self.orders_layout(update, context, all_orders, ORDERS)

    def orders_layout(self, update, context, all_orders, state):
        """This Method works for the admin item list and for the item trash"""
        # Title
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=context.bot.lang_dict["shop_admin_orders_title"].format(
                    all_orders.count()),
                parse_mode=ParseMode.HTML))

        if all_orders.count() == 0:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_no_orders"],
                    reply_markup=back_kb("back_to_main_menu",
                                         context=context)))
        else:
            pagination = Pagination(all_orders,
                                    page=context.user_data["page"])
            for order in pagination.content:
                order = AdminOrder(context, order)
                order.send_short_template(
                    update, context,
                    reply_markup=self.order_reply_markup(context, order))

            pagination.send_keyboard(
                update, context,
                text=context.bot.lang_dict["user_orders_title"].format(
                    all_orders.count()),
                buttons=[[back_btn("back_to_main_menu", context=context)]],
                page_prefix="admin_order_list_pagination")
        return state


    def confirm_to_done(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.callback_query.data.startswith("admin_order_item_pagination"):
            context.user_data["item_page"] = int(
                update.callback_query.data.replace("admin_order_item_pagination_", ""))
        if not context.user_data.get("item_page"):
            context.user_data["item_page"] = 1
        if update.callback_query.data.startswith("to_done"):
            order_id = update.callback_query.data.split("/")[1]
            context.user_data["order"] = AdminOrder(context, order_id)
        context.user_data["order"].send_full_template(
            update, context,
            text=context.bot.lang_dict["shop_admin_confirm_to_done"],
            reply_markup=keyboards(context)["confirm_to_done"])
        return CONFIRM_TO_DONE

    def finish_to_done(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context, True)
        context.user_data["order"].update({"status": True})
        update.callback_query.answer(
            context.bot.lang_dict["shop_admin_moved_to_done_blink"])
        return self.back_to_orders(update, context)

    def confirm_cancel_order(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        # Set current page integer in the user_data.
        if update.callback_query.data.startswith("admin_order_item_pagination"):
            context.user_data["item_page"] = int(
                update.callback_query.data.replace("admin_order_item_pagination_", ""))
        if not context.user_data.get("item_page"):
            context.user_data["item_page"] = 1
        if update.callback_query.data.startswith("cancel_order"):
            order_id = ObjectId(update.callback_query.data.split("/")[1])
            context.user_data["order"] = AdminOrder(context, order_id)

        if context.user_data["order"].status:
            confirm_text = context.bot.lang_dict["shop_admin_confirm_cancel"]
        else:
            confirm_text = context.bot.lang_dict["shop_admin_confirm_new_cancel"]

        context.user_data["order"].send_full_template(
            update, context, confirm_text, keyboards(context)["confirm_cancel"])
        return CONFIRM_CANCEL

    def finish_cancel(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context, True)
        # change order status
        context.user_data["order"].update({"in_trash": True})
        # return all items to sale.
        for item in context.user_data["order"].items_json:
            # search product
            product = products_table.find_one({"_id": item["product_id"]})
            # if there are no product document - create it
            if not product:
                # TODO - ADD CATEGORY IF IT DOESN'T EXIST
                product = Product(context, item["product"])
                if not product.unlimited:
                    product.quantity = item["quantity"]
                product.create()
            # increase quantity if document exist and product is not unlimited
            elif not product["unlimited"]:
                products_table.update_one(
                    {"_id": item["product_id"]},
                    {"$inc": {"quantity": item["quantity"]}})
        update.callback_query.answer(
            context.bot.lang_dict["order_canceled_blink"])
        return self.back_to_orders(update, context)

    def back_to_orders(self, update, context):
        page = context.user_data.get("page")
        clear_user_data(context)
        context.user_data["page"] = page
        return self.orders(update, context)


(ORDERS, CONFIRM_TO_PROCESS, CONFIRM_TO_DONE,
 CONFIRM_CANCEL, CONFIRM_TO_TRASH, EDIT, CHOOSE_PRODUCT) = range(7)


ORDERS_HANDLER = ConversationHandler(
    allow_reentry=True,
    entry_points=[CallbackQueryHandler(OrdersHandler().orders,
                                       pattern=r"orders")],
    states={
        ORDERS: [CallbackQueryHandler(OrdersHandler().orders,
                                      pattern="admin_order_list_pagination"),
                 CallbackQueryHandler(OrdersHandler().confirm_to_done,
                                      pattern=r"to_done"),
                 CallbackQueryHandler(OrdersHandler().confirm_cancel_order,
                                      pattern=r"cancel_order"),
                 ],

        CONFIRM_TO_DONE: [CallbackQueryHandler(
                              OrdersHandler().finish_to_done,
                              pattern=r"finish_to_done"),
                          CallbackQueryHandler(
                              OrdersHandler().confirm_to_done,
                              pattern="admin_order_item_pagination"),
                          ],

        CONFIRM_CANCEL: [CallbackQueryHandler(OrdersHandler().finish_cancel,
                                              pattern=r"finish_cancel"),
                         CallbackQueryHandler(OrdersHandler().confirm_cancel_order,
                                              pattern="admin_order_item_pagination")
                         ],

    },
    fallbacks=[CallbackQueryHandler(OrdersHandler().back_to_orders,
                                    pattern=r"back_to_orders"),
               CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu"),
               CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"help_back")
               ]
)
