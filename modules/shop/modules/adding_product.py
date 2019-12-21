import logging

from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.modules.welcome import Welcome
from modules.shop.components.product import Product
from helper_funcs.misc import delete_messages
from modules.shop.helper.strings import strings
from database import categories_table
from modules.shop.helper.keyboards import (
    keyboards, back_btn, create_keyboard)


logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


START_ADD_PRODUCT, SET_CATEGORY, SET_PRICE, SET_DESCRIPTION, \
    CONFIRM_ADDING = range(5)


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
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton(context.bot.lang_dict["shop_admin_continue_btn"],
                                      callback_data="continue"),
                 back_btn("back_to_main_menu_btn", context=context)]
            ]))
        return START_ADD_PRODUCT

    def set_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        keyboard = create_keyboard(
            [InlineKeyboardButton(text=i["name"],
                                  callback_data=f"choose_category/{i['_id']}")
             for i in categories_table.find()],
            [back_btn("back_to_main_menu_btn", context)])
        context.user_data["new_product"].send_adding_product_template(
            update, context, context.bot.lang_dict["shop_admin_set_category"], keyboard)
        return SET_CATEGORY

    def set_count(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        # if update.message:
        #     context.user_data["category"] = update.message.text  # TODO fix this, add new category or choose one
        # elif update.callback_query:
        context.user_data["new_product"].category_id = \
            update.callback_query.data.split("/")[1]
        context.user_data["new_product"].send_adding_product_template(
                    update, context, "write your price",
                    keyboards(context)["back_to_main_menu_keyboard"])
        return SET_PRICE

    def set_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["new_product"].price = float(update.message.text)  # TODO add exception for wrong float
        context.user_data["new_product"].send_adding_product_template(
            update, context, "Write description",
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_DESCRIPTION

    def confirm_adding(self, update: Update, context: CallbackContext):
        context.user_data["new_product"].description = update.message.text
        delete_messages(update, context, True)
        context.user_data["new_product"].send_adding_product_template(
            update, context,
            "Confirm adding product",
            keyboards(context)["confirm_add_product"])
        return CONFIRM_ADDING

    # @catch_request_exception
    def finish_adding(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "upload_photo")
        context.user_data["new_product"].create()
        return Welcome().back_to_main_menu(
            update, context, context.bot.lang_dict["shop_admin_adding_product_finished"])


ADD_PRODUCT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(AddingProductHandler().start,
                                       pattern=r"add_product")],

    states={   # TODO fix add category
        START_ADD_PRODUCT: [
            MessageHandler(Filters.photo,
                           AddingProductHandler().received_image),
            CallbackQueryHandler(AddingProductHandler().set_category,
                                 pattern="continue")],
        SET_CATEGORY: [  # CallbackQueryHandler(AddingProductHandler().set_size,
            #                      pattern="^[0-9]+$")
MessageHandler(Filters.text, AddingProductHandler().set_count),
            CallbackQueryHandler(AddingProductHandler().set_count,
                                 pattern=r"choose_category")],
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