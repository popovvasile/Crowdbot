from telegram import (ParseMode, InputMediaPhoto, InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.error import BadRequest
from bson.objectid import ObjectId
from datetime import datetime
from helper_funcs.misc import get_obj
from modules.shop.helper.helper import send_media_arr
from database import products_table, categories_table


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
        self.order_ids = product.get("order_ids", list())
        self.images = product.get("images", list())
        self.in_trash = product.get("in_trash")
        self.category_id = product.get("category_id")
        self.shipping = product.get("shipping")
        self.online_payment = product.get("online_payment")

    @property
    def category_id(self):
        return self._category_id

    @category_id.setter
    def category_id(self, _id):
        _id = ObjectId(_id) if type(_id) is str else _id
        self._category_id = _id
        print(_id)
        print(categories_table.find_one({"_id": ObjectId(_id)}))
        self.category = categories_table.find_one({"_id": _id})

    @property
    def template(self):
        return self.context.bot.lang_dict["shop_admin_product_template"].format(
            self.name, True if not self.sold else False, self.category["name"], self.price,
        )

    def full_template(self, long_description=None):
        description = self.context.bot.lang_dict["shop_admin_description_below"] \
            if long_description else self.description
        return self.context.bot.lang_dict["shop_admin_full_product_template"].format(
            True if not self.sold else False,
            self.name,
            self.category["name"],
            description,
            self.price,
            self.discount_price,
        )

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
                    ["to_delete"][-len(context.user_data["new_product"].images
                                       )].message_id))

    # Method For Showing Product Template For Customer In Products List
    def send_customer_template(self, update, context):
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Buy", callback_data=f"buy/{self._id}")],
        ])
        context.user_data["to_delete"].append(
            context.bot.send_photo(   # TODO send album if  multiple images
                chat_id=update.effective_chat.id, photo=self.images[0],
                caption=self.template, parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup, timeout=10))

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

    def add_keyboard(self, order):
        # remove items that already exist in the order

        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text="TODO",
                                  callback_data="TODO")]
        ])

    def update(self, json=None):
        print(json)
        if json:
            products_table.update_one({"_id": self._id}, {"$set": json})
            product = products_table.find_one({"_id": self._id})
            self._id = product.get("_id")
            self.sold = product.get("sold")
            self.price = product.get("price")
            self.currency = product.get("currency")
            self.description = product.get("description")
            self.name = product.get("name")
            self.discount_price = product.get("discount_price")
            # self.sizes = product.get("sizes", list())
            self.order_ids = product.get("order_ids", list())
            self.images = product.get("images", list())
            self.in_trash = product.get("in_trash")
            self.category_id = product.get("category_id")
            self.shipping = product.get("shipping")
            self.online_payment = product.get("online_payment")
        else:
            products_table.update_one(
                {"_id": self._id},
                {"$set":
                     {"price": self.price,
                      "currency": self.currency,
                      "discount_price": self.discount_price,
                      "description": self.description,
                      "name": self.name,
                      "category_id": self.category_id,
                      "images": self.images,
                      "sold": self.sold,
                      "in_trash": self.in_trash,
                      "order_ids": self.order_ids,
                      "online_payment": self.online_payment,
                      "shipping": self.shipping
                      }
                 })

    # Only For cloth shop method - for refresh "sold" field after product edit
    def reset_sold_status(self):  # TODO modify
        products_table.update_one(
            {"_id": self._id},
            {"$set": {"sold": 0}})
        self.__init__(self._id)

    def create(self):
        products_table.insert_one({
            # "article": 1,
            "bot_id":self.context.bot.id,
            "price": self.price,
            "discount_price": 0,
            "description": self.description,
            "name": self.name,
            "category_id": self.category_id,
            "images": self.images,
            "shipping": self.shipping,
            "online_payment": self.online_payment,
            "sold": False,
            "in_trash": False,
            "on_sale": True,
            "order_ids": list(),
            "creation_timestamp": datetime.now()
        })
