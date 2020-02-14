import logging
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.admin_side.welcome import Welcome
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

START_ADD_PRODUCT, ONLINE_PAYMENT, PAID_CONTENT, \
    SET_TITLE, SET_CATEGORY, SET_PRICE, \
    SET_DESCRIPTION, SET_QUANTITY, CONFIRM_ADDING, \
    ADDING_OPEN_CONTENT, ADDING_CONTENT, FINISH_ADDING = range(12)


# TODO ADDING SKIP TO EVERYTHING
# ADD PRODUCT AND ADD CONTENT
# EDIT WHAT- CONTENT OR PRODUCT
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

    def set_title(self, update: Update, context: CallbackContext):
        context.user_data["new_product"] = Product(context)
        context.user_data["new_product"].name = update.message.text
        delete_messages(update, context, True)
        category_list = categories_table.find({"bot_id": context.bot.id})
        if category_list.count() > 0:
            keyboard = create_keyboard(
                [InlineKeyboardButton(text=i["name"],
                                      callback_data=f"choose_category/{i['_id']}")
                 for i in category_list],
                [back_btn("back_to_main_menu_btn", context)])
            context.user_data["new_product"].send_adding_product_template(
                update, context, context.bot.lang_dict["shop_admin_set_category"], keyboard)

        else:
            buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="back_to_main_menu")]]
            reply_markup = InlineKeyboardMarkup(
                buttons)
            context.bot.send_message(chat_id=update.message.chat_id,
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
                [InlineKeyboardButton(text=i["name"],
                                      callback_data=f"choose_category/{i['_id']}")
                 for i in category_list],
                [back_btn("back_to_main_menu_btn", context)])
            context.user_data["new_product"].send_adding_product_template(
                update, context, context.bot.lang_dict["shop_admin_set_category"], keyboard)
        return SET_CATEGORY

    def set_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.callback_query:
            context.user_data["new_product"].category_id = \
                update.callback_query.data.split("/")[1]
        context.user_data["new_product"].send_adding_product_template(
            update, context, "Write the quantity of your product. How many copies do you want to sell?",
            keyboards(context)["back_to_main_menu_keyboard"])
        return SET_QUANTITY

    def set_quantity(self, update: Update, context: CallbackContext):
        context.user_data["new_product"].quantity = format(Price.fromstring(update.message.text).amount)

        delete_messages(update, context, True)
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
            return PAID_CONTENT
        else:
            return ADDING_CONTENT

    def paid_content(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Is your product a physical one or do you want to sell content?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("CONTENT",
                                          callback_data="product_type_content")],
                    # => ADDING_CLOSED_CONTENT => ADDING_CONTENT
                    [InlineKeyboardButton("PHYSICAL",
                                          callback_data="product_type_physical")],
                    # => ADDING_CONTENT
                    [back_btn("back_to_main_menu_btn", context=context)]
                ])))
        context.user_data["new_product"] = Product(context)
        context.user_data["new_product"].name = update.message.text
        return ADDING_CONTENT

    def closed_content_handler(self, update, context):

        context.user_data["to_delete"].append(update.message)
        reply_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                               callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        if "content" not in context.user_data:
            context.user_data["content"] = []
        general_list = context.user_data["content"]
        if update.message:
            if update.message.text:
                general_list.append({"text": update.message.text})

            if update.message.photo:
                photo_file = update.message.photo[-1].get_file().file_id
                general_list.append({"photo_file": photo_file})

            if update.message.audio:
                audio_file = update.message.audio.get_file().file_id
                general_list.append({"audio_file": audio_file})

            if update.message.voice:
                voice_file = update.message.voice.get_file().file_id
                general_list.append({"voice_file": voice_file})

            if update.message.document:
                document_file = update.message.document.get_file().file_id
                general_list.append({"document_file": document_file})

            if update.message.video:
                video_file = update.message.video.get_file().file_id
                general_list.append({"video_file": video_file})

            if update.message.video_note:
                video_note_file = update.message.video_note.get_file().file_id
                general_list.append({"video_note_file": video_note_file})
            if update.message.animation:
                animation_file = update.message.animation.get_file().file_id
                general_list.append({"animation_file": animation_file})
            if update.message.sticker:
                sticker_file = update.message.sticker.get_file().file_id
                general_list.append({"sticker_file": sticker_file})
            message = update.message
        else:
            message = update.callback_query.message
        context.user_data["to_delete"].append(message.reply_text(context.bot.lang_dict["back_text"],
                                                                 reply_markup=reply_markup))
        done_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                              callback_data="product_type_physical")]]
        done_reply_markup = InlineKeyboardMarkup(
            done_buttons)
        context.user_data["to_delete"].append(
            message.reply_text(context.bot.lang_dict["add_menu_buttons_str_4"],
                               reply_markup=done_reply_markup))
        context.user_data["secret_content"] = general_list
        return ADDING_CONTENT

    def open_content_handler(self, update, context):
        context.user_data["to_delete"].append(update.message)
        reply_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                               callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_buttons)
        if "content" not in context.user_data:
            context.user_data["content"] = []
        general_list = context.user_data["content"]

        if update.message:
            if update.message.text:
                general_list.append({"text": update.message.text})

            if update.message.photo:  # TODO triple check
                photo_file = update.message.photo[-1].get_file().file_id
                general_list.append({"photo_file": photo_file})
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
                context.user_data["content"] = general_list
                return ADDING_OPEN_CONTENT

            if update.message.audio:
                audio_file = update.message.audio.get_file().file_id
                general_list.append({"audio_file": audio_file})

            if update.message.voice:
                voice_file = update.message.voice.get_file().file_id
                general_list.append({"voice_file": voice_file})

            if update.message.document:
                document_file = update.message.document.get_file().file_id
                general_list.append({"document_file": document_file})

            if update.message.video:
                video_file = update.message.video.get_file().file_id
                general_list.append({"video_file": video_file})

            if update.message.video_note:
                video_note_file = update.message.video_note.get_file().file_id
                general_list.append({"video_note_file": video_note_file})
            if update.message.animation:
                animation_file = update.message.animation.get_file().file_id
                general_list.append({"animation_file": animation_file})
            if update.message.sticker:
                sticker_file = update.message.sticker.get_file().file_id
                general_list.append({"sticker_file": sticker_file})
            message = update.message
        else:
            message = update.callback_query.message
        context.user_data["to_delete"].append(message.reply_text(context.bot.lang_dict["back_text"],
                                                                 reply_markup=reply_markup))
        done_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["done_button"], callback_data="continue")]]
        done_reply_markup = InlineKeyboardMarkup(
            done_buttons)
        context.user_data["to_delete"].append(
            message.reply_text(context.bot.lang_dict["add_menu_buttons_str_4"],
                               reply_markup=done_reply_markup))
        context.user_data["content"] = general_list
        return ADDING_OPEN_CONTENT

    def confirm_adding(self, update: Update, context: CallbackContext):
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
            MessageHandler(Filters.text,
                           AddingProductHandler().set_title)],
        SET_CATEGORY: [
            MessageHandler(Filters.text, AddingProductHandler().set_category),
            CallbackQueryHandler(AddingProductHandler().set_price,
                                 pattern=r"choose_category")
        ],

        SET_QUANTITY: [MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                                      AddingProductHandler().set_quantity)],
        SET_DESCRIPTION: [MessageHandler(Filters.regex(r'(\d+\.\d{1,2})|(\d+\,\d{1,2})'),
                                         AddingProductHandler().set_description),
                          MessageHandler(Filters.regex(r'^[-+]?([1-9]\d*|0)$'),
                                         AddingProductHandler().set_description),
                          MessageHandler(Filters.regex(r"^((?!@).)*$"), AddingProductHandler().set_price),
                          ],
        PAID_CONTENT: [MessageHandler(Filters.all, callback=AddingProductHandler().paid_content)],

        ADDING_CONTENT: [CallbackQueryHandler(AddingProductHandler().open_content_handler,
                                              pattern=r"product_type_physical"),
                         CallbackQueryHandler(AddingProductHandler().closed_content_handler,
                                              pattern=r"product_type_content"),

                         MessageHandler(Filters.all, callback=AddingProductHandler().closed_content_handler)
                         ],
        ADDING_OPEN_CONTENT: [
            MessageHandler(Filters.all, callback=AddingProductHandler().open_content_handler),
            CallbackQueryHandler(AddingProductHandler().confirm_adding,
                                 pattern=r"continue"),
        ],
        FINISH_ADDING: [CallbackQueryHandler(AddingProductHandler().finish_adding,
                                             pattern=r"confirm_product"),
                        MessageHandler(Filters.all, callback=AddingProductHandler().finish_adding)]

    },

    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu"),

               ]
)
