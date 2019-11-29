from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from modules.shop.helper.strings import strings
from config import conf
from modules.shop.helper.pagination import Pagination
import requests
from requests.exceptions import RequestException
from .product import Product


class Order(object):
    def __init__(self, order: (int, dict)):
        if type(order) is int:
            resp = requests.get(f"{conf['API_URL']}/order/{order}")
            if resp.status_code == 200:
                order = resp.json()
            else:
                raise RequestException

        self._id = order["id"]
        self.items = order["items"]
        self.status = order["status"]
        self.timestamp = order["creation_timestamp"].split(".")[0]
        self.name = order["name"]
        self.phone_number = order["phone_number"]
        self.price = order["price"]
        self.in_trash = order["in_trash"]
        self.all_items_exists = not any(item["product_exist"] is False
                                        for item in self.items)

    @property
    def template(self):
        return (strings["order_status_new"]
                if self.status is False
                else strings["order_status_true"]) + "\n" + \
               strings["order_temp"].format(
                   self._id, self.timestamp,
                   self.str_status, self.name,
                   self.phone_number, self.price,
                   self.str_order_items)

    @property
    def str_status(self):
        return strings["order_status_true"] if self.status is True \
            else strings["some_product_not_exist"] \
            if not self.all_items_exists \
            else strings["empty_order"] if not len(self.items) \
            else strings["all_products_exist"]

    # todo refactor for long texts
    @property
    def str_order_items(self):
        return "\n".join(
            [f'(артикул: {item["product"]["article"]} '
             f' размер: {item["size"]})'
             + (self.order_item_emoji(item) if not self.status else "")
             for item in self.items])

    @property
    def single_keyboard(self):
        kb = [[]]
        if self.in_trash:
            kb[0].append(InlineKeyboardButton(
                            strings["restore_btn"],
                            callback_data=f"restore/{self._id}"))
            return InlineKeyboardMarkup(kb)

        if self.status is False:
            if self.all_items_exists and len(self.items):
                kb[0].append(InlineKeyboardButton(
                                strings["to_done_btn"],
                                callback_data=f"to_done/{self._id}"))
            else:
                kb[0].append(InlineKeyboardButton(
                                strings["edit_btn"],
                                callback_data=f"edit/{self._id}"))

            kb[0].append(InlineKeyboardButton(
                            strings["to_trash_btn"],
                            callback_data=f"to_trash/{self._id}"))

        elif self.status is True:
            kb[0].append(InlineKeyboardButton(
                            strings["cancel_btn"],
                            callback_data=f"cancel_order/{self._id}"))
        return InlineKeyboardMarkup(kb)

    @staticmethod
    def order_item_emoji(item):
        return " 📛" if not item["product_exist"] else ""

    def send_short_template(self, update, context, kb=None):
        context.context.user_data["to_delete"].append(
            context.context.bot.send_message(update.effective_chat.id,
                                     self.template,
                                     reply_markup=kb if kb
                                     else self.single_keyboard,
                                     parse_mode=ParseMode.MARKDOWN))

    def send_full_template(self, update, context, text, kb, delete_kb=None):
        context.context.user_data["to_delete"].append(
            context.context.bot.send_message(update.effective_chat.id,
                                     self.template,
                                     parse_mode=ParseMode.MARKDOWN))

        # PAGINATION OF ORDER ITEMS
        # all_data = [item for item in self.items]
        pagination = Pagination(context.context.user_data["item_page"], 3, self.items)
        for item in pagination.page_content():
            OrderProductItem(item).send_template(update, context,
                                                 delete_kb=delete_kb)
        pagination.send_pagin(update, context)
        context.context.user_data["to_delete"].append(
            context.context.bot.send_message(update.effective_chat.id,
                                     text, reply_markup=kb,
                                     parse_mode=ParseMode.MARKDOWN))

    def remove_item(self, item_id):
        resp = requests.post(
            f"{conf['API_URL']}/order/{self._id}/edit_items",
            json={"id_to_remove": int(item_id)})
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException

    def add_item(self, item: dict):
        resp = requests.post(
            f"{conf['API_URL']}/order/{self._id}/edit_items",
            json={"to_add": [item]})
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException

    def change_status(self, json):
        resp = requests.patch(
            f"{conf['API_URL']}/order/{self._id}",
            json=json)
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException

    def refresh(self):
        self.__init__(self._id)


class OrderProductItem(Product):
    def __init__(self, order_item):
        super(OrderProductItem, self).__init__(order_item["product"])
        self.item_obj = order_item

    def send_template(self, update, context, delete_kb=None):
        if delete_kb:
            delete_kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    strings["cancel_btn"],
                    callback_data=f"remove_item/{self.item_obj['id']}")]])

        text = strings["product_temp_for_order_item"].format(
            self.article, self.sizes_text, self.brand,
            self.category, self.price,
            self.item_obj["size"] +
            f" {Order.order_item_emoji(self.item_obj)}")
        self.send_short_template(update, context, text, delete_kb)
