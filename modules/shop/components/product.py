from telegram import (ParseMode, InputMediaPhoto, InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.error import BadRequest
from bson.objectid import ObjectId
from datetime import datetime
from helper_funcs.misc import get_obj
from modules.shop.helper.helper import send_media_arr
from database import products_table, categories_table, chatbots_table


class Product(object):
    def __init__(self, context, obj: (ObjectId, dict, str) = None):
        self.context = context
        product = get_obj(products_table, obj)
        self._id = product.get("_id")
        self.bot_id = context.bot.id
        self.article = product.get("article")
        self.sold = product.get("sold")
        self.price = product.get("price")
        self.description = product.get("description", "")
        self.name = product.get("name")
        self.discount_price = product.get("discount_price")
        self.order_ids = product.get("order_ids", list())
        self.images = product.get("images", list())
        self.in_trash = product.get("in_trash")
        self.category_id = product.get("category_id")
        self.quantity = product.get("quantity")
        self.unlimited = product.get("unlimited")

    @property
    def category_id(self):
        return self._category_id

    @category_id.setter
    def category_id(self, _id):
        _id = ObjectId(_id) if type(_id) is str else _id
        self._category_id = _id
        # print(_id)
        # print(categories_table.find_one({"_id": ObjectId(_id)}))
        self.category = categories_table.find_one({"_id": _id})

    @property
    def template(self):
        shop = chatbots_table.find_one(
            {"bot_id": self.context.bot.id})["shop"]
        return self.context.bot.lang_dict[
            "shop_admin_product_template"].format(
                self.name,
                True if not self.sold else False,
                self.category["name"],
                self.price,
                shop["currency"])

    '''@property
    def short_customer_template(self):
        """Shows product for customers as the short version
        to display it in the products list"""

        shop = chatbots_table.find_one(
            {"bot_id": self.context.bot.id})["shop"]

        customer_template = ("*Article:* `{}`"
                             "\n*Name:* `{}`"
                             "\n*Category:* `{}`"
                             "\n*Description:* `{}`"
                             "\n*Price:* `{} {}`"
                             "\n*Quantity:* `{}`")

        if len(self.description) > 150:
            description = self.description[:150] + "..."
        else:
            description = self.description

        return customer_template.format(
            self.article,
            self.name,
            self.category["name"],
            description,
            self.price, shop["currency"],
            "Here must be quantity or None if quantity unlimited")'''

    @property
    def full_customer_template(self):
        """Shows product for customers as the full version
        to display it whenever user open it"""
        shop = chatbots_table.find_one(
            {"bot_id": self.context.bot.id})["shop"]

        customer_template = ("*Article:* `{}`"
                             "\n*Name:* `{}`"
                             "\n*Category:* `{}`"
                             "\n*Description:* `{}`"
                             "\n*Price:* `{} {}`"
                             "\n*Quantity:* `{}`")

        if len(self.description) > 500:
            description = self.context.bot.lang_dict[
                "shop_admin_description_below"]
        else:
            description = self.description

        return customer_template.format(
            self.article,
            self.name,
            self.category["name"],
            description,
            self.price, shop["currency"],
            "Here must be quantity or None if quantity unlimited")

    '''def send_customer_template(self, update, temp,
                               text="", reply_markup=None):  # TODO Content
        """Sends product as full version(temp="full")
        or short version(temp="short")"""

        if temp == "short":
            self.context.user_data["to_delete"].append(
                self.context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=self.images[0],
                    caption=self.short_customer_template + "\n\n" + text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup))
        else:
            full_media_group = [
                InputMediaPhoto(i, f'{self.name}') for i in self.images]
            send_media_arr(full_media_group, update, self.context)

            self.context.user_data["to_delete"].append(
                self.context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=self.full_customer_template + "\n\n" + text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup))

            if len(self.description) > 500:
                self.context.user_data["to_delete"].append(
                    self.context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=self.description))'''

    def full_template(self, long_description=None):
        description = self.context.bot.lang_dict["shop_admin_description_below"] \
            if long_description else self.description
        return self.context.bot.lang_dict["shop_admin_full_product_template"].format(
            True if not self.sold else False,
            self.name,
            self.category["name"],
            description,
            self.price,
            self.discount_price
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
        # TODO not only photo- every type of files
        if len(self.images) < 1:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id, text=text,
                    reply_markup=kb, parse_mode=ParseMode.MARKDOWN))
        elif len(self.images) < 2:
            context.user_data["to_delete"].append(
                context.bot.send_photo(
                    chat_id=update.effective_chat.id, photo=self.images[0],
                    caption=text, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb, mime_type="image"))
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
    """def send_customer_template(self, update, context):
        if self.offline_payment and self.online_payment:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Buy", callback_data=f"product_menu/{self._id}")],
            ])
        elif self.online_payment:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Buy", callback_data=f"online_buy/{self._id}")],
            ])
        else:
            reply_markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("Buy", callback_data=f"offline_buy/{self._id}")],
            ])
        if len(self.images) > 0:  # TODO double check and add the representation of the content
            context.user_data["to_delete"].append(
                context.bot.send_media_group(
                    chat_id=update.effective_chat.id, media=[InputMediaPhoto(x) for x in self.images]
                ))

        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            ))"""

    def send_admin_short_template(self, update, context, text=None, kb=None):
        text = text if text else self.template
        kb = self.admin_keyboard if kb is True else None if kb is None else kb
        try:
            context.user_data["to_delete"].append(
                context.bot.send_media_group(
                    chat_id=update.effective_chat.id, media=[InputMediaPhoto(x) for x in self.images]
                ))
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb
                     ))
        except (BadRequest, IndexError):
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_image_exception"] + "\n\n" + text,
                    parse_mode=ParseMode.MARKDOWN, reply_markup=kb))

    def send_full_template(self, update, context, text=None, kb=None):
        full_media_group = [InputMediaPhoto(
            i, f'{self.name}') for i in self.images]
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
            self.bot_id = product.get("bot_id")
            self.sold = product.get("sold")
            self.price = product.get("price")
            self.description = product.get("description")
            self.name = product.get("name")
            self.discount_price = product.get("discount_price")
            self.order_ids = product.get("order_ids", list())
            self.images = product.get("images", list())
            self.in_trash = product.get("in_trash")
            self.category_id = product.get("category_id")
            self.quantity = product.get("quantity"),
            self.unlimited = product.get("unlimited")

        else:
            products_table.update_one(
                {"_id": self._id},
                {"$set":
                     {"price": self.price,
                      "bot_id": self.bot_id,
                      "discount_price": self.discount_price,
                      "description": self.description,
                      "name": self.name,
                      "category_id": self.category_id,
                      "images": self.images,
                      "sold": self.sold,
                      "in_trash": self.in_trash,
                      "order_ids": self.order_ids,
                      "quantity": self.quantity,
                      "unlimited": self.unlimited
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
            "bot_id":self.context.bot.id,
            "price": self.price,
            "discount_price": 0,
            "description": self.description,
            "name": self.name,
            "category_id": self.category_id,
            "images": self.images,
            "sold": False,
            "in_trash": False,
            "on_sale": True,
            "order_ids": list(),
            "creation_timestamp": datetime.now(),
            "quantity": self.quantity,
            "unlimited": self.unlimited
        })
