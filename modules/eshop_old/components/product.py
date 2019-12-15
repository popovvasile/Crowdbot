from telegram import (ParseMode, InputMediaPhoto, InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.error import BadRequest
from helper_funcs.misc import get_obj
from database import products_table
from bson.objectid import ObjectId



class Product(object):
    def __init__(self, obj: (ObjectId, dict, str)):
        # self.context = context
        product_obj = get_obj(products_table, obj)

        self._id = product_obj.get("_id")
        self.title = product_obj["title"]
        self.price = product_obj["price"]
        self.currency = product_obj["currency"]
        self.shipping = product_obj["shipping"]
        self.content = product_obj["content"]
        self.title_lower = product_obj["title_lower"]
        self.admin_id = product_obj["admin_id"]
        self.bot_id = product_obj["bot_id"]
        self.link_button = product_obj["link_button"]

    @property
    def template(self):
        return

    def full_template(self):
        return

    def reply_markup(self):
        return

    """"@property
    def template(self):
        return context.bot.lang_dict["shop_admin_product_template"].format(
            self.article, True if not self.sold else False,
            self.brand, self.category, self.price,
            self.sizes_text)

    def full_template(self, long_description=None):
        description = context.bot.lang_dict["shop_admin_description_below"] \
            if long_description else self.description
        return context.bot.lang_dict["shop_admin_full_product_template"].format(
            self.article, True if not self.sold else False,
            self.name, self.brand, self.category,
            description, self.price, self.discount_price,
            self.sizes_text)

    @property
    def sizes_text(self):
        return "\n".join([f"{i['size']} - {i['quantity']}"
                          for i in self.sizes]) \
            if self.sizes else "💢 *Товар Продан*"

    @property
    def single_keyboard(self):
        kb = [[]]
        if self.in_trash:
            kb[0].append(InlineKeyboardButton(
                            context.bot.lang_dict["shop_admin_restore_btn"],
                            callback_data=f"restore_product/{self.article}"))
            return InlineKeyboardMarkup(kb)
        kb[0].append(InlineKeyboardButton(
                        context.bot.lang_dict["shop_admin_edit_btn"],
                        callback_data=f"edit_product/{self.article}"))
        if not self.order_ids:
            kb[0].append(InlineKeyboardButton(
                            context.bot.lang_dict["shop_admin_to_trash_btn"],
                            callback_data=f"to_trash/{self.article}"))

        return InlineKeyboardMarkup(kb)

    @staticmethod
    def send_adding_product_template(update, context, text, kb=None):
        if len(context.user_data["product_images"]) < 2:
            context.user_data["to_delete"].append(
                context.bot.send_photo(
                    update.effective_chat.id,
                    context.user_data["product_images"][0].file_id,
                    text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb))
        else:
            # todo mb don't delete media group until product adding finish
            context.user_data["to_delete"].extend([
                i for i in context.bot.send_media_group(
                    update.effective_chat.id,
                    [InputMediaPhoto(i)
                     for i in context.user_data["product_images"]])
            ])

            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id, text,
                    reply_markup=kb,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=context.user_data
                    ["to_delete"][-len(context.user_data["product_images"]
                                       )].message_id))

    def send_short_template(self, update, context, text=None, kb=None):
        text = text if text else self.template
        kb = self.single_keyboard if kb is True \
            else None if kb is None else kb
        try:
            context.user_data["to_delete"].append(
                context.bot.send_photo(
                    update.effective_chat.id,
                    self.images[0]["telegram_id"]
                    if self.images[0]["telegram_id"]
                    else self.images[0]["url"],
                    text, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb, timeout=10))
        except (BadRequest, IndexError):
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    context.bot.lang_dict["shop_admin_image_exception"] +
                    "\n\n" + text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb))

    def send_full_template(self, update, context, text=None, kb=None):
        full_media_group = [InputMediaPhoto(
            i["telegram_id"] if i["telegram_id"] else i["url"],
            f'{self.article} - {self.name}')
            for i in self.images]
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
                    update.effective_chat.id,
                    context.bot.lang_dict["shop_admin_product_size_temp"].format(
                        item["size"], item["quantity"]),
                    reply_markup=kb,
                    parse_mode=ParseMode.MARKDOWN))
        kb = [[]]
        if len(self.sizes) < len(sizes_list):
            kb[0].append(InlineKeyboardButton(context.bot.lang_dict["shop_admin_add_size_btn"],
                                              callback_data="add_size"))
        kb[0].append(back_btn("back_to_edit", context))
        context.user_data["to_delete"].append(
            context.bot.send_message(update.effective_chat.id,
                                     "Nice bro 😎",
                                     reply_markup=InlineKeyboardMarkup(kb)))

    def add_keyboard(self, order):
        # remove items that already exist in the order
        sizes = [size for size in self.sizes
                 if not any(order_item["size"] == size["size"]
                            and order_item["product"]["article"] == self.article
                            for order_item in order.items)]
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(item["size"],
                                  callback_data=f"finish_add_to_order/"
                                                f"{self.article}/"
                                                f"{item['size']}")
             for item in sizes]
        ])

    def edit(self, json):
        resp = requests.patch(
            f"{conf['API_URL']}/product/{self.article}", json=json)
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException"""