from telegram import (ParseMode, InputMediaPhoto, InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.error import BadRequest
from bson.objectid import ObjectId
from datetime import datetime

from modules.shop.helper.strings import emoji
from modules.shop.helper.keyboards import back_btn, sizes_list
from helper_funcs.misc import get_obj
from modules.shop.helper.helper import send_media_arr
from database import products_table, categories_table
from modules.shop.components.brand import Brand


class Product(object):
    def __init__(self, context, obj: (ObjectId, dict, str) = None):
        self.context = context
        product = get_obj(products_table, obj)
        self._id = product.get("_id")
        self.article = product.get("article")
        self.sold = product.get("sold")
        self.price = product.get("price")
        self.description = product.get("description")
        self.name = product.get("name")
        self.discount_price = product.get("discount_price")
        self.sizes = product.get("sizes", list())
        self.order_ids = product.get("order_ids", list())
        self.images = product.get("images", list())
        self.in_trash = product.get("in_trash")
        self.category_id = product.get("category_id")
        self.brand_id = product.get("brand_id")

    @property
    def brand_id(self):
        return self._brand_id

    @brand_id.setter
    def brand_id(self, _id):
        self._brand_id = _id
        self.brand = Brand(self.context, self.brand_id)

    @property
    def category_id(self):
        return self._category_id

    @category_id.setter
    def category_id(self, _id):
        _id = ObjectId(_id) if type(_id) is str else _id
        self._category_id = _id
        self.category = categories_table.find_one({"_id": ObjectId(_id)})

    @property
    def template(self):
        return self.context.bot.lang_dict["shop_admin_product_template"].format(
            self.article, True if not self.sold else False,
            self.brand.name, self.category["name"], self.price,
            self.sizes_text)

    def full_template(self, long_description=None):
        description = self.context.bot.lang_dict["shop_admin_description_below"] \
            if long_description else self.description
        return self.context.bot.lang_dict["shop_admin_full_product_template"].format(
            self.article, True if not self.sold else False,
            self.name, self.brand.name, self.category["name"],
            description, self.price, self.discount_price,
            self.sizes_text)

    @property
    def sizes_text(self):
        return "\n".join([f"{i['size']} - {i['quantity']}"
                          for i in self.sizes]) \
            if self.sizes else "💢 *Товар Продан*"

    # Admin Reply Markup For Product In Products List
    @property
    def admin_keyboard(self):
        kb = [[]]
        if self.in_trash:
            kb[0].append(InlineKeyboardButton(
                            text=self.context.bot.lang_dict["shop_admin_restore_btn"],
                            callback_data=f"restore_product/{self._id}"))
            return InlineKeyboardMarkup(kb)
        kb[0].append(InlineKeyboardButton(
                        text=self.context.bot.lang_dict["shop_admin_edit_btn"],
                        callback_data=f"edit_product/{self._id}"))
        if not self.order_ids:
            kb[0].append(InlineKeyboardButton(
                            text=self.context.bot.lang_dict["shop_admin_to_trash_btn"],
                            callback_data=f"to_trash/{self._id}"))

        return InlineKeyboardMarkup(kb)

    # Method For Sending Product Template While Adding New Product
    def send_adding_product_template(self, update, context, text, kb=None):
        if len(self.images) < 2:
            context.user_data["to_delete"].append(
                context.bot.send_photo(
                    chat_id=update.effective_chat.id, photo=self.images[0],
                    caption=text, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb))
        else:
            # todo mb don't delete media group until product adding finish
            context.user_data["to_delete"].extend(
                [i for i in
                 context.bot.send_media_group(
                     chat_id=update.effective_chat.id,
                     media=[InputMediaPhoto(i)
                            for i in self.images])])

            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=text,
                    reply_markup=kb, parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=context.user_data
                    ["to_delete"][-len(context.user_data["product_images"]
                                       )].message_id))

    # Method For Showing Product Template For Customer In Products List
    # TODO add the "pay" button and more images/files/etc.
    def send_customer_template(self, update, context):
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Buy", callback_data=f"buy/{self._id}")],
            [InlineKeyboardButton("Open", callback_data=f"open/{self._id}")]
        ])
        context.user_data["to_delete"].append(
            context.bot.send_photo(
                chat_id=update.effective_chat.id, photo=self.images[0],
                caption=self.template, parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup, timeout=10))

    # def customer_markup(self):
    #     return InlineKeyboardMarkup([
    #         InlineKeyboardButton("Buy", callback_data=f"buy/{self._id}")
    #     ])

    def send_admin_short_template(self, update, context, text=None, kb=None):
        text = text if text else self.template
        kb = self.admin_keyboard if kb is True else None if kb is None else kb
        try:
            context.user_data["to_delete"].append(
                context.bot.send_photo(
                    chat_id=update.effective_chat.id, photo=self.images[0],
                    caption=text, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb, timeout=10))
        except (BadRequest, IndexError):
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_image_exception"] + "\n\n" + text,
                    parse_mode=ParseMode.MARKDOWN, reply_markup=kb))

    def send_full_template(self, update, context, text=None, kb=None):
        full_media_group = [InputMediaPhoto(
            i, f'{self.article} - {self.name}') for i in self.images]
        send_media_arr(full_media_group, update, context)
        if len(self.description) > 2500:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         self.full_template(
                                             long_description=True),
                                         parse_mode=ParseMode.MARKDOWN))
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         self.description))
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         text, reply_markup=kb,
                                         parse_mode=ParseMode.MARKDOWN))
        else:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         f"{self.full_template()}"
                                         f"\n{text}",
                                         reply_markup=kb,
                                         parse_mode=ParseMode.MARKDOWN))

    def send_sizes_menu(self, update, context):
        self.send_full_template(update, context, context.bot.lang_dict["shop_admin_sizes_menu_title"])
        for item in self.sizes:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(emoji["x"],
                                      callback_data=f"remove_size/"
                                                    f"{item['size']}"),
                 InlineKeyboardButton(context.bot.lang_dict["shop_admin_edit_btn"],
                                      callback_data=f"change_size_quantity/"
                                                    f"{item['size']}")]
            ])
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_product_size_temp"].format(
                        item["size"], item["quantity"]),
                    reply_markup=kb,
                    parse_mode=ParseMode.MARKDOWN))
        kb = [[]]
        if len(self.sizes) < len(sizes_list):
            kb[0].append(InlineKeyboardButton(context.bot.lang_dict["shop_admin_add_size_btn"],
                                              callback_data="add_size"))
        kb[0].append(back_btn("back_to_edit", context))
        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Nice bro 😎",
                                     reply_markup=InlineKeyboardMarkup(kb)))

    def add_keyboard(self, order):
        # remove items that already exist in the order
        sizes = [size for size in self.sizes
                 if not any(order_item["size"] == size["size"]
                            and order_item["product"]["article"] == self.article
                            for order_item in order.items)]
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text=item["size"],
                                  callback_data=f"finish_add_to_order/"
                                                f"{self.article}/"
                                                f"{item['size']}")
             for item in sizes]
        ])

    def update(self, json=None):
        if json:
            products_table.update_one({"_id": self._id}, {"$set": json})
        else:
            products_table.update_one(
                {"_id": self._id},
                {"$set":
                    {"price": self.price,
                     # "article": 1,
                     "discount_price": self.discount_price,
                     "description": self.description,
                     "name": self.name,
                     "category_id": self.category_id,
                     "brand_id": self.brand_id,
                     "images": self.images,
                     "sizes": self.sizes,
                     "sold": self.sold,
                     "in_trash": self.in_trash,
                     "order_ids": self.order_ids}})
        self.__init__(self._id)
        # self.reset_sold_status()

    def add_sizes(self, sizes):
        for size_dict in sizes:
            # $addToSet
            products_table.update_one({"_id": self._id},
                                      {"$push": {"sizes": size_dict}})
        self.__init__(self._id)
        # self.reset_sold_status()

    def remove_size(self, size_name):
        products_table.update_one({"_id": self._id},
                                  {"$pull": {"sizes": {"size": size_name}}})
        self.__init__(self._id)
        # self.reset_sold_status()

    def edit_size(self, size_dict):
        next(size for size in self.sizes
             if size["size"] == size_dict["size"]
             )["quantity"] = size_dict["quantity"]
        self.update()

    # Only For cloth shop method - for refresh "sold" field after product edit
    def reset_sold_status(self):
        products_table.update_one(
            {"_id": self._id},
            {"$set": {"sold": not any(size for size in self.sizes
                                     if size["quantity"] > 0)}})
        self.__init__(self._id)

    def create(self):
        products_table.insert_one({
            # "article": 1,
            "price": self.price,
            "discount_price": 0,
            "description": self.description,
            "name": f"{self.brand.name} {self.category['name']}",
            "category_id": self.category_id,
            "brand_id": self.brand_id,
            "images": self.images,
            "sizes": self.sizes,
            "sold": False,
            "in_trash": False,
            "on_sale": True,
            "order_ids": list(),
            "creation_timestamp": datetime.now()
        })
