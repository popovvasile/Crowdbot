from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from modules.shop.helper.strings import strings
from config import conf
import requests
from requests.exceptions import RequestException


class WholesaleOrder(object):
    def __init__(self, wholesale_order):
        if type(wholesale_order) is int:
            resp = requests.get(
                f"{conf['API_URL']}/wholesale_order/{wholesale_order}")
            if resp.status_code == 200:
                wholesale_order = resp.json()
            else:
                raise RequestException

        self._id = wholesale_order["id"]
        self.status = wholesale_order["status"]
        self.timestamp = wholesale_order["creation_timestamp"].split(".")[0]
        self.name = wholesale_order["name"]
        self.phone_number = wholesale_order["phone_number"]
        self.price = wholesale_order["price"]
        self.items = wholesale_order["items"]
        self.in_trash = wholesale_order["in_trash"]
        self.categories = wholesale_order["categories"]
        self.comment = wholesale_order["comment"]

    @property
    def template(self):
        text = (strings["order_status_new"]
                if self.status is False
                else strings["order_status_true"]) + "\n" + \
            strings["wholesale_order_temp"].format(
                self._id, self.timestamp, self.name, self.phone_number,
                self.price, "\n".join([c["name"] for c in self.categories]),
                [(i["brand"]["name"],
                  i["weight"], i["price"]) for i in self.items])
        if self.comment:
            text += f"\n\n*Комментарий:* `{self.comment}`"
        return text

    @property
    def single_keyboard(self):
        kb = [[]]
        if self.in_trash is True:
            kb[0].append(InlineKeyboardButton(
                            strings["restore_btn"],
                            callback_data=f"restore_wholesale/{self._id}"))
            return InlineKeyboardMarkup(kb)
        if self.status is False:
            kb[0].append(InlineKeyboardButton(
                            strings["to_done_btn"],
                            callback_data=f"to_done/{self._id}"))
            kb[0].append(InlineKeyboardButton(
                            strings["to_trash_btn"],
                            callback_data=f"to_trash/{self._id}"))

        elif self.status is True:
            kb[0].append(InlineKeyboardButton(
                            strings["cancel_btn"],
                            callback_data=f"cancel_order/{self._id}"))
        return InlineKeyboardMarkup(kb)

    def send_template(self, update, context, kb=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(update.effective_chat.id,
                                     self.template,
                                     parse_mode=ParseMode.MARKDOWN,
                                     reply_markup=kb or self.single_keyboard))

    def change_status(self, json):
        resp = requests.patch(f"{conf['API_URL']}/wholesale_order/"
                              f"{self._id}", json=json)
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException
