import logging

from bson.objectid import ObjectId
from telegram import (Update, ParseMode, InlineKeyboardButton,
                      InlineKeyboardMarkup)
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

from helper_funcs.pagination import Pagination
from modules.shop.helper.keyboards import keyboards, back_kb, back_btn
from modules.shop.helper.helper import clear_user_data
from modules.shop.components.order import AdminOrder
from modules.shop.components.product import Product
from modules.shop.admin_side.welcome import Welcome
from database import orders_table
from helper_funcs.misc import delete_messages
from database import products_table


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class OrdersHandlerHelper(object):
    @staticmethod
    def order_reply_markup(context, order):
        kb = [[]]
        if order.in_trash:
            # kb[0].append(
            #     InlineKeyboardButton(
            #         text=context.bot.lang_dict["shop_admin_restore_btn"],
            #         callback_data=f"restore/{order.id_}"))
            # return InlineKeyboardMarkup(kb)
            return None

        if order.status is False:
            if len(order.items):
                kb[0].append(
                    InlineKeyboardButton(
                        text=context.bot.lang_dict["shop_admin_to_done_btn"],
                        callback_data=f"to_done/{order.id_}"))
            kb[0].append(
                InlineKeyboardButton(
                    text=context.bot.lang_dict["shop_admin_edit_btn"],
                    callback_data=f"edit/{order.id_}"))

            # kb[0].append(InlineKeyboardButton(
            #     text=context.bot.lang_dict["shop_admin_to_trash_btn"],
            #     callback_data=f"to_trash/{order.id_}"))

        # elif order.status is True:
        kb[0].append(
            InlineKeyboardButton(
                text=context.bot.lang_dict["shop_admin_cancel_btn"],
                callback_data=f"cancel_order/{order.id_}"))
        return InlineKeyboardMarkup(kb)


