from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from helper_funcs.helper import currency_limits_dict
from modules.shop.admin_side.welcome import Welcome
from modules.shop.components.product import Product, MAX_TEMP_DESCRIPTION_LENGTH
from helper_funcs.misc import delete_messages
from price_parser import Price
from database import categories_table, chatbots_table
from modules.shop.helper.keyboards import keyboards, back_btn, create_keyboard


START_ADD_PRODUCT, ONLINE_PAYMENT, \
    SET_TITLE, SET_CATEGORY, SET_PRICE, SET_DISCOUNT, \
    ASK_DESCRIPTION, SET_DESCRIPTION, SET_QUANTITY, CONFIRM_ADDING, \
    ADDING_CONTENT, FINISH_ADDING = range(12)


# EDIT WHAT- CONTENT OR PRODUCT
class AddingProductHandler(object):
    def start(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="back_to_main_menu")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        context.user_data["to_delete"].append(
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=context.bot.lang_dict["shop_admin_product_title"],
                reply_markup=reply_markup)))
        return SET_TITLE

    def set_title(self, update: Update, context: CallbackContext):
        context.user_data["new_product"] = Product(context)
        if len(update.message.text) <= 30:
            context.user_data["new_product"].name = update.message.text
        else:
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_name["shop_admin_name_too_long"],
                reply_markup=InlineKeyboardMarkup([
                             [back_btn("back_to_main_menu_btn", context)]])))
            return SET_TITLE
        delete_messages(update, context, True)
        category_list = categories_table.find({"bot_id": context.bot.id})
        if category_list.count() > 0:
            keyboard = create_keyboard(
                [InlineKeyboardButton(
                    text=i["name"],
                    callback_data=f"choose_category/{i['_id']}")
                    for i in category_list],
                [back_btn("back_to_main_menu_btn", context)])
            context.user_data["new_product"].send_full_template(
                update, context,
                context.bot.lang_dict["shop_admin_set_category"], keyboard)

        else:
            buttons = [
                [InlineKeyboardButton(
                    text=context.bot.lang_dict["back_button"],
                    callback_data="back_to_main_menu")]]
            reply_markup = InlineKeyboardMarkup(buttons)
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["add_product_didnt_set_category"],
                reply_markup=reply_markup))
        return SET_CATEGORY

    def set_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.message:
            if len(update.message.text) <= 30:
                categories_table.insert_one({
                    "name": update.message.text,
                    "query_name": update.message.text,
                    "bot_id": context.bot.id
                })
            else:
                context.user_data["to_delete"].append(context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=context.bot.lang_name["shop_admin_category_too_long"],
                    reply_markup=InlineKeyboardMarkup([
                                 [back_btn("back_to_main_menu_btn", context)]])))
                return SET_CATEGORY

        category_list = categories_table.find({"bot_id": context.bot.id})

        if category_list.count() > 0:
            keyboard = create_keyboard(
                [InlineKeyboardButton(
                    text=i["name"],
                    callback_data=f"choose_category/{i['_id']}")
                    for i in category_list],
                [back_btn("back_to_main_menu_btn", context)])
            context.user_data["new_product"].send_full_template(
                update, context,
                context.bot.lang_dict["shop_admin_set_category"],
                keyboard)
        return SET_CATEGORY

    def set_quantity(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.callback_query:
            context.user_data["new_product"].category_id = (
                update.callback_query.data.split("/")[1])
        context.user_data["new_product"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_write_quantity"],
            InlineKeyboardMarkup([
                [InlineKeyboardButton(text=context.bot.lang_dict["shop_admin_set_unlimited"],
                                      callback_data="unlimited")],
                [back_btn("back_to_main_menu_btn", context)]]))
        return SET_PRICE

    def set_price(self, update: Update, context: CallbackContext):
        if update.message:
            try:
                assert int(update.message.text) > 0
            except (ValueError, AssertionError):
                context.user_data["to_delete"].append(context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=context.bot.lang_dict["shop_admin_number_wrong"],
                    reply_markup=InlineKeyboardMarkup([
                        [back_btn("back_to_main_menu_btn", context)]])))
                return SET_PRICE
            if len(update.message.text) <= 10:
                context.user_data["new_product"].quantity = int(
                    format(Price.fromstring(update.message.text).amount))
                context.user_data["new_product"].unlimited = False
            else:
                context.user_data["to_delete"].append(context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=context.bot.lang_dict["shop_admin_quantity_too_big"],
                    reply_markup=InlineKeyboardMarkup([
                                 [back_btn("back_to_main_menu_btn", context)]])))
                return SET_PRICE
        elif update.callback_query.data == "unlimited":
            context.user_data["new_product"].quantity = 0
            context.user_data["new_product"].in_stock = 0
            context.user_data["new_product"].unlimited = True

        delete_messages(update, context, True)
        context.user_data["new_product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_write_your_price"],
            keyboards(context)["back_to_main_menu_keyboard"])
        return ASK_DESCRIPTION

    def ask_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        currency = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]["currency"]
        currency_limits = currency_limits_dict[currency]
        try:
            assert currency_limits["min"] < int(update.message.text) < currency_limits["max"]
        except (ValueError, AssertionError):
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["shop_admin_price_wrong"].format(
                    currency_limits["min"], currency, currency_limits["max"], currency),
                reply_markup=InlineKeyboardMarkup([
                    [back_btn("back_to_main_menu_btn", context)]])))
            return ASK_DESCRIPTION

        if len(update.message.text) <= 7:
            context.user_data["new_product"].price = float(
                format(Price.fromstring(update.message.text).amount, '.2f'))
            context.user_data["new_product"].discount_price = 0
        else:
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["shop_admin_price_too_big"],
                reply_markup=InlineKeyboardMarkup([
                             [back_btn("back_to_main_menu_btn", context)]])))
            return ASK_DESCRIPTION

        context.user_data["new_product"].send_full_template(
            update, context, context.bot.lang_dict["add_product_description"],
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_DESCRIPTION

    def set_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["new_product"].description = update.message.text
        context.user_data["new_product"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_files_adding"],
            keyboards(context)["back_to_main_menu_keyboard"])
        return ADDING_CONTENT

    def open_content_handler(self, update, context):
        delete_messages(update, context, True)
        if len(context.user_data["new_product"].content) < 10:
            context.user_data["new_product"].add_content_dict(update)
            text = context.bot.lang_dict["shop_admin_send_more_photo"].format(
                len(context.user_data["new_product"].content))
        else:
            text = context.bot.lang_dict["shop_admin_press_continue"]
        context.user_data["new_product"].send_full_template(
            update, context,
            text=text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    context.bot.lang_dict["shop_admin_continue_btn"],
                    callback_data="continue"),
                    back_btn("back_to_main_menu_btn", context=context)]
            ]))
        return ADDING_CONTENT

    def confirm_adding(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        currency = chatbots_table.find_one(
            {"bot_id": context.bot.id})["shop"]["currency"]

        category = categories_table.find_one(
            {"_id": context.user_data["new_product"].category_id})["name"]

        if (len(context.user_data["new_product"].description)
                > MAX_TEMP_DESCRIPTION_LENGTH):
            description = context.bot.lang_dict["add_product_description_above"]
        else:
            description = context.user_data["new_product"].description

        context.user_data["new_product"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_product_description"].format(
                currency=currency,
                name=context.user_data["new_product"].name,
                price=context.user_data["new_product"].price,
                discount_price=context.user_data["new_product"].discount_price,
                quantity=context.user_data["new_product"].quantity,
                category=category,
                # description=context.user_data["new_product"].description),
                description=description),
            keyboards(context)["confirm_add_product"])
        return FINISH_ADDING

    def finish_adding(self, update: Update, context: CallbackContext):
        context.bot.send_chat_action(update.effective_chat.id, "upload_photo")
        context.user_data["new_product"].create()
        return Welcome().back_to_main_menu(
            update, context,
            context.bot.lang_dict["shop_admin_adding_product_finished"])


