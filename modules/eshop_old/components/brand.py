from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from modules.shop.helper.strings import strings
from config import conf
import requests
from requests.exceptions import RequestException
from telegram.error import BadRequest


class Brand(object):
    def __init__(self, brand: (int, dict)):
        if type(brand) is int:
            resp = requests.get(f"{conf['API_URL']}/brand/{brand}")
            if resp.status_code == 200:
                brand = resp.json()
            else:
                raise RequestException

        self._id = brand["id"]
        self.name = brand["name"]
        self.price = brand["price"]
        self.logo_url = brand["logo_url"]

    @property
    def template(self):
        return strings["brand_template"].format(self.name, self.price)

    @property
    def single_keyboard(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(strings["edit_btn"],
             callback_data=f"edit_brand/{self._id}")]
        ])

    def send_template(self, update, context, text="", kb=None):
        kb = self.single_keyboard if not kb else kb
        try:
            context.user_data["to_delete"].append(
                context.bot.send_photo(update.effective_chat.id,
                                       self.logo_url,
                                       f"{self.template}"
                                       f"\n{text}",
                                       parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=kb))
        except BadRequest:
            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         f"{strings['image_brand_exception']}"
                                         f"\n\n{self.template}"
                                         f"\n{text}",
                                         parse_mode=ParseMode.MARKDOWN,
                                         reply_markup=kb))

    def edit(self, json):
        resp = requests.post(f"{conf['API_URL']}/brand/{self._id}",
                             json=json)
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException
