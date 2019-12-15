import logging

from telegram import InlineKeyboardButton, Update
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.modules.welcome import Welcome
from modules.shop.components.product import Product
from helper_funcs.misc import delete_messages
from modules.shop.helper.strings import strings
from database import brands_table, categories_table
from modules.shop.helper.keyboards import (
    keyboards, back_btn, create_keyboard,
    sizes_checkboxes, sizes_list)


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class AddingProductHandler(object):
    def start(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=context.bot.lang_dict["shop_admin_adding_product_start"],
                reply_markup=keyboards(context)["back_to_main_menu_keyboard"]))
        context.user_data["new_product"] = Product(context)
        return START_ADD_PRODUCT

    def received_image(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["new_product"].images.append(
            update.message.photo[-1].file_id)
        context.user_data["new_product"].send_adding_product_template(
            update, context, context.bot.lang_dict["shop_admin_send_more_photo"].format(
                len(context.user_data["new_product"].images)),
            keyboards(context)["continue_back_kb"])
        return START_ADD_PRODUCT

    def set_brand(self, update: Update, context: CallbackContext):  # TODO skip this part if there are no brands
        delete_messages(update, context, True)
        context.user_data["all_brands"] = brands_table.find()
        keyboard = create_keyboard(
            [InlineKeyboardButton(text=i["name"],
                                  callback_data=f"choose_brand/{i['_id']}")
             for i in context.user_data["all_brands"]],
            [back_btn("back_to_main_menu_btn", context)])
        context.user_data["new_product"].send_adding_product_template(
            update, context, context.bot.lang_dict["shop_admin_set_brand"], keyboard)
        return SET_BRAND

    def set_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["all_categories"] = categories_table.find()
        context.user_data["new_product"].brand_id = \
            update.callback_query.data.split("/")[1]
        keyboard = create_keyboard(
            [InlineKeyboardButton(text=i["name"],
                                  callback_data=f"choose_category/{i['_id']}")
             for i in context.user_data["all_categories"]],
            [back_btn("back_to_main_menu_btn", context)])
        context.user_data["new_product"].send_adding_product_template(
            update, context, context.bot.lang_dict["shop_admin_set_category"], keyboard)
        return SET_CATEGORY

    # Sizes Checkboxes
    def set_size(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.callback_query.data in sizes_list:
            if (update.callback_query.data in
                    context.user_data["selected_sizes"]):
                context.user_data["selected_sizes"].remove(
                    update.callback_query.data)
            else:
                context.user_data["selected_sizes"].append(
                    update.callback_query.data)
        else:
            context.user_data["new_product"].category_id = \
                update.callback_query.data.split("/")[1]
            context.user_data["selected_sizes"] = list()
        context.user_data["new_product"].send_adding_product_template(
            update, context,
            f"\n*Бренд:* `{context.user_data['new_product'].brand.name}`"
            f"\n*Категория:* "
            f"`{context.user_data['new_product'].category['name']}`"
            f"\n\n{strings['set_sizes']}",
            sizes_checkboxes(context.user_data["selected_sizes"], context=context))
        return SET_SIZE

    def set_count(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.message:
            context.user_data["new_product"].sizes[-1]["quantity"] = \
                int(update.message.text)
        if len(context.user_data["new_product"].sizes) == \
                len(context.user_data["selected_sizes"]):
            return self.set_price(update, context)
        for size in context.user_data["selected_sizes"]:
            if not any(i["size"] == size
                       for i in context.user_data["new_product"].sizes):
                context.user_data["new_product"].sizes.append({"size": size})
                context.user_data["new_product"].send_adding_product_template(
                    update, context,
                    f"\n*Бренд:* "
                    f"`{context.user_data['new_product'].brand.name}`"
                    f"\n*Категория:* "
                    f"`{context.user_data['new_product'].category['name']}`"
                    f"\n*Размеры*: "
                    f"{context.user_data['selected_sizes']}"
                    f"{strings['size_quantity'].format(size)}",
                    keyboards(context)["back_to_main_menu_keyboard"])
                break
        return SET_QUANTITY

    def set_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        # Product
        context.user_data["new_product"].send_adding_product_template(
            update, context,
            f"\n*Бренд:* "
            f"`{context.user_data['new_product'].brand.name}`"
            f"\n*Категория:* "
            f"`{context.user_data['new_product'].category['name']}`"
            f"\n*Размеры*: "
            f"{context.user_data['new_product'].sizes_text}"
            f"\n\n{strings['set_price']}",
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_PRICE

    def set_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["new_product"].price = int(update.message.text)
        context.user_data["new_product"].send_adding_product_template(
            update, context,
            f"`{context.user_data['new_product'].brand.name}`"
            f"\n*Категория:* "
            f"`{context.user_data['new_product'].category['name']}`"
            f"\n*Размеры*: "
            f"{context.user_data['new_product'].sizes_text}"
            f"\n*Цена:* "
            f"`{context.user_data['new_product'].price}`"
            f"\n\n{strings['set_description']}",
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_DESCRIPTION

    def confirm_adding(self, update: Update, context: CallbackContext):
        context.user_data["new_product"].description = update.message.text
        delete_messages(update, context, True)
        context.user_data["new_product"].send_adding_product_template(
            update, context,
            f"*Бренд:* "
            f"`{context.user_data['new_product'].brand.name}`"
            f"\n*Категория:* "
            f"`{context.user_data['new_product'].category['name']}`"
            f"\n*Размеры*: "
            f"{context.user_data['new_product'].sizes_text}"
            f"\n*Цена:* "
            f"`{context.user_data['new_product'].price}`"
            f"\n*Описание*: "
            f"`{context.user_data['new_product'].description}`"
            f"\n\n{strings['confirm_add_product']}",
            keyboards(context)["confirm_add_product"])
        return CONFIRM_ADDING

    # @catch_request_exception
    def finish_adding(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "upload_photo")
        context.user_data["new_product"].create()
        return Welcome().back_to_main_menu(
            update, context, context.bot.lang_dict["shop_admin_adding_product_finished"])


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

        SET_BRAND: [  # CallbackQueryHandler(AddingProductHandler().set_category,
                    #                      pattern="^[0-9]+$")
                    CallbackQueryHandler(AddingProductHandler().set_category,
                                         pattern=r"choose_brand")],

        SET_CATEGORY: [  # CallbackQueryHandler(AddingProductHandler().set_size,
                       #                      pattern="^[0-9]+$")
                       CallbackQueryHandler(AddingProductHandler().set_size,
                                            pattern=r"choose_category")],

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
