import html

from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.admin_side.welcome import Welcome
from modules.shop.admin_side.categories import validate_category_name, MAX_CATEGORIES_COUNT
from modules.shop.components.product import Product
from modules.shop.helper.keyboards import keyboards, back_btn, create_keyboard
from helper_funcs.misc import delete_messages
from helper_funcs.constants import MAX_TEMP_DESCRIPTION_LENGTH, MAX_PRODUCT_NAME_LENGTH
from database import categories_table, chatbots_table


(START_ADD_PRODUCT, ONLINE_PAYMENT,
 SET_TITLE, SET_CATEGORY, SET_PRICE, SET_DISCOUNT,
 ASK_DESCRIPTION, SET_DESCRIPTION, SET_QUANTITY, CONFIRM_ADDING,
 ADDING_CONTENT, FINISH_ADDING) = range(12)


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
        if len(update.message.text) <= MAX_PRODUCT_NAME_LENGTH:
            context.user_data["new_product"].name = update.message.text
        else:
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["shop_admin_name_too_long"],
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
            final_text = context.bot.lang_dict["shop_admin_set_category"]
            category_list = categories_table.find({"bot_id": context.bot.id})

            name_request = validate_category_name(update.message.text, context)
            if name_request["ok"]:
                if category_list.count() >= MAX_CATEGORIES_COUNT:
                    final_text = context.bot.lang_dict["too_much_categories_blink"]

                else:
                    categories_table.insert_one({
                        "name": name_request["name"],
                        "query_name": name_request["name"],
                        "bot_id": context.bot.id
                    })
                    category_list = categories_table.find({"bot_id": context.bot.id})
                reply_markup = create_keyboard(
                    [InlineKeyboardButton(
                        text=i["name"],
                        callback_data=f"choose_category/{i['_id']}")
                        for i in category_list],
                    [back_btn("back_to_main_menu_btn", context)])
            else:
                # category_list = categories_table.find({"bot_id": context.bot.id})
                final_text = name_request["error_message"]
                if category_list.count() > 0:
                    reply_markup = create_keyboard(
                        [InlineKeyboardButton(
                            text=i["name"],
                            callback_data=f"choose_category/{i['_id']}")
                            for i in category_list],
                        [back_btn("back_to_main_menu_btn", context)])
                else:
                    reply_markup = InlineKeyboardMarkup([
                        [back_btn("back_to_main_menu_btn", context)]])

            context.user_data["new_product"].send_full_template(
                update, context,
                final_text,
                reply_markup)
            return SET_CATEGORY

    def ask_quantity(self, update: Update, context: CallbackContext):
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
        return SET_QUANTITY

    def ask_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.message:
            quantity_request = context.user_data["new_product"].create_quantity(
                update, context)
            if quantity_request["ok"]:
                context.user_data["new_product"].quantity = quantity_request["quantity"]
                context.user_data["new_product"].unlimited = False
            else:
                context.user_data["to_delete"].append(context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=quantity_request["error_message"],
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(
                            text=context.bot.lang_dict["shop_admin_set_unlimited"],
                            callback_data="unlimited")],
                        [back_btn("back_to_main_menu_btn", context)]])))
                return SET_QUANTITY
            # try:
            #     assert int(update.message.text) > 0
            # except AssertionError:
            #     context.user_data["to_delete"].append(context.bot.send_message(
            #         chat_id=update.message.chat_id,
            #         text=context.bot.lang_dict["shop_admin_number_wrong"],
            #         reply_markup=InlineKeyboardMarkup([
            #             [back_btn("back_to_main_menu_btn", context)]])))
            #     return SET_QUANTITY
            # except ValueError:
            #     context.user_data["to_delete"].append(context.bot.send_message(
            #         chat_id=update.message.chat_id,
            #         text=context.bot.lang_dict["shop_admin_number_not_integer"],
            #         reply_markup=InlineKeyboardMarkup([
            #             [back_btn("back_to_main_menu_btn", context)]])))
            #     return SET_QUANTITY
            # if len(update.message.text) <= 10:
            #     context.user_data["new_product"].quantity = int(
            #         format(Price.fromstring(update.message.text).amount))
            #     context.user_data["new_product"].unlimited = False
            # else:
            #     context.user_data["to_delete"].append(context.bot.send_message(
            #         chat_id=update.message.chat_id,
            #         text=context.bot.lang_dict["shop_admin_quantity_too_big"],
            #         reply_markup=InlineKeyboardMarkup([
            #                      [back_btn("back_to_main_menu_btn", context)]])))
            #     return SET_QUANTITY
        elif update.callback_query.data == "unlimited":
            context.user_data["new_product"].quantity = 0
            context.user_data["new_product"].unlimited = True

        context.user_data["new_product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_write_your_price"],
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_PRICE

    def ask_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        price_request = context.user_data["new_product"].create_price(update, context)
        if price_request["ok"]:
            context.user_data["new_product"].price = price_request["price"]
            context.user_data["new_product"].discount_price = 0
            context.user_data["new_product"].send_full_template(
                update, context, context.bot.lang_dict["add_product_description"],
                keyboards(context)["back_to_main_menu_keyboard"])
            return SET_DESCRIPTION
        else:
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=price_request["error_message"],
                reply_markup=InlineKeyboardMarkup([
                    [back_btn("back_to_main_menu_btn", context)]])))
            return SET_PRICE

    """currency = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]["currency"]
        currency_limits = currency_limits_dict[currency]
        try:
            assert currency_limits["min"] < float(update.message.text) < currency_limits["max"]
        except AssertionError:
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["shop_admin_price_wrong"].format(
                    currency_limits["min"], currency, currency_limits["max"], currency),
                reply_markup=InlineKeyboardMarkup([
                    [back_btn("back_to_main_menu_btn", context)]])))
            return ASK_DESCRIPTION
        except ValueError:
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["add_product_wrong_floating_point_number"],
                reply_markup=InlineKeyboardMarkup([
                    [back_btn("back_to_main_menu_btn", context)]])))
            return ASK_DESCRIPTION
        if len(update.message.text) <= len(str(currency_limits["max"])):
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
        return SET_DESCRIPTION"""

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
            description = html.escape(context.user_data["new_product"].description, quote=False)

        context.user_data["new_product"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_product_description"].format(
                currency=currency,
                name=html.escape(context.user_data["new_product"].name, quote=False),
                price=context.user_data["new_product"].price,
                quantity=context.user_data["new_product"].quantity_str,
                category=html.escape(category, quote=False),
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
    allow_reentry=True,
    entry_points=[CallbackQueryHandler(AddingProductHandler().start,
                                       pattern=r"add_product")],

    states={
        SET_TITLE: [
            MessageHandler(Filters.text,
                           AddingProductHandler().set_title)],
        SET_CATEGORY: [
            MessageHandler(Filters.text, AddingProductHandler().set_category),
            CallbackQueryHandler(AddingProductHandler().ask_quantity,
                                 pattern=r"choose_category")],

        # todo 3 regexes vs just Filters.text(it looks like everything works anyway)
        SET_QUANTITY: [CallbackQueryHandler(AddingProductHandler().ask_price,
                                            pattern=r"unlimited"),
                       MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                                      AddingProductHandler().ask_price),
                       MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                                      AddingProductHandler().ask_price),
                       MessageHandler(Filters.regex(r"^((?!@).)*$"),
                                      AddingProductHandler().ask_price),
                       # MessageHandler(Filters.text,
                       #                AddingProductHandler().ask_price),
                       ],

        # todo 3 regexes vs just Filters.text(it looks like everything works anyway)
        SET_PRICE: [MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                                   AddingProductHandler().ask_description),
                    MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                                   AddingProductHandler().ask_description),
                    MessageHandler(Filters.regex(r"^((?!@).)*$"),
                                   AddingProductHandler().ask_description)
                    # MessageHandler(Filters.text,
                    #                AddingProductHandler().ask_description)
                    ],

        # ASK_DESCRIPTION: [
        #     MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
        #                    AddingProductHandler().ask_description),
        #     MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
        #                    AddingProductHandler().ask_description),
        #     MessageHandler(Filters.regex(r"^((?!@).)*$"),
        #                    AddingProductHandler().ask_price)
        # ],

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
            # MessageHandler(Filters.all,
            #                callback=AddingProductHandler().finish_adding)
        ]
    },

    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu")]
)
