import requests
from requests.exceptions import RequestException
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.error import BadRequest
from bson.objectid import ObjectId

from modules.shop.helper.strings import strings
from config import conf
from helper_funcs.misc import get_obj
from database import brands_table
from modules.shop.helper.keyboards import create_keyboard, back_btn


class Brand(object):
    def __init__(self, context, obj: (ObjectId, dict, str) = None):
        brand = get_obj(brands_table, obj)
        self._id = brand.get("_id")
        self.name = brand.get("name")
        self.price = brand.get("price")
        self.logo_file_id = brand.get("logo_file_id")
        self.context = context

    def __repr__(self):
        return (f"_id: {self._id}"
                f"name: {self.name}"
                f"price: {self.price}"
                f"logo_file_id: {self.logo_file_id}")

    @property
    def template(self):
        return self.context.bot.lang_dict["shop_admin_brand_template"].format(self.name, self.price)

    @property
    def single_keyboard(self):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text=self.context.bot.lang_dict["shop_admin_edit_btn"],
                                  callback_data=f"edit_brand/{self._id}")]
        ])

    def send_template(self, update, context, text="", kb=None):
        kb = self.single_keyboard if not kb else kb
        try:
            context.user_data["to_delete"].append(
                context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=self.logo_file_id,
                    caption=f"{self.template}\n{text}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb))
        except BadRequest:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"{strings['image_brand_exception']}"
                         f"\n\n{self.template}\n{text}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=kb))

    def edit(self, json):
        resp = requests.post(f"{conf['API_URL']}/brand/{self._id}",
                             json=json)
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException

