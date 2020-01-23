import logging
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.modules.welcome import Welcome
from modules.shop.components.product import Product
from helper_funcs.misc import delete_messages
from price_parser import Price
from database import categories_table, chatbots_table
from modules.shop.helper.keyboards import (
    keyboards, back_btn, create_keyboard)

logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

START_ADD_PRODUCT, ONLINE_PAYMENT, SHIPPING, SET_TITLE, SET_CATEGORY, SET_PRICE, \
SET_DESCRIPTION, CONFIRM_ADDING, FINISH_ADDING = range(9)


class AddingProductHandler(object):
    def start(self, update: Update, context: CallbackContext):  # TODO add title
        delete_messages(update, context, True)
        buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Introduce the name of your new product",
                                     reply_markup=reply_markup))
        return SET_TITLE

    def set_image(self, update: Update, context: CallbackContext):

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
        if len(update.message.photo) >0:  # TODO receive image as files
            context.user_data["new_product"].images.append(
                update.message.photo[-1].file_id)
        else:
            context.user_data["new_product"].images.append(
                update.message.document.file_id)
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
            buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="back_to_main_menu")]]
            reply_markup = InlineKeyboardMarkup(
                buttons)
            context.bot.send_message(chat_id=update.callback_query.message.chat_id,
                                     text="You didn't set any categories yet.\n"
                                          "Please write a new category",
                                     reply_markup=reply_markup)

            return START_ADD_PRODUCT

    def set_count(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.callback_query:
            context.user_data["new_product"].category_id = \
                update.callback_query.data.split("/")[1]
        context.user_data["new_product"].send_adding_product_template(
            update, context, "Write your price",
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_DESCRIPTION

    def set_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["new_product"].price = format(Price.fromstring(update.message.text).amount, '.2f')
        context.user_data["new_product"].send_adding_product_template(
            update, context, "Write description",
            keyboards(context)["back_to_main_menu_keyboard"])
        chatbot = chatbots_table.find_one({"bot_id": context.bot.id}) or {}

        if "payment_token" in chatbot.get("shop", {}):
            return ONLINE_PAYMENT
        else:
            return SHIPPING

    def online_payment(self, update: Update, context: CallbackContext):
        if update.message:
            context.user_data["new_product"].description = update.message.text
        delete_messages(update, context, True)
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text="Do you want to make this product with online payment, offline payment or both?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Online payment",
                                      callback_data="set_payment_online")],
                [InlineKeyboardButton("Offline payment",
                                      callback_data="set_payment_offline")],
                [InlineKeyboardButton("Both options",
                                      callback_data="set_payment_both")],
                [back_btn("back_to_main_menu_btn", context=context)]
            ]))
        return SHIPPING

    def shipping(self, update: Update, context: CallbackContext):
        if update.message:
            context.user_data["new_product"].description = update.message.text
        else:
            if "online" in update.callback_query.data:
                context.user_data["new_product"].online_payment = True
                context.user_data["new_product"].offline_payment = False
            elif "offline" in update.callback_query.data:
                context.user_data["new_product"].online_payment = False
                context.user_data["new_product"].offline_payment = True
            elif "both" in update.callback_query.data:
                context.user_data["new_product"].online_payment = True
                context.user_data["new_product"].offline_payment = True
        delete_messages(update, context, True)
        context.bot.send_message(
            chat_id=update.effective_message.chat_id,
            text="Do you want to make this product with shipping or without it?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("With Shipping",
                                      callback_data="shipping_true")],
                [InlineKeyboardButton("Without Shipping",
                                      callback_data="shipping_false")],
                [back_btn("back_to_main_menu_btn", context=context)]
            ]))
        return CONFIRM_ADDING

    def confirm_adding(self, update: Update, context: CallbackContext):
        if "true" in update.callback_query.data:
            context.user_data["new_product"].shipping = True
        else:
            context.user_data["new_product"].shipping = False
        delete_messages(update, context, True)
        context.user_data["new_product"].send_adding_product_template(
            update, context,
            "Confirm adding product",
            keyboards(context)["confirm_add_product"])
        return FINISH_ADDING

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
            MessageHandler(Filters.text, AddingProductHandler().set_image)],
        START_ADD_PRODUCT: [
            MessageHandler(Filters.photo,
                           AddingProductHandler().received_image),
            MessageHandler(Filters.document.image,
                           AddingProductHandler().received_image),
            CallbackQueryHandler(AddingProductHandler().set_category,
                                 pattern="continue"),
            MessageHandler(Filters.text, AddingProductHandler().set_category),

        ],
        SET_CATEGORY: [
            MessageHandler(Filters.text, AddingProductHandler().set_category),
            CallbackQueryHandler(AddingProductHandler().set_count,
                                 pattern=r"choose_category")],
        SET_DESCRIPTION: [MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                                         AddingProductHandler().set_description),
                          MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                                         AddingProductHandler().set_description),
                          MessageHandler(Filters.regex(r"^((?!@).)*$"), AddingProductHandler().set_count),
                          ],
        ONLINE_PAYMENT: [MessageHandler(Filters.text, callback=AddingProductHandler().online_payment)],

        SHIPPING: [CallbackQueryHandler(AddingProductHandler().shipping,
                                        pattern=r"set_payment_"),
                   MessageHandler(Filters.text, callback=AddingProductHandler().shipping)],

        CONFIRM_ADDING: [CallbackQueryHandler(AddingProductHandler().confirm_adding,
                                              pattern=r"shipping_")],
        FINISH_ADDING: [CallbackQueryHandler(AddingProductHandler().finish_adding,
                                             pattern=r"send_product")]

    },

    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu")]
)
