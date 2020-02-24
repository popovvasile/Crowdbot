import logging
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.admin_side.welcome import Welcome
from modules.shop.components.product import Product
from helper_funcs.misc import delete_messages
from price_parser import Price
from database import categories_table, chatbots_table
from modules.shop.helper.keyboards import keyboards, back_btn, create_keyboard

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)

START_ADD_PRODUCT, ONLINE_PAYMENT, \
    SET_TITLE, SET_CATEGORY, SET_PRICE, SET_DISCOUNT, \
    ASK_DESCRIPTION, SET_DESCRIPTION, SET_QUANTITY, CONFIRM_ADDING, \
    ADDING_CONTENT, FINISH_ADDING = range(12)


# EDIT WHAT- CONTENT OR PRODUCT
class AddingProductHandler(object):
    def start(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
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
        context.user_data["new_product"].name = update.message.text
        if len(update.message.text) <= 4096:
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
                text="You didn't set any categories yet.\n"
                     "Please write a new category",
                reply_markup=reply_markup))
        return SET_CATEGORY

    def set_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        category_list = categories_table.find({"bot_id": context.bot.id})
        if update.message:
            if len(update.message.text) <= 4096:
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
            context.user_data["new_product"].unlimited = True

        delete_messages(update, context, True)
        context.user_data["new_product"].send_full_template(
            update, context, context.bot.lang_dict["shop_admin_write_your_price"],
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_DISCOUNT

    def set_discount_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        try:
            assert float(update.message.text) > 0
        except (ValueError, AssertionError):
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["shop_admin_number_wrong"],
                reply_markup=InlineKeyboardMarkup([
                    [back_btn("back_to_main_menu_btn", context)]])))
            return SET_DISCOUNT
        if update.message:
            if len(update.message.text) <= 7:
                context.user_data["new_product"].price = float(
                    format(Price.fromstring(update.message.text).amount, '.2f'))
                context.user_data["new_product"].unlimited = False
            else:
                context.user_data["to_delete"].append(context.bot.send_message(
                    chat_id=update.message.chat_id,
                    text=context.bot.lang_dict["shop_admin_price_too_big"],
                    reply_markup=InlineKeyboardMarkup([
                                 [back_btn("back_to_main_menu_btn", context)]])))
                return SET_DISCOUNT
        context.user_data["new_product"].price = float(
            format(Price.fromstring(update.message.text).amount, '.2f'))
        context.user_data["new_product"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_write_your_discount_price"],
            keyboards(context)["back_to_main_menu_keyboard"])
        return ASK_DESCRIPTION

    def ask_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        try:
            assert float(update.message.text) >= 0
        except (ValueError, AssertionError):
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["shop_admin_number_wrong"],
                reply_markup=InlineKeyboardMarkup([
                    [back_btn("back_to_main_menu_btn", context)]])))
            return ASK_DESCRIPTION
        if len(update.message.text) <= 10:
            discount_price = float(
                format(Price.fromstring(update.message.text).amount, '.2f'))
        else:
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["shop_admin_discount_price_too_big"],
                reply_markup=InlineKeyboardMarkup([
                    [back_btn("back_to_main_menu_btn", context)]])))
            return ASK_DESCRIPTION
        if discount_price >= context.user_data["new_product"].price:
            context.user_data["new_product"].send_full_template(
                update, context,
                context.bot.lang_dict["shop_admin_discount_bigger_than_price"],
                keyboards(context)["back_to_main_menu_keyboard"])
            return ASK_DESCRIPTION
        context.user_data["new_product"].discount_price = discount_price
        context.user_data["new_product"].send_full_template(
            update, context, "Write description of this product.",
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
            """# video_note_file and sticker_file - don't have captions
            if update.message.photo:
                photo_file = update.message.photo[-1].get_file().file_id
                context.user_data["new_product"].content.append(
                    {"file_id": photo_file,
                     "type": "photo_file"
                     # "photo_file": photo_file
                     })

            elif update.message.audio:
                audio_file = update.message.audio.get_file().file_id
                context.user_data["new_product"].content.append(
                    {"file_id": audio_file,
                     "type": "photo_file",
                     # "audio_file": audio_file,
                     "name": update.message.audio.title
                     })

            elif update.message.voice:
                voice_file = update.message.voice.get_file().file_id
                context.user_data["new_product"].content.append(
                    {"file_id": voice_file,
                     "type": "photo_file",
                     # "voice_file": voice_file
                     })

            elif update.message.document:
                document_file = update.message.document.get_file().file_id
                context.user_data["new_product"].content.append(
                    {"file_id": document_file,
                     "type": "photo_file",
                     # "document_file": document_file,
                     "name": update.message.document.file_name})

            elif update.message.video:
                video_file = update.message.video.get_file().file_id
                context.user_data["new_product"].content.append(
                    {"file_id": video_file,
                     "type": "photo_file",
                     # "video_file": video_file
                     })

            elif update.message.animation:
                animation_file = update.message.animation.get_file().file_id
                context.user_data["new_product"].content.append(
                    {"file_id": animation_file,
                     "type": "photo_file",
                     # "animation_file": animation_file
                     })"""
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
        currency = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]["currency"]
        category = categories_table.find_one({"_id": context.user_data["new_product"].category_id})["name"]
        context.user_data["new_product"].send_full_template(
            update, context,
            context.bot.lang_dict["shop_admin_product_description"].format(
                currency=currency,
                name=context.user_data["new_product"].name,
                price=context.user_data["new_product"].price,
                discount_price=context.user_data["new_product"].discount_price,
                quantity=context.user_data["new_product"].quantity,
                category=category,
                description=context.user_data["new_product"].description),
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

        SET_DISCOUNT: [
            MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                           AddingProductHandler().set_discount_price),
            MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                           AddingProductHandler().set_discount_price),
            MessageHandler(Filters.regex(r"^((?!@).)*$"),
                           AddingProductHandler().set_price)
        ],

        ASK_DESCRIPTION: [
            MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                           AddingProductHandler().ask_description),
            MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                           AddingProductHandler().ask_description),
            MessageHandler(Filters.regex(r"^((?!@).)*$"),
                           AddingProductHandler().set_discount_price)
        ],

        SET_DESCRIPTION: [
            MessageHandler(Filters.text,
                           AddingProductHandler().set_description)],

        ADDING_CONTENT: [
            # video_note_file and sticker_file - don't have captions
            # todo change Filters.all
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
