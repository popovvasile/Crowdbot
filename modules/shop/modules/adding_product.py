from telegram import InlineKeyboardButton, Update
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)
from modules.shop.helper.keyboards import (keyboards, back_btn, create_keyboard,
                                   sizes_checkboxes, sizes_list, show_sizes)
from modules.shop.helper.decorator import catch_request_exception
from modules.shop.helper.helper import delete_messages
from modules.shop.helper.strings import strings
import requests
from requests.exceptions import RequestException
import logging
from config import conf
from .welcome import Welcome
from modules.shop.components.product import Product


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class AddingProductHandler(object):
    def start(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.context.user_data["to_delete"].append(
            context.context.bot.send_message(
                update.effective_chat.id,
                strings["adding_product_start"],
                reply_markup=keyboards["back_to_main_menu_keyboard"]))
        return START_ADD_PRODUCT

    def received_image(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        if "product_images" not in context.context.user_data:
            context.context.user_data["product_images"] = list()
        context.context.user_data["product_images"].append(update.message.photo[-1])
        Product.send_adding_product_template(
            update, context,
            strings["send_more_photo"].format(
                len(context.context.user_data["product_images"])),
            keyboards["continue_back_kb"])
        return START_ADD_PRODUCT

    @catch_request_exception
    def set_brand(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        resp = requests.get(f"{conf['API_URL']}/categories_data")
        if resp.status_code != 200:
            raise RequestException
        context.context.user_data["categories_data"] = resp.json()
        keyboard = create_keyboard(
            [InlineKeyboardButton(i["name"], callback_data=i["id"])
             for i in context.context.user_data["categories_data"]["brands"]],
            [back_btn("back_to_main_menu_btn")])
        Product.send_adding_product_template(
            update, context, strings["set_brand"], keyboard)
        return SET_BRAND

    def set_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.context.user_data["selected_brand"] = next(
            (b for b in context.context.user_data["categories_data"]["brands"]
             if str(b["id"]) == update.callback_query.data))
        keyboard = create_keyboard(
            [InlineKeyboardButton(i["name"], callback_data=i["id"])
             for i in context.context.user_data["categories_data"]["categories"]],
            [back_btn("back_to_main_menu_btn")])
        Product.send_adding_product_template(
            update, context, strings["set_category"], keyboard)
        return SET_CATEGORY

    # Sizes Checkboxes
    def set_size(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        if update.callback_query.data in sizes_list:
            if update.callback_query.data \
                    in context.context.user_data["selected_sizes"]:
                context.context.user_data["selected_sizes"].remove(
                    update.callback_query.data)
            else:
                context.context.user_data["selected_sizes"].append(
                    update.callback_query.data)
        else:
            context.context.user_data["selected_category"] = next(
                (i for i in context.context.user_data.get("categories_data")["categories"]
                 if str(i["id"]) == update.callback_query.data), None)
            context.context.user_data["selected_sizes"] = list()
        Product.send_adding_product_template(
            update, context,
            f"\n*Бренд:* "
            f"`{context.context.user_data['selected_brand']['name']}`"
            f"\n*Категория:* "
            f"`{context.context.user_data['selected_category']['name']}`"
            f"\n\n{strings['set_sizes']}",
            sizes_checkboxes(context.context.user_data["selected_sizes"]))
        return SET_SIZE

    # Sizes Single choice
    """def set_size(self, update: Update, context: CallbackContext):
            delete_messages(update, context)
            context.user_data["selected_category"] = next(
                (i for i in context.user_data["categories_data"]["categories"]
                 if str(i["id"]) == update.callback_query.data))

            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton(i, callback_data=i)] for i in sizes_list] +
                [keyboards["back_to_main_menu_button"]])
            Product.send_adding_photo_template(
                update, context,
                f"\n*Бренд:* `{context.user_data['selected_brand']['name']}`"
                f"\n*Категория:* `{context.user_data['selected_category']['name']}`"
                f"\n\n{strings['set_sizes']}", kb)
            return SET_SIZE"""

    def set_count(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        if not context.context.user_data.get("sizes"):
            context.context.user_data["sizes"] = list()
        if update.message:
            context.context.user_data["sizes"][-1]["count"] = int(update.message.text)
        if len(context.context.user_data["sizes"]) == \
                len(context.context.user_data["selected_sizes"]):
            return self.set_price(update, context)
        for size in context.context.user_data["selected_sizes"]:
            if not any(i["size"] == size for i in context.context.user_data["sizes"]):
                context.context.user_data["sizes"].append({"size": size})
                Product.send_adding_product_template(
                    update, context,
                    f"\n*Бренд:* "
                    f"`{context.context.user_data['selected_brand']['name']}`"
                    f"\n*Категория:* "
                    f"`{context.context.user_data['selected_category']['name']}`"
                    f"\n*Размеры*: "
                    f"{context.context.user_data['selected_sizes']}"
                    f"{strings['size_quantity'].format(size)}",
                    # f"\n\n Выбери количество *{size}* размера",
                    keyboards["back_to_main_menu_keyboard"])
                break
        return SET_QUANTITY

    def set_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        Product.send_adding_product_template(
            update, context,
            f"\n*Бренд:* `{context.context.user_data['selected_brand']['name']}`"
            f"\n*Категория:* "
            f"`{context.context.user_data['selected_category']['name']}`"
            f"\n*Размеры*: \n{show_sizes(context)}"
            f"\n\n{strings['set_price']}",
            keyboards["back_to_main_menu_keyboard"])
        return SET_PRICE

    def set_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.context.user_data["price"] = int(update.message.text)
        Product.send_adding_product_template(
            update, context,
            f"*Бренд:* `{context.context.user_data['selected_brand']['name']}`"
            f"\n*Категория:* "
            f"`{context.context.user_data['selected_category']['name']}`"
            f"\n*Размеры*: \n{show_sizes(context)}"
            f"\n*Цена:* `{context.context.user_data['price']}`"
            f"\n\n{strings['set_description']}",
            keyboards["back_to_main_menu_keyboard"])
        return SET_DESCRIPTION

    def confirm_adding(self, update: Update, context: CallbackContext):
        context.context.user_data["description"] = update.message.text
        delete_messages(update, context)
        # pprint(context.user_data)
        Product.send_adding_product_template(
            update, context,
            f"*Бренд:* `{context.context.user_data['selected_brand']['name']}`"
            f"\n*Категория:* "
            f"`{context.context.user_data['selected_category']['name']}`"
            f"\n*Размеры*: \n{show_sizes(context)}"
            f"\n*Цена:* `{context.context.user_data['price']}`"
            f"\n*Описание*: `{context.context.user_data['description']}`"
            f"\n\n{strings['confirm_add_product']}",
            keyboards["confirm_add_product"])
        return CONFIRM_ADDING

    @catch_request_exception
    def finish_adding(self, update: Update, context: CallbackContext):
        context.context.bot.send_chat_action(update.effective_chat.id, "upload_photo")
        files = [("images", (i.file_id,
                             i.get_file().download_as_bytearray(),
                             "image/jpg"))
                 for i in context.context.user_data["product_images"]]
        data = {
            "price": context.context.user_data["price"],
            "brand_id": context.context.user_data["selected_brand"]["id"],
            "category_id": context.context.user_data["selected_category"]["id"],
            "sizes": context.context.user_data["sizes"],
            "description": context.context.user_data["description"]
        }
        resp = requests.post(f"{conf['API_URL']}/product",
                             files=files, data=data)
        if resp.status_code != 200:
            raise RequestException
        return Welcome().back_to_main_menu(
            update, context, strings["adding_product_finished"])


START_ADD_PRODUCT, SET_BRAND, SET_CATEGORY, \
    SET_SIZE, SET_PRICE, SET_DESCRIPTION, \
    CONFIRM_ADDING, SET_QUANTITY = range(8)


ADD_PRODUCT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(AddingProductHandler().start,
                                       pattern=r"add_product")],

    states={
        START_ADD_PRODUCT: [
            MessageHandler(Filters.photo,
                           AddingProductHandler().received_image),
            CallbackQueryHandler(AddingProductHandler().set_brand,
                                 pattern="continue")],

        SET_BRAND: [CallbackQueryHandler(AddingProductHandler().set_category,
                                         pattern="^[0-9]+$")],

        SET_CATEGORY: [CallbackQueryHandler(AddingProductHandler().set_size,
                                            pattern="^[0-9]+$")],

        SET_SIZE: [CallbackQueryHandler(AddingProductHandler().set_count,
                                        pattern="set_price"),
                   # CallbackQueryHandler(Welcome().back_to_main_menu,
                   # pattern=r"back_to_main_menu"),
                   # CallbackQueryHandler(AddingProductHandler().set_price)
                   CallbackQueryHandler(AddingProductHandler().set_size)],

        SET_QUANTITY: [MessageHandler(Filters.regex("^[0-9]+$"),
                                      AddingProductHandler().set_count)],

        SET_PRICE: [MessageHandler(Filters.regex("^[0-9]+$"),
                                   AddingProductHandler().set_description)],

        SET_DESCRIPTION: [
            MessageHandler(Filters.text,
                           AddingProductHandler().confirm_adding)],

        CONFIRM_ADDING: [
            CallbackQueryHandler(AddingProductHandler().finish_adding,
                                 pattern=r"send_product")]
    },

    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu")]
)
