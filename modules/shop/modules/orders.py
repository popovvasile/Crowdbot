import logging
from telegram import Update, ParseMode
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext)

from helper_funcs.pagination import Pagination
from modules.shop.helper.keyboards import keyboards, back_kb, back_btn
from modules.shop.helper.helper import clear_user_data
from modules.shop.components.order import Order
from modules.shop.components.product import Product
from helper_funcs.pagination import set_page_key
from modules.shop.modules.welcome import Welcome
from database import orders_table
from helper_funcs.misc import delete_messages


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class OrdersHandler(object):
    def orders(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        set_page_key(update, context, "orders")
        all_orders = orders_table.find({"in_trash": False}).sort([["_id", 1]])
        return self.orders_layout(update, context, all_orders, ORDERS)

    def orders_layout(self, update, context, all_orders, state):
        # Title
        context.user_data['to_delete'].append(
            context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["shop_admin_orders_title"].format(all_orders.count()),
                parse_mode=ParseMode.MARKDOWN))

        if all_orders.count() == 0:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_no_orders"],
                    reply_markup=back_kb("back_to_main_menu", context=context)))
        else:
            pagination = Pagination(
                all_orders, page=context.user_data["page"], per_page=5)
            for order in pagination.content:
                Order(context=context, obj=order).send_short_template(update, context)
            pagination.send_keyboard(
                update, context, [[back_btn("back_to_main_menu", context=context)]])
        return state

    def confirm_to_trash(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        set_page_key(update, context, name="item_page", start_data={})
        order_id = update.callback_query.data.split("/")[1]
        context.user_data["order"] = Order(order_id)
        context.user_data["order"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_confirm_to_trash_new"],
            keyboards(context)["confirm_to_trash"])
        return CONFIRM_TO_TRASH

    def finish_to_trash(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context, True)
        context.user_data["order"].update({"in_trash": True})
        update.callback_query.answer(context.bot.lang_dict["shop_admin_moved_to_trash_blink"])
        return self.back_to_orders(update, context)

    # TODO all next methods broken! Need to change !

    def confirm_to_done(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        set_page_key(update, context, name="item_page", start_data={})
        if update.callback_query.data.startswith("to_done"):
            order_id = update.callback_query.data.split("/")[1]
            context.user_data["order"] = Order(order_id)
        context.user_data["order"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_confirm_to_done"],
            keyboards(context)["confirm_to_done"])
        return CONFIRM_TO_DONE

    def finish_to_done(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context, True)
        context.user_data["order"].change_status({"new_status": True})
        update.callback_query.answer(context.bot.lang_dict["shop_admin_moved_to_done_blink"])
        return self.back_to_orders(update, context)

    def confirm_cancel_order(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        set_page_key(update, context=context, name="item_page", start_data={})  # TODO hz what is this, double check
        if update.callback_query.data.startswith("cancel_order"):
            order_id = int(update.callback_query.data.split("/")[1])
            context.user_data["order"] = Order(order_id)
        context.user_data["order"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_confirm_cancel"],
            keyboards(context)["confirm_cancel"])
        return CONFIRM_CANCEL

    def finish_cancel(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context, True)
        context.user_data["order"].change_status({"new_status": False})
        update.callback_query.answer(context.bot.lang_dict["shop_admin_order_canceled_blink"])
        return self.back_to_orders(update, context)

    def edit(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        set_page_key(update, context, "item_page")
        if update.callback_query.data.startswith("edit"):
            try:
                order_id = update.callback_query.data.split("/")[1]
                context.user_data["order"] = Order(order_id)
            except IndexError:
                context.user_data["order"].refresh()
        context.user_data["order"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_edit_menu"],
            keyboards(context)["edit_keyboard"],
            delete_kb=True)
        return EDIT

    def remove_item(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        item_id = update.callback_query.data.split("/")[1]
        context.user_data["order"].remove_item(item_id)
        update.callback_query.answer(context.bot.lang_dict["shop_admin_item_removed_blink"])
        return self.edit(update, context)

    def add_item(self, update: Update, context: CallbackContext):  # TODO
        delete_messages(update, context, True)
        set_page_key(update, context, "choose_product_page")
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
        product.send_admin_short_template(update, context, kb=add_kb)
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
                                      pattern="^[0-9]+$"),
                 CallbackQueryHandler(OrdersHandler().confirm_to_done,
                                      pattern=r"to_done"),
                 CallbackQueryHandler(OrdersHandler().confirm_to_trash,
                                      pattern=r"to_trash"),
                 CallbackQueryHandler(OrdersHandler().confirm_cancel_order,
                                      pattern=r"cancel_order"),
                 CallbackQueryHandler(OrdersHandler().edit,
                                      pattern=r"edit")],

        CONFIRM_TO_DONE: [CallbackQueryHandler(OrdersHandler().finish_to_done,
                                               pattern=r"finish_to_done"),
                          CallbackQueryHandler(OrdersHandler().confirm_to_done,
                                               pattern="^[0-9]+$"),
                          CallbackQueryHandler(OrdersHandler().edit,
                                               pattern=r"edit")],

        CONFIRM_CANCEL: [CallbackQueryHandler(OrdersHandler().finish_cancel,
                                              pattern=r"finish_cancel"),
                         CallbackQueryHandler(OrdersHandler().confirm_cancel_order,
                                              pattern="^[0-9]+$")],

        CONFIRM_TO_TRASH: [CallbackQueryHandler(OrdersHandler().finish_to_trash,
                                                pattern=r"finish_to_trash")],

        EDIT: [CallbackQueryHandler(OrdersHandler().add_item,
                                    pattern=r"add_to_order"),
               CallbackQueryHandler(OrdersHandler().remove_item,
                                    pattern=r"remove_item"),
               CallbackQueryHandler(OrdersHandler().edit,
                                    pattern="^[0-9]+$")],

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