class OrdersHandler(OrdersHandlerHelper):
    def orders(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        # Set current page integer in the user_data.
        if update.callback_query.data.startswith(
                "admin_order_list_pagination"):
            context.user_data["page"] = int(
                update.callback_query.data.replace(
                    "admin_order_list_pagination_", ""))
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
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["shop_admin_orders_title"].format(
                    all_orders.count()),
                parse_mode=ParseMode.MARKDOWN))

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
                [[back_btn("back_to_main_menu", context=context)]],
                "admin_order_list_pagination")
        return state

    # def confirm_to_trash(self, update: Update, context: CallbackContext):
    #     delete_messages(update, context, True)
    #     set_page_key(update, context, name="item_page", start_data={})
    #     order_id = update.callback_query.data.split("/")[1]
    #     context.user_data["order"] = Order(order_id)
    #     context.user_data["order"].send_full_template(
    #         update, context,
    #         context.bot.lang_dict["shop_admin_confirm_to_trash_new"],
    #         keyboards(context)["confirm_to_trash"])
    #     return CONFIRM_TO_TRASH

    # def finish_to_trash(self, update: Update, context: CallbackContext):
    #     context.bot.send_chat_action(update.effective_chat.id, "typing")
    #     delete_messages(update, context, True)
    #     context.user_data["order"].update({"in_trash": True})
    #     update.callback_query.answer(context.bot.lang_dict["shop_admin_moved_to_trash_blink"])
    #     return self.back_to_orders(update, context)

    def confirm_to_done(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.callback_query.data.startswith(
                "admin_order_item_pagination"):
            context.user_data["item_page"] = int(
                update.callback_query.data.replace(
                    "admin_order_item_pagination_", ""))
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
        if update.callback_query.data.startswith(
                "admin_order_item_pagination"):
            context.user_data["item_page"] = int(
                update.callback_query.data.replace(
                    "admin_order_item_pagination_", ""))
        if not context.user_data.get("item_page"):
            context.user_data["item_page"] = 1
        if update.callback_query.data.startswith("cancel_order"):
            order_id = ObjectId(update.callback_query.data.split("/")[1])
            context.user_data["order"] = AdminOrder(context, order_id)
        context.user_data["order"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_confirm_cancel"],
            keyboards(context)["confirm_cancel"])
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
                product = Product(context, item["product"])
                if not product.unlimited:
                    product.quantity = item["quantity"]
                product.create()

            elif not product["unlimited"]:
                products_table.update_one(
                    {"_id": item["product_id"]},
                    {"$inc": {"quantity": item["quantity"]}})
        update.callback_query.answer(
            context.bot.lang_dict["shop_admin_order_canceled_blink"])
        return self.back_to_orders(update, context)

    def edit(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        # Set current page integer in the user_data.
        if update.callback_query.data.startswith(
                "admin_order_item_pagination"):
            context.user_data["item_page"] = int(
                update.callback_query.data.replace(
                    "admin_order_item_pagination_", ""))
        if not context.user_data.get("item_page"):
            context.user_data["item_page"] = 1
        if update.callback_query.data.startswith("edit"):
            try:
                order_id = update.callback_query.data.split("/")[1]
                context.user_data["order"] = AdminOrder(context, order_id)
            except IndexError:
                context.user_data["order"].create_fields()
        context.user_data["order"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_edit_menu"],
            keyboards(context)["edit_keyboard"],
            item_reply_markup=True)
        return EDIT

    def remove_item(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        item_id = update.callback_query.data.split("/")[1]
        context.user_data["order"].remove_item(item_id)
        update.callback_query.answer(
            context.bot.lang_dict["shop_admin_item_removed_blink"])
        return self.edit(update, context)

    def add_item(self, update: Update, context: CallbackContext):  # TODO
        delete_messages(update, context, True)
        # set_page_key(update, context, "choose_product_page")
        # resp = requests.get(
        #     f"{conf['API_URL']}/admin_products",
        #     params={"page": context.user_data["choose_product_page"],
        #             "per_page": 3,
        #             "status": "not_sold"})
        # pagin = APIPaginatedPage(resp)
        # pagin.start(update, context,
        #             f'{context.bot.lang_dict["shop_admin_choose_products_title"]}'
        #             f'\n{context.user_data["order"].template}',
        #             context.bot.lang_dict["shop_admin_no_products"])
        # for product in pagin.data["products_data"]:
        product = Product(context, context.user_data["product"])
        add_kb = product.add_keyboard(context.user_data["order"])
        product.send_admin_short_template(update, context, reply_markup=add_kb)
        # Pagination().send_pagin(update, context)
        return CHOOSE_PRODUCT

    def finish_adding_item(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        item_data = update.callback_query.data.split("/")
        item = dict(
            article=item_data[1],
            size=item_data[2]
        )
        context.user_data["order"].add_item(item)
        return self.edit(update, context)

    def back_to_orders(self, update, context):
        page = context.user_data.get("page")
        clear_user_data(context)
        context.user_data["page"] = page
        return self.orders(update, context)


ORDERS, CONFIRM_TO_PROCESS, CONFIRM_TO_DONE, \
    CONFIRM_CANCEL, CONFIRM_TO_TRASH, EDIT, \
    CHOOSE_PRODUCT = range(7)


ORDERS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(OrdersHandler().orders,
                                       pattern=r"orders")],
    states={
        ORDERS: [CallbackQueryHandler(OrdersHandler().orders,
                                      pattern="admin_order_list_pagination"),
                 CallbackQueryHandler(OrdersHandler().confirm_to_done,
                                      pattern=r"to_done"),
                 # CallbackQueryHandler(OrdersHandler().confirm_to_trash,
                 #                      pattern=r"to_trash"),
                 CallbackQueryHandler(OrdersHandler().confirm_cancel_order,
                                      pattern=r"cancel_order"),
                 # CallbackQueryHandler(OrdersHandler().edit,
                 #                      pattern=r"edit")
                 ],

        CONFIRM_TO_DONE: [CallbackQueryHandler(
                              OrdersHandler().finish_to_done,
                              pattern=r"finish_to_done"),
                          CallbackQueryHandler(
                              OrdersHandler().confirm_to_done,
                              pattern="admin_order_item_pagination"),
                          CallbackQueryHandler(
                              OrdersHandler().edit,
                              pattern=r"edit")],

        CONFIRM_CANCEL: [CallbackQueryHandler(OrdersHandler().finish_cancel,
                                              pattern=r"finish_cancel"),
                         CallbackQueryHandler(OrdersHandler().confirm_cancel_order,
                                              pattern="admin_order_item_pagination")],

        # CONFIRM_TO_TRASH: [
        #     CallbackQueryHandler(OrdersHandler().finish_to_trash,
        #                          pattern=r"finish_to_trash")],

        EDIT: [CallbackQueryHandler(OrdersHandler().add_item,
                                    pattern=r"add_to_order"),
               CallbackQueryHandler(OrdersHandler().remove_item,
                                    pattern=r"remove_item"),
               CallbackQueryHandler(OrdersHandler().edit,
                                    pattern="admin_order_item_pagination")],

        CHOOSE_PRODUCT: [CallbackQueryHandler(OrdersHandler().finish_adding_item,
                                              pattern=r"finish_add_to_order"),
                         CallbackQueryHandler(OrdersHandler().add_item,
                                              pattern="^[0-9]+$")]
    },
    fallbacks=[CallbackQueryHandler(OrdersHandler().back_to_orders,
                                    pattern=r"back_to_orders"),
               CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu")]
)