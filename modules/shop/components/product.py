import logging
from datetime import datetime
from uuid import uuid4

from bson.objectid import ObjectId
from telegram.error import BadRequest
from telegram.constants import MAX_CAPTION_LENGTH
from telegram import (ParseMode, InputMediaPhoto, InlineKeyboardMarkup,
                      InlineKeyboardButton)

from helper_funcs.misc import get_obj
from modules.shop.helper.helper import send_media_arr
from database import products_table, categories_table


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


"""If product description length bigger than this integer
description will be sends as separate message

User side also use this constant at the templates"""
MAX_TEMP_DESCRIPTION_LENGTH = 150


class Product(object):
    def __init__(self, context, obj: (ObjectId, dict, str) = None):
        self.context = context
        product = get_obj(products_table, obj)
        # Change  _id attribute to id_
        self._id = product.get("_id")
        self.bot_id = context.bot.id
        self.article = product.get("article")
        self.sold = product.get("sold")
        self.price = product.get("price")
        self.description = product.get("description", "")
        self.name = product.get("name")
        self.discount_price = product.get("discount_price")
        self.order_ids = product.get("order_ids", list())
        self.content = product.get("content", list())
        self.in_trash = product.get("in_trash")
        self.category_id = product.get("category_id")
        self.quantity = product.get("quantity")
        self.unlimited = product.get("unlimited")

    @property
    def category_id(self):
        return self._category_id

    @category_id.setter
    def category_id(self, _id):
        if type(_id) is str:
            _id = ObjectId(_id)
        self._category_id = _id
        self.category = categories_table.find_one({"_id": _id})

    @property
    def id_(self):
        return self._id

    @property
    def files_str(self):
        return f"\n\n• Files {len(self.content)}/10"

    def send_short_template(self, update, context,
                            text=None, reply_markup=None):
        """Send short representation of the product.
        Must pass only short templates to this method

        Works for the both user and admin side.
        All templates, strings and keyboard must be passed as arguments"""
        try:
            if len(self.content):
                self.send_content(
                    update.effective_chat.id, context, self.content[0],
                    caption=text, reply_markup=reply_markup)
            else:
                context.user_data["to_delete"].append(
                    context.bot.send_message(chat_id=update.effective_chat.id,
                                             text=text,
                                             reply_markup=reply_markup,
                                             parse_mode=ParseMode.MARKDOWN))

        except (BadRequest, IndexError):
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=context.bot.lang_dict["shop_admin_image_exception"]
                    + "\n\n" + text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=reply_markup))

    def send_full_template(self, update, context,
                           text=None, reply_markup=None):
        """Send full representation of the product.
        Must pass only full templates to this method

        Works for the both user and admin side.
        All templates, strings and keyboard must be passed as arguments
        """
        reply_to_message_id = None

        if len(self.content) == 0:
            if len(self.description) > MAX_TEMP_DESCRIPTION_LENGTH:
                context.user_data["to_delete"].append(
                    context.bot.send_message(update.effective_chat.id,
                                             self.description))
                reply_to_message_id = (
                    context.user_data["to_delete"][-1].message_id)
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply_to_message_id))

        elif len(self.content) == 1:
            if len(self.description) > MAX_TEMP_DESCRIPTION_LENGTH:
                if len(self.description) > MAX_CAPTION_LENGTH:
                    self.send_content(update.effective_chat.id,
                                      context, self.content[0],
                                      caption=self.name)
                    reply_to_message_id = (
                        context.user_data["to_delete"][-1].message_id)
                    context.user_data["to_delete"].append(
                        context.bot.send_message(
                            update.effective_chat.id,
                            self.description,
                            reply_to_message_id=reply_to_message_id))
                    context.user_data["to_delete"].append(
                        context.bot.send_message(
                            update.effective_chat.id,
                            text=text,
                            reply_markup=reply_markup,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_to_message_id=reply_to_message_id))
                else:
                    self.send_content(update.effective_chat.id,
                                      context, self.content[0],
                                      caption=self.description)
                    reply_to_message_id = (
                        context.user_data["to_delete"][-1].message_id)
                    context.user_data["to_delete"].append(
                        context.bot.send_message(
                            update.effective_chat.id,
                            text=text,
                            reply_markup=reply_markup,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_to_message_id=reply_to_message_id))
            else:
                self.send_content(update.effective_chat.id,
                                  context, self.content[0],
                                  caption=text, reply_markup=reply_markup)
        else:
            if all(content_dict["type"] == "photo_file"
                   for content_dict in self.content):
                full_media_group = [
                    InputMediaPhoto(content_dict["file_id"])
                    for content_dict in self.content]
                send_media_arr(full_media_group, update, context)
            else:
                # First file - title file
                self.send_content(update.effective_chat.id,
                                  self.context, self.content[0])

                images = list()
                other_types = list()
                for content_dict in self.content[1:]:
                    if content_dict["type"] == "photo_file":
                        images.append(content_dict)
                    else:
                        other_types.append(content_dict)

                # Then goes all images
                if len(images) >= 2:
                    full_media_group = [
                        InputMediaPhoto(content_dict["file_id"])
                        for content_dict in images]
                    send_media_arr(full_media_group, update, context)
                elif len(images) == 1:
                    other_types.insert(0, images[0])

                # And then goes all other types of content
                for content_dict in other_types:
                    self.send_content(update.effective_chat.id,
                                      self.context, content_dict)

            reply_to_message_id = (
                context.user_data["to_delete"][-len(self.content)].message_id)

            if len(self.description) > MAX_TEMP_DESCRIPTION_LENGTH:
                context.user_data["to_delete"].append(
                    context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=self.description,
                        reply_to_message_id=reply_to_message_id))
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply_to_message_id))

    def add_content_dict(self, update, to_save=False):
        """video_note_file and sticker_file - don't have captions

         "id" field coz of -
        https://github.com/python-telegram-bot/python-telegram-bot/issues/1267
        """
        content_dict = {}
        if update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            content_dict = {"file_id": photo_file,
                            "type": "photo_file",
                            "id": str(uuid4())}

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            content_dict = {"file_id": audio_file,
                            "type": "audio_file",
                            "name": update.message.audio.title,
                            "id": str(uuid4())}

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            content_dict = {"file_id": voice_file,
                            "type": "voice_file",
                            "id": str(uuid4())}

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            content_dict = {"file_id": document_file,
                            "type": "document_file",
                            "name": update.message.document.file_name,
                            "id": str(uuid4())}

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            content_dict = {"file_id": video_file,
                            "type": "video_file",
                            "id": str(uuid4())}

        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            content_dict = {"file_id": animation_file,
                            "type": "animation_file",
                            "id": str(uuid4())}
        if content_dict:
            self.content.append(content_dict)
            if to_save:
                products_table.find_and_modify(
                    {"_id": self._id}, {"$push": {"content": content_dict}})
                self.refresh()
        return content_dict

    @staticmethod
    def send_content(chat_id, context, content_dict,
                     caption=None, parse_mode=ParseMode.MARKDOWN,
                     reply_markup=None):
        """video_note_file and sticker_file - don't have captions"""

        if content_dict["type"] == "audio_file":
            context.user_data["to_delete"].append(
                context.bot.send_audio(chat_id,
                                       content_dict["file_id"],
                                       caption=caption,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup))

        if content_dict["type"] == "voice_file":
            context.user_data["to_delete"].append(
                context.bot.send_voice(chat_id,
                                       content_dict["file_id"],
                                       caption=caption,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup))

        if content_dict["type"] == "video_file":
            context.user_data["to_delete"].append(
                context.bot.send_video(chat_id,
                                       content_dict["file_id"],
                                       caption=caption,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup))

        if content_dict["type"] == "document_file":
            if (".png" in content_dict["file_id"] or
                    ".jpg" in content_dict["file_id"]):
                context.user_data["to_delete"].append(
                    context.bot.send_photo(chat_id,
                                           content_dict["file_id"],
                                           caption=caption,
                                           parse_mode=parse_mode,
                                           reply_markup=reply_markup))
            else:
                context.user_data["to_delete"].append(
                    context.bot.send_document(chat_id,
                                              content_dict["file_id"],
                                              caption=caption,
                                              parse_mode=parse_mode,
                                              reply_markup=reply_markup))

        if content_dict["type"] == "photo_file":
            context.user_data["to_delete"].append(
                context.bot.send_photo(chat_id,
                                       content_dict["file_id"],
                                       caption=caption,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup,
                                       # mime_type="image"
                                       ))

        if content_dict["type"] == "animation_file":
            context.user_data["to_delete"].append(
                context.bot.send_animation(chat_id,
                                           content_dict["file_id"],
                                           caption=caption,
                                           parse_mode=parse_mode,
                                           reply_markup=reply_markup))

    def add_keyboard(self, order):
        # remove items that already exist in the order
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text="TODO",
                                  callback_data="TODO")]
        ])

    def update(self, json=None):
        if json:
            products_table.update_one({"_id": self._id}, {"$set": json})
            # product = products_table.find_one({"_id": self._id})
            # self._id = product.get("_id")
            # self.bot_id = product.get("bot_id")
            # self.sold = product.get("sold")
            # self.price = product.get("price")
            # self.description = product.get("description")
            # self.name = product.get("name")
            # self.discount_price = product.get("discount_price")
            # self.order_ids = product.get("order_ids", list())
            # self.content = product.get("content", list())
            # self.in_trash = product.get("in_trash")
            # self.category_id = product.get("category_id")
            # self.quantity = product.get("quantity"),
            # self.unlimited = product.get("unlimited")
        else:
            products_table.update_one(
                {"_id": self._id},
                {"$set": {"price": self.price,
                          "bot_id": self.bot_id,
                          "discount_price": self.discount_price,
                          "description": self.description,
                          "name": self.name,
                          "category_id": self.category_id,
                          "content": self.content,
                          "sold": self.sold,
                          "in_trash": self.in_trash,
                          "order_ids": self.order_ids,
                          "quantity": self.quantity,
                          "unlimited": self.unlimited}
                 })
        self.refresh()

    def refresh(self, obj=None):
        if not obj:
            product = get_obj(products_table, self._id)
        else:
            product = get_obj(products_table, obj)

        self._id = product.get("_id")
        self.article = product.get("article")
        self.sold = product.get("sold")
        self.price = product.get("price")
        self.description = product.get("description", "")
        self.name = product.get("name")
        self.discount_price = product.get("discount_price")
        self.order_ids = product.get("order_ids", list())
        self.content = product.get("content", list())
        self.in_trash = product.get("in_trash")
        self.category_id = product.get("category_id")
        self.quantity = product.get("quantity")
        self.unlimited = product.get("unlimited")

    def to_dict(self):
        return {
            "_id": self._id,
            "bot_id": self.bot_id,
            "article": self.article,
            "sold": self.sold,
            "price": self.price,
            "description": self.description,
            "name": self.name,
            "discount_price": self.discount_price,
            "order_ids": self.order_ids,
            "content": self.content,
            "in_trash": self.in_trash,
            "category_id": self.category_id,
            "quantity": self.quantity,
            "unlimited": self.unlimited,
        }

    # Only For cloth shop method - for refresh "sold" field after product edit
    # def reset_sold_status(self):  # TODO modify
    #     products_table.update_one(
    #         {"_id": self._id},
    #         {"$set": {"sold": 0}})
    #     self.__init__(self._id)

    def create(self):
        products_table.insert_one({
            "bot_id": self.context.bot.id,
            "price": self.price,
            "discount_price": 0,
            "description": self.description,
            "name": self.name,
            "category_id": self.category_id,
            "content": self.content,
            "sold": False,
            "in_trash": False,
            "on_sale": True,
            "order_ids": list(),
            "creation_timestamp": datetime.now(),
            "quantity": self.quantity,
            "unlimited": self.unlimited
        })


# TODO put special logic here
class UserProduct(Product):
    pass


class AdminProduct(Product):
    pass


class CartProduct(Product):
    pass
