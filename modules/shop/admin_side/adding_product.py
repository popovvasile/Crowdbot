import logging
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.admin_side.welcome import Welcome
from modules.shop.components.product import Product
from helper_funcs.misc import delete_messages
from price_parser import Price
from database import categories_table
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
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Introduce the name of your new product",
                reply_markup=reply_markup))
        return SET_TITLE

    def set_title(self, update: Update, context: CallbackContext):
        context.user_data["new_product"] = Product(context)
        context.user_data["new_product"].name = update.message.text
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
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text="You didn't set any categories yet.\n"
                     "Please write a new category",
                reply_markup=reply_markup)
        return SET_CATEGORY

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
            "Write the quantity of your product. "
            "How many copies do you want to sell?\nPress 'Unlimited' to skip",
            InlineKeyboardMarkup([
                [InlineKeyboardButton(text="Unlimited",
                                      callback_data="unlimited")],
                [back_btn("back_to_main_menu_btn", context)]]))
        return SET_PRICE

    def set_price(self, update: Update, context: CallbackContext):
        if update.message:
            context.user_data["new_product"].quantity = int(
                format(Price.fromstring(update.message.text).amount))
            context.user_data["new_product"].unlimited = False
        elif update.callback_query.data == "unlimited":
            context.user_data["new_product"].quantity = 0
            context.user_data["new_product"].unlimited = True

        delete_messages(update, context, True)
        context.user_data["new_product"].send_full_template(
            update, context, "Write your price",
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_DISCOUNT

    def set_discount_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["new_product"].price = float(
            format(Price.fromstring(update.message.text).amount, '.2f'))
        context.user_data["new_product"].send_full_template(
            update, context,
            "Write a discount price for this product. Send 0 to skip",
            keyboards(context)["back_to_main_menu_keyboard"])
        return ASK_DESCRIPTION

    def ask_description(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        discount_price = float(
            format(Price.fromstring(update.message.text).amount, '.2f'))
        if discount_price >= context.user_data["new_product"].price:
            context.user_data["new_product"].send_full_template(
                update, context,
                "Your discount price is bigger than the price of the product "
                "itself. \n""Please write another discount price",
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
            "Add any files about this product: documents, images or videos."
            "\n_First file will be title file for the product_"
            "\nFiles 0/10",
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
            text = "Press 'Continue'"
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
        context.user_data["new_product"].send_full_template(
            update, context,
            "Confirm adding product",
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
                    MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                                   AddingProductHandler().set_price),
                    MessageHandler(Filters.regex(r"^((?!@).)*$"),
                                   AddingProductHandler().set_quantity)],

        SET_DISCOUNT: [
            MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                           AddingProductHandler().set_discount_price),
            MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                           AddingProductHandler().set_discount_price)],

        ASK_DESCRIPTION: [
            MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                           AddingProductHandler().ask_description),
            MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                           AddingProductHandler().ask_description)],

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
