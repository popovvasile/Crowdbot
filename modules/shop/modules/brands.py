from telegram import Update
from telegram.ext import (ConversationHandler, CallbackQueryHandler,
                          CallbackContext, MessageHandler, Filters)
from helper_funcs.misc import delete_messages
from helper_funcs.pagination import set_page_key
from modules.shop.helper.decorator import catch_request_exception
from modules.shop.helper.keyboards import keyboards
from modules.shop.components.brand import Brand
from .welcome import Welcome
from modules.shop.helper.helper import clear_user_data


class BrandsHandler(object):
    @catch_request_exception
    def brands(self, update: Update, context: CallbackContext):
        set_page_key(update, context)
        # resp = requests.get(f"{conf['API_URL']}/brands",   # TODO
        #                     params={"page": context.user_data["page"],
        #                             "per_page": 3})
        # pagin = APIPaginatedPage(resp)
        # pagin.start(update, context,
        #             context.bot.lang_dict["shop_admin_brands_title"],
        #             context.bot.lang_dict["shop_admin_no_brands"])
        # for brand in pagin.data["data"]:
        #     Brand(context, brand).send_template(update, context)
        # pagin.send_pagin(update, context)
        return BRANDS

    @catch_request_exception
    def edit(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        if update.callback_query \
                and update.callback_query.data.startswith("edit_brand"):
            brand_id = int(update.callback_query.data.split("/")[1])
            context.user_data["brand"] = Brand(context, brand_id)
        context.user_data["brand"].send_template(
            update, context,
            context.bot.lang_dict["shop_admin_edit_brand_menu"],
            keyboards(context)["edit_brand"])
        return EDIT

    def price(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["brand"].send_template(
            update, context,
            context.bot.lang_dict["shop_admin_set_brand_price"],
            keyboards(context)["back_to_brands"])
        return PRICE

    @catch_request_exception
    def finish_price(self, update: Update, context: CallbackContext):
        delete_messages(update, context)
        context.user_data["brand"].edit({"price": update.message.text})
        return self.edit(update, context)

    def back_to_brands(self, update: Update, context: CallbackContext):
        page = context.user_data.get("page")
        clear_user_data(context)
        context.user_data["page"] = page
        return self.brands(update, context)


BRANDS, EDIT, PRICE = range(3)


BRANDS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(BrandsHandler().brands,
                                       pattern=r"brands")],
    states={
        BRANDS: [CallbackQueryHandler(BrandsHandler().brands,
                                      pattern="^[0-9]+$"),
                 CallbackQueryHandler(BrandsHandler().edit,
                                      pattern=r"edit_brand")],

        EDIT: [CallbackQueryHandler(BrandsHandler().price,
                                    pattern="change_brand_price")],

        PRICE: [MessageHandler(Filters.regex("^[0-9]+$"),
                               BrandsHandler().finish_price)]
    },
    fallbacks=[CallbackQueryHandler(Welcome().back_to_main_menu,
                                    pattern=r"back_to_main_menu"),
               CallbackQueryHandler(BrandsHandler().back_to_brands,
                                    pattern="back_to_brands")]
)
