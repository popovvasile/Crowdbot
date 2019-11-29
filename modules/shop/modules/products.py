from telegram import Update
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, MessageHandler, Filters)
from modules.shop.helper.helper import delete_messages, clear_user_data
from modules.shop.helper.decorator import catch_request_exception
from modules.shop.helper.pagination import APIPaginatedPage, set_page_key
import requests
import logging
from modules.shop.helper.strings import strings
from modules.shop.helper.keyboards import (keyboards, sizes_checkboxes,
                                   back_kb, show_sizes, sizes_list)
from config import conf
from .welcome import Welcome
from modules.shop.components.product import Product

logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class ProductsHandler:
    @catch_request_exception
    def products(self, update: Update, context: CallbackContext):
        set_page_key(update, context)
        resp = requests.get(f"{conf['API_URL']}/admin_products",
                            params={"page": context.user_data["page"],
                                    "per_page": 3,
                                    # "status": "all"
                                    "trash": False})
        pagin = APIPaginatedPage(resp)
        pagin.start(update, context,
                    strings["products_title"],
                    strings["no_products"])
        for product in pagin.data["products_data"]:
            Product(product).send_short_template(update, context, kb=True)
        pagin.send_pagin(update, context)
        return PRODUCTS

    @catch_request_exception
    def edit(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        if update.callback_query \
                and update.callback_query.data.startswith("edit_product"):
            product_id = int(update.callback_query.data.split("/")[1])
            context.user_data["product"] = Product(product_id)
        context.user_data["product"].send_full_template(
            update, context, strings["edit_product_menu"],
            keyboards["edit_product"])
        return EDIT

    def description(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].send_full_template(
            update, context, strings["set_description"],
            keyboards["back_to_products"])
        return DESCRIPTION

    @catch_request_exception
    def finish_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].edit(
            {"description": update.message.text})
        return self.edit(update, context)

    def name(self, update: Update, context: CallbackContext, msg=None):
        delete_messages(update, context)
        context.user_data["product"].send_full_template(
            update, context, strings["change_name"],
            keyboards["back_to_products"])
        if msg:
            context.bot.send_message(update.effective_chat.id,
                                     strings["name_length_error"])
        return NAME

    @catch_request_exception
    def finish_name(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        if len(update.message.text) > 1000:
            return self.name(update, context, msg=True)
        context.user_data["product"].edit({"name": update.message.text})
        return self.edit(update, context)

    def price(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].send_full_template(
            update, context, strings["set_price"],
            keyboards["back_to_products"])
        return PRICE

    @catch_request_exception
    def finish_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].edit({"price": update.message.text})
        return self.edit(update, context)

    def discount_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].send_full_template(
            update, context, strings["set_discount_price"],
            keyboards["back_to_products"])
        return DISCOUNT_PRICE

    @catch_request_exception
    def finish_discount_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        json = {"discount_price": update.message.text}
        context.user_data["product"].edit(json)
        return self.edit(update, context)

    def confirm_to_trash(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        product_id = int(update.callback_query.data.split("/")[1])
        context.user_data["product"] = Product(product_id)
        context.user_data["product"].send_full_template(
            update, context,
            strings["confirm_to_trash_product"],
            keyboards["confirm_to_trash_product"])
        return CONFIRM_TO_TRASH

    @catch_request_exception
    def finish_to_trash(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "typing")
        delete_messages(update, context)
        context.user_data["product"].edit({"new_trash_status": True})
        update.callback_query.answer(strings["moved_to_trash_blink"])
        return self.back_to_products(update, context)

    def sizes_menu(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].send_sizes_menu(update, context)
        return SIZES_MENU

    @catch_request_exception
    def remove_size(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].edit(
            {"sizes_to_remove": [update.callback_query.data.split("/")[1]]})
        update.callback_query.answer(strings["size_removed_blink"])
        return self.sizes_menu(update, context)

    # Sizes Checkboxes
    def set_new_sizes(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        to_remove = [i["size"]
                     for i in context.user_data["product"].sizes]
        if update.callback_query.data in sizes_list:
            if update.callback_query.data \
                    in context.user_data["selected_sizes"]:
                context.user_data["selected_sizes"].remove(
                    update.callback_query.data)
            else:
                context.user_data["selected_sizes"].append(
                    update.callback_query.data)
        else:
            context.user_data["selected_sizes"] = list()
        context.user_data["product"].send_full_template(
            update, context, text=strings["set_new_sizes"],
            kb=sizes_checkboxes(context.user_data["selected_sizes"],
                                to_remove=to_remove,
                                continue_data="set_quantity",
                                back_data="back_to_products"))
        return SET_SIZE

    def set_new_quantity(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        if not context.user_data.get("sizes"):
            context.user_data["sizes"] = list()
        if update.message:
            context.user_data["sizes"][-1]["count"] = int(update.message.text)
        if len(context.user_data["sizes"]) == \
                len(context.user_data["selected_sizes"]):
            return self.confirm_adding_sizes(update, context)
        for size in context.user_data["selected_sizes"]:
            if not any(i["size"] == size for i in context.user_data["sizes"]):
                context.user_data["sizes"].append({"size": size})
                context.user_data["product"].send_full_template(
                    update, context, kb=back_kb("back_to_products"),
                    text=f"{strings['size_quantity'].format(size)}")
                break
        return SET_QUANTITY

    def confirm_adding_sizes(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].send_full_template(
            update, context, text="\n*Добавить данные размеры?*\n" +
                                  show_sizes(context),
            kb=keyboards["confirm_adding_sizes"])
        return CONFIRM_ADD_SIZES

    @catch_request_exception
    def finish_add_sizes(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].edit(
            {"sizes_to_add": context.user_data["sizes"]})
        update.callback_query.answer(strings["sizes_added_blink"])
        return self.edit(update, context)

    def size_quantity(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["edited_size"] = \
            update.callback_query.data.split("/")[1]
        context.user_data["product"].send_full_template(
            update, context, kb=back_kb("back_to_edit"),
            text=strings['size_quantity'].format(
                context.user_data["edited_size"]))
        return SIZE_QUANTITY

    @catch_request_exception
    def finish_quantity_edit(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["product"].edit(
            {"edit_sizes": [{"size": context.user_data["edited_size"],
                             "quantity": int(update.message.text)}]})
        return self.sizes_menu(update, context)

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
                                    pattern="change_name"),
               CallbackQueryHandler(ProductsHandler().sizes_menu,
                                    pattern=r"sizes_menu")],

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

        SIZES_MENU: [CallbackQueryHandler(ProductsHandler().remove_size,
                                          pattern=r"remove_size"),
                     CallbackQueryHandler(ProductsHandler().size_quantity,
                                          pattern=r"change_size_quantity"),
                     CallbackQueryHandler(ProductsHandler().set_new_sizes,
                                          pattern=r"add_size")],

        SET_SIZE: [CallbackQueryHandler(ProductsHandler().set_new_quantity,
                                        pattern="set_quantity"),
                   CallbackQueryHandler(ProductsHandler().back_to_products,
                                        pattern="back_to_products"),
                   CallbackQueryHandler(ProductsHandler().set_new_sizes)],

        SET_QUANTITY: [MessageHandler(Filters.regex("^[0-9]+$"),
                                      ProductsHandler().set_new_quantity)],

        CONFIRM_ADD_SIZES: [CallbackQueryHandler(ProductsHandler().finish_add_sizes,
                                                 pattern=r"finish_add_sizes")],

        SIZE_QUANTITY: [MessageHandler(Filters.regex("^[0-9]+$"),
                                       ProductsHandler().finish_quantity_edit)]
    },
    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu"),
               CallbackQueryHandler(ProductsHandler().back_to_products,
                                    pattern="back_to_products"),
               CallbackQueryHandler(ProductsHandler().edit,
                                    pattern=r"back_to_edit")]
)
