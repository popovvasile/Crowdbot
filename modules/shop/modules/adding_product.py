import logging

from bson import Decimal128
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.modules.welcome import Welcome
from modules.shop.components.product import Product
from helper_funcs.misc import delete_messages
from price_parser import Price
from database import categories_table
from modules.shop.helper.keyboards import (
    keyboards, back_btn, create_keyboard)

logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

START_ADD_PRODUCT, SET_TITLE, SET_CATEGORY, SET_PRICE, SET_CURRENCY, SET_DESCRIPTION, CONFIRM_ADDING = range(7)


class AddingProductHandler(object):
    def start(self, update: Update, context: CallbackContext):  # TODO add title
        delete_messages(update, context, True)
        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Introduce the name of your new product"))
        return SET_TITLE

    def set_title(self, update: Update, context: CallbackContext):

        delete_messages(update, context, True)
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=context.bot.lang_dict["shop_admin_adding_product_start"],
                reply_markup=keyboards(context)["back_to_main_menu_keyboard"]))
        context.user_data["new_product"] = Product(context)
        context.user_data["new_product"].name = update.message.text
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
        category_list = categories_table.find({"bot_id": context.bot.id})
        if update.message:
            categories_table.insert_one({
                "name": update.message.text,
                "query_name": update.message.text,
                "bot_id": context.bot.id
            })
        if category_list.count() > 0:
            keyboard = create_keyboard(
                [InlineKeyboardButton(text=i["name"],
                                      callback_data=f"choose_category/{i['_id']}")
                 for i in category_list],
                [back_btn("back_to_main_menu_btn", context)])
            context.user_data["new_product"].send_adding_product_template(
                update, context, context.bot.lang_dict["shop_admin_set_category"], keyboard)
            return SET_CATEGORY

        else:
            context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                                     text="You didn't set any categories yet.\n"
                                          "Please write a new category",
                                     reply_markup=InlineKeyboardMarkup([[back_btn("back_to_main_menu_btn", context)]]))
            return START_ADD_PRODUCT

    def set_count(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.callback_query:
            context.user_data["new_product"].category_id = \
                update.callback_query.data.split("/")[1]
        context.user_data["new_product"].send_adding_product_template(
            update, context, "Write your price",
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_PRICE

    def set_currency(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["new_product"].price = Decimal128(
            format(Price.fromstring(update.message.text).amount, '.2f'))
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Choose a currency",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("EUR",
                                      callback_data="currency_EUR")],
                [InlineKeyboardButton("USD",
                                      callback_data="currency_USD")],
                [InlineKeyboardButton("RUB",
                                      callback_data="currency_RUB")],
                [InlineKeyboardButton("CHF",
                                      callback_data="currency_CHF")],
                [InlineKeyboardButton("GBP",
                                      callback_data="currency_GBP")
                 ],
                [back_btn("back_to_main_menu_btn", context=context)]
            ]))
        return SET_CURRENCY

    def set_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["new_product"].currency = \
            update.callback_query.data.replace("currency_", "")
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

    states={  # TODO fix add category
        SET_TITLE: [
            MessageHandler(Filters.text, AddingProductHandler().set_title)],
        START_ADD_PRODUCT: [
            MessageHandler(Filters.photo,
                           AddingProductHandler().received_image),
            CallbackQueryHandler(AddingProductHandler().set_category,
                                 pattern="continue"),
            MessageHandler(Filters.text, AddingProductHandler().set_category)],
        SET_CATEGORY: [
            MessageHandler(Filters.text, AddingProductHandler().set_count),
            CallbackQueryHandler(AddingProductHandler().set_count,
                                 pattern=r"choose_category")],
        SET_PRICE: [MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                                   AddingProductHandler().set_currency),
                    MessageHandler(Filters.regex(r"^((?!@).)*$"), AddingProductHandler().set_count)],
        SET_CURRENCY: [CallbackQueryHandler(AddingProductHandler().set_description,
                                            pattern="currency_")],

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
