import logging

from bson import ObjectId
from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, Filters, MessageHandler)

from modules.shop.admin_side.welcome import Welcome
from helper_funcs.misc import delete_messages
from database import categories_table, products_table
from modules.shop.helper.keyboards import (back_btn)

logging.basicConfig(format='%(asctime)s - %(name)s - '
                           '%(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

START_ADD_CATEGORY, SET_CATEGORY, RENAME_CATEGORY = range(3)
DELETE_CATEGORY_CONFIRM = 1


class ProductCategoryHandler(object):
    def menu(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        category_list = categories_table.find({"bot_id": context.bot.id})
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=i["name"],
                                   callback_data=f"edit_category/{i['_id']}")]
             for i in category_list]
            + [[InlineKeyboardButton(context.bot.lang_dict["shop_admin_add_category_btn"],
                                    callback_data="add_shop_category")],
            [back_btn("back_to_main_menu", context)]],
        )

        context.user_data["to_delete"] = [context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Choose ",
            reply_markup=keyboard)]

        return ConversationHandler.END

    def edit_category_menu(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        category_id = update.callback_query.data.replace("edit_category/", "")
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Change the name",
                                  callback_data="edit_name_shop_category/{}".format(category_id))],
            [InlineKeyboardButton("Delete",
                                  callback_data="delete_shop_category/{}".format(category_id))],

            [back_btn("back_to_main_menu", context)],
        ]
        )

        context.user_data["to_delete"] = [context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Choose your action about this shop category",
            reply_markup=keyboard)]

        return ConversationHandler.END

    def delete_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        category_id = update.callback_query.data.replace("delete_shop_category/", "")
        products = products_table.find({"bot_id": context.bot.id,
                                        "category_id": ObjectId(category_id)})
        category = categories_table.find_one({"bot_id": context.bot.id,
                                              "_id": ObjectId(category_id)})

        if products.count() > 0:
            context.user_data["category_id"] = category_id
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("YES", callback_data="del_cat_confirm")],
                [InlineKeyboardButton("NO", callback_data="back_to_main_menu")]])
            context.user_data["to_delete"] = [context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text=context.bot.lang_dict["shop_category_will_be_deleted"].
                    format(category["name"], str(products.count())),
                reply_markup=keyboard)]

            return DELETE_CATEGORY_CONFIRM
        else:
            keyboard = InlineKeyboardMarkup([
                [back_btn("back_to_main_menu", context)]])
            categories_table.delete_one({"bot_id": context.bot.id,
                                         "_id": ObjectId(category_id)})
            products_table.delete_many({"bot_id": context.bot.id,
                                        "category_id": ObjectId(category_id)})

            context.user_data["to_delete"] = [context.bot.send_message(
                chat_id=update.callback_query.message.chat_id,
                text="Category {} has been deleted".format(category["name"]),
                reply_markup=keyboard)]

            return ConversationHandler.END

    def delete_category_confirm(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        category_id = context.user_data["category_id"]
        category = categories_table.find_one({"bot_id": context.bot.id,
                                              "_id": ObjectId(category_id)})
        categories_table.delete_one({"bot_id": context.bot.id,
                                     "_id": ObjectId(category_id)})
        products_table.delete_many({"bot_id": context.bot.id,
                                    "category_id": ObjectId(category_id)})
        keyboard = InlineKeyboardMarkup([
            [back_btn("back_to_main_menu", context)]])

        context.user_data["to_delete"] = [context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Category {} has been deleted".format(category["name"]),
            reply_markup=keyboard)]

        return ConversationHandler.END

    def rename_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        context.user_data["category_id"] = update.callback_query.data.replace("edit_name_shop_category/", "")
        keyboard = InlineKeyboardMarkup([
            [back_btn("back_to_main_menu", context)],
        ]
        )

        context.user_data["to_delete"] = [context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text="Write a new name for this product category",
            reply_markup=keyboard)]

        return RENAME_CATEGORY

    def rename_category_finish(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        keyboard = InlineKeyboardMarkup([
            [back_btn("back_to_main_menu", context)],
        ]
        )
        categories_table.update({"bot_id": context.bot.id,
                                 "_id": ObjectId(context.user_data["category_id"])},
                                {"bot_id": context.bot.id,
                                 "_id": ObjectId(context.user_data["category_id"]),
                                 "name": update.message.text})
        context.user_data["to_delete"] = [context.bot.send_message(
            chat_id=update.message.chat_id,
            text=context.bot.lang_dict["shop_category_changed_name"],
            reply_markup=keyboard)]

        return ConversationHandler.END

    def add_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        category_list = categories_table.find({"bot_id": context.bot.id})
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=i["name"], callback_data="nigga_dont_touch_me")] for i in category_list] +
            [[back_btn("back_to_main_menu", context)]]
        )

        context.user_data["to_delete"] = [context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=context.bot.lang_dict["shop_category_add_new"],
            reply_markup=keyboard)]

        return START_ADD_CATEGORY

    def set_category(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        if update.message:
            categories_table.insert_one({
                "name": update.message.text,
                "query_name": update.message.text,
                "bot_id": context.bot.id
            })
            category_list = categories_table.find({"bot_id": context.bot.id})
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(text=i["name"],
                                      callback_data=f"edit_category/{i['_id']}")
                 for i in category_list],
                [back_btn("back_to_main_menu", context)],
                [InlineKeyboardButton(context.bot.lang_dict["shop_admin_continue_btn"],
                                      callback_data="continue")]]
            )
            context.user_data["to_delete"].append(context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["shop_category_add_or_continue"],
                reply_markup=keyboard))
        return START_ADD_CATEGORY

    def confirm_adding(self, update: Update, context: CallbackContext):
        delete_messages(update, context, True)
        return Welcome().back_to_main_menu(
            update, context, context.bot.lang_dict["shop_admin_adding_category_finished"])


CATEGORIES_HANDLER = CallbackQueryHandler(ProductCategoryHandler().edit_category_menu,
                                          pattern=r"edit_category")
EDIT_CATEGORIES_HANDLER = CallbackQueryHandler(ProductCategoryHandler().menu,
                                               pattern=r"categories")
RENAME_CATEGORY_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(ProductCategoryHandler().rename_category,
                                       pattern=r"edit_name_shop_category")],

    states={
        RENAME_CATEGORY: [
            MessageHandler(Filters.text, ProductCategoryHandler().rename_category_finish)],
    },

    fallbacks=[
        CallbackQueryHandler(Welcome().back_to_main_menu,
                             pattern=r"back_to_main_menu"),
    ]
)
DELETE_CATEGORY_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(ProductCategoryHandler().delete_category,
                                       pattern=r"delete_shop_category")],
    states={DELETE_CATEGORY_CONFIRM: [
        CallbackQueryHandler(ProductCategoryHandler().delete_category_confirm,
                             pattern="del_cat_confirm"),
    ]},
    fallbacks=[
        CallbackQueryHandler(Welcome().back_to_main_menu,
                             pattern=r"back_to_main_menu"),
    ])
ADD_CATEGORY_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(ProductCategoryHandler().add_category,
                                       pattern=r"add_shop_category")],

    states={  # TODO fix add category
        START_ADD_CATEGORY: [
            CallbackQueryHandler(ProductCategoryHandler().confirm_adding,
                                 pattern="continue"),
            MessageHandler(Filters.text, ProductCategoryHandler().set_category)],
    },

    fallbacks=[
        CallbackQueryHandler(Welcome().back_to_main_menu,
                             pattern=r"back_to_main_menu"),
    ]
)