ADD_PRODUCT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(AddingProductHandler().start,
                                       pattern=r"add_product")],

    states={
        SET_TITLE: [
            MessageHandler(Filters.text,
                           AddingProductHandler().set_title)],
        SET_CATEGORY: [
            MessageHandler(Filters.text, AddingProductHandler().set_category),
            CallbackQueryHandler(AddingProductHandler().set_quantity,
                                 pattern=r"choose_category")],

        SET_PRICE: [CallbackQueryHandler(AddingProductHandler().set_price,
                                         pattern=r"unlimited"),
                    MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                                   AddingProductHandler().set_price),
                    MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                                   AddingProductHandler().set_price),
                    MessageHandler(Filters.regex(r"^((?!@).)*$"),
                                   AddingProductHandler().set_quantity)],

        ASK_DESCRIPTION: [
            MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                           AddingProductHandler().ask_description),
            MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                           AddingProductHandler().ask_description),
            MessageHandler(Filters.regex(r"^((?!@).)*$"),
                           AddingProductHandler().set_price)
        ],

        SET_DESCRIPTION: [
            MessageHandler(Filters.text,
                           AddingProductHandler().set_description)],

        ADDING_CONTENT: [
            MessageHandler(Filters.all,
                           AddingProductHandler().open_content_handler),
            CallbackQueryHandler(AddingProductHandler().confirm_adding,
                                 pattern=r"continue"),
        ],
        FINISH_ADDING: [
            CallbackQueryHandler(AddingProductHandler().finish_adding,
                                 pattern=r"confirm_product"),
            MessageHandler(Filters.all,
                           callback=AddingProductHandler().finish_adding)]
    },

    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu")]
)
