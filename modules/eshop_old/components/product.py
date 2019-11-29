from telegram import ParseMode, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton
from modules.shop.helper.strings import strings, emoji
from modules.shop.helper.keyboards import back_btn, sizes_list

from config import conf
import requests
from telegram.error import BadRequest
from modules.shop.helper.helper import send_media_arr
from requests.exceptions import RequestException


class Product(object):
    def __init__(self, product: (int, dict)):
        if type(product) is int:
            resp = requests.get(f"{conf['API_URL']}/product/{product}")
            if resp.status_code == 200:
                product = resp.json()
            else:
                raise RequestException

        self.article = product["article"]
        self.sold = product["sold"]
        self.brand = product["brand"]
        self.category = product["category"]
        self.price = product["price"]
        self.description = product["description"]
        self.name = product["name"]
        self.discount_price = product["discount_price"]
        self.sizes = product["sizes"]
        self.order_ids = product["order_ids"]
        self.images = product["images"]
        self.in_trash = product["in_trash"]

    @property
    def template(self):
        return strings["product_template"].format(
            self.article, True if not self.sold else False,
            self.brand, self.category, self.price,
            self.sizes_text)

    def full_template(self, long_description=None):
        description = strings["description_below"] \
            if long_description else self.description
        return strings["full_product_template"].format(
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
                            strings["restore_btn"],
                            callback_data=f"restore_product/{self.article}"))
            return InlineKeyboardMarkup(kb)
        kb[0].append(InlineKeyboardButton(
                        strings["edit_btn"],
                        callback_data=f"edit_product/{self.article}"))
        if not self.order_ids:
            kb[0].append(InlineKeyboardButton(
                            strings["to_trash_btn"],
                            callback_data=f"to_trash/{self.article}"))

        return InlineKeyboardMarkup(kb)

    @staticmethod
    def send_adding_product_template(update, context, text, kb=None):
        if len(context.context.user_data["product_images"]) < 2:
            context.context.user_data["to_delete"].append(
                context.context.bot.send_photo(
                    update.effective_chat.id,
                    context.context.user_data["product_images"][0].file_id,
                    text, parse_mode=ParseMode.MARKDOWN, reply_markup=kb))
        else:
            # todo mb don't delete media group until product adding finish
            context.context.user_data["to_delete"].extend([
                i for i in context.context.bot.send_media_group(
                    update.effective_chat.id,
                    [InputMediaPhoto(i)
                     for i in context.context.user_data["product_images"]])
            ])

            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(
                    update.effective_chat.id, text,
                    reply_markup=kb,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=context.context.user_data
                    ["to_delete"][-len(context.context.user_data["product_images"]
                                       )].message_id))

    def send_short_template(self, update, context, text=None, kb=None):
        text = text if text else self.template
        kb = self.single_keyboard if kb is True \
            else None if kb is None else kb
        try:
            context.context.user_data["to_delete"].append(
                context.context.bot.send_photo(
                    update.effective_chat.id,
                    self.images[0]["telegram_id"]
                    if self.images[0]["telegram_id"]
                    else self.images[0]["url"],
                    text, parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb, timeout=10))
        except (BadRequest, IndexError):
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(
                    update.effective_chat.id,
                    strings["image_exception"] +
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
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(update.effective_chat.id,
                                         self.full_template(
                                             long_description=True),
                                         parse_mode=ParseMode.MARKDOWN))
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(update.effective_chat.id,
                                         self.description))
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(update.effective_chat.id,
                                         text, reply_markup=kb,
                                         parse_mode=ParseMode.MARKDOWN))
        else:
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(update.effective_chat.id,
                                         f"{self.full_template()}"
                                         f"\n{text}",
                                         reply_markup=kb,
                                         parse_mode=ParseMode.MARKDOWN))

    def send_sizes_menu(self, update, context):
        self.send_full_template(update, context, strings["sizes_menu_title"])
        for item in self.sizes:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(emoji["x"],
                                      callback_data=f"remove_size/"
                                                    f"{item['size']}"),
                 InlineKeyboardButton(strings["edit_btn"],
                                      callback_data=f"change_size_quantity/"
                                                    f"{item['size']}")]
            ])
            context.context.user_data["to_delete"].append(
                context.context.bot.send_message(
                    update.effective_chat.id,
                    strings["product_size_temp"].format(
                        item["size"], item["quantity"]),
                    reply_markup=kb,
                    parse_mode=ParseMode.MARKDOWN))
        kb = [[]]
        if len(self.sizes) < len(sizes_list):
            kb[0].append(InlineKeyboardButton(strings["add_size_btn"],
                                              callback_data="add_size"))
        kb[0].append(back_btn("back_to_edit"))
        context.context.user_data["to_delete"].append(
            context.context.bot.send_message(update.effective_chat.id,
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
            raise RequestException
