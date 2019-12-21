from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from bson.objectid import ObjectId
from .product import Product
from database import orders_table
from helper_funcs.misc import get_obj
from helper_funcs.pagination import Pagination


class Order(object):
    def __init__(self, context,  obj: (ObjectId, dict, str) = None):
        """
        {"status": False,
         "creation_timestamp": "time.time:time",
         "last_modiffrom database import brands_table
y_timestamp": "time.time:time",
         "name": "yurec",
         "items": [{"size": "M",
                    "product": ObjectId('5df3f95621de961d524a1625'),
                    "product_exist": True}],
         "phone_number": "+111-222-333",
         "price": 2000,
         "in_trash": False,
         "comment": "Lil comment from user"}"""

        order = get_obj(orders_table, obj)
        self.context = context
        self._id = order.get("_id")
        self.status = order.get("status")
        self.timestamp = order.get("creation_timestamp", ".").split(".")[0]
        self.name = order.get("name")
        self.phone_number = order.get("phone_number")
        self.price = order.get("price")
        self.in_trash = order.get("in_trash")
        self.items_json = order.get("items")
        self.items = [OrderItem(order_item) for order_item in self.items_json]
        self.all_items_exists = not any(item.item_exist is False
                                        for item in self.items)

    @property
    def template(self):
        return (self.context.bot.lang_dict["shop_admin_order_status_new"]
                if self.status is False
                else self.context.bot.lang_dict["shop_admin_order_status_true"]) + "\n" + \
               self.context.bot.lang_dict["shop_admin_order_temp"].format(
                   self._id, self.timestamp,
                   self.str_status, self.name,
                   self.phone_number, self.price,
                   self.str_order_items)

    @property
    def str_status(self):
        return self.context.bot.lang_dict["shop_admin_order_status_true"] if self.status is True \
            else self.context.bot.lang_dict["shop_admin_some_product_not_exist"] \
            if not self.all_items_exists \
            else self.context.bot.lang_dict["shop_admin_empty_order"] if not len(self.items) \
            else self.context.bot.lang_dict["shop_admin_all_products_exist"]

    # todo refactor for long order items texts
    @property
    def str_order_items(self):
        return "\n".join(
            [f'(артикул: {item.article} )'
             + (item.item_emoji if not self.status else "")
             for item in self.items])

    @property
    def single_keyboard(self):
        kb = [[]]
        if self.in_trash:
            kb[0].append(InlineKeyboardButton(
                            text=self.context.bot.lang_dict["shop_admin_restore_btn"],
                            callback_data=f"restore/{self._id}"))
            return InlineKeyboardMarkup(kb)

        if self.status is False:
            if self.all_items_exists and len(self.items):
                kb[0].append(InlineKeyboardButton(
                                text=self.context.bot.lang_dict["shop_admin_to_done_btn"],
                                callback_data=f"to_done/{self._id}"))
            else:
                kb[0].append(InlineKeyboardButton(
                                text=self.context.bot.lang_dict["shop_admin_edit_btn"],
                                callback_data=f"edit/{self._id}"))

            kb[0].append(InlineKeyboardButton(
                            text=self.context.bot.lang_dict["shop_admin_to_trash_btn"],
                            callback_data=f"to_trash/{self._id}"))

        elif self.status is True:
            kb[0].append(InlineKeyboardButton(
                            text=self.context.bot.lang_dict["shop_admin_cancel_btn"],
                            callback_data=f"cancel_order/{self._id}"))
        return InlineKeyboardMarkup(kb)

    def send_short_template(self, update, context, kb=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template,
                reply_markup=kb if kb else self.single_keyboard,
                parse_mode=ParseMode.MARKDOWN))

    def send_full_template(self, update, context, text, kb, delete_kb=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template,
                parse_mode=ParseMode.MARKDOWN))

        # PAGINATION OF ORDER ITEMS
        # all_data = [item for item in self.items]
        pagination = Pagination(
            self.items_json, per_page=3,
            page=context.user_data["item_page"])
        for item in pagination.page_content():
            OrderItem(item).send_template(
                update, context, delete_kb=delete_kb)
        pagination.send_keyboard(update, context)
        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text, reply_markup=kb,
                                     parse_mode=ParseMode.MARKDOWN))

    def update(self, json=None):
        orders_table.update_one({"_id": self._id}, {"$set": json})
        self.__init__(self._id)

    """def remove_item(self, item_id):
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
            raise RequestException"""

    def refresh(self):
        self.__init__(self._id)


# Class For Showing Orders Items - Need to change for not cloth shop
class OrderItem(Product):
    def __init__(self, order_item):
        super(OrderItem, self).__init__(order_item["product"])
        self.item_obj = order_item

        self.item_exist = (True) # TODO

    def send_template(self, update, context, delete_kb=None):
        if delete_kb:
            delete_kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    context.bot.lang_dict["shop_admin_cancel_btn"],
                    callback_data=f"remove_item/{self.item_obj['id']}")]])

        text = context.bot.lang_dict["shop_admin_product_temp_for_order_item"].format(
            self.article,
            self.category["name"], self.price,
            f" {self.item_emoji}")
        self.send_admin_short_template(update, context, text, delete_kb)

    @property
    def item_emoji(self):
        return " 📛" if not self.item_exist else ""
