from datetime import datetime

from bson.objectid import ObjectId
from telegram.error import BadRequest
from telegram.constants import MAX_CAPTION_LENGTH
from telegram import (ParseMode, InputMediaPhoto, InlineKeyboardMarkup,
                      InlineKeyboardButton)

from helper_funcs.misc import get_obj
from modules.shop.helper.helper import send_media_arr
from database import products_table, categories_table, chatbots_table

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
        # self.images = product.get("images", list())
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
    def admin_short_template(self):
        """Admin short text representation of the product"""
        shop = chatbots_table.find_one(
            {"bot_id": self.context.bot.id})["shop"]
        if self.unlimited is True:
            quantity = "Unlimited"
        else:
            quantity = self.quantity
        return self.context.bot.lang_dict[
            "shop_admin_product_template"].format(
                self.name,
                True if not self.sold else False,
                self.category["name"],
                self.price,
                shop["currency"],
                self.discount_price,
                shop["currency"],
                quantity)

    @property
    def admin_full_template(self):
        """Admin full text representation of the product"""
        shop = chatbots_table.find_one(
            {"bot_id": self.context.bot.id})["shop"]
        if self.unlimited is True:
            quantity = "Unlimited"
        else:
            quantity = self.quantity
        # If description is long send_full_template method
        # will send description as separate message
        if len(self.description) > MAX_TEMP_DESCRIPTION_LENGTH:
            description = self.context.bot.lang_dict[
                "shop_admin_description_above"]
        else:
            description = self.description

        return self.context.bot.lang_dict[
            "shop_admin_full_product_template"].format(
                True if not self.sold else False,
                self.name,
                self.category["name"],
                self.price,
                shop["currency"],
                self.discount_price,
                shop["currency"],
                quantity,
                description)

    '''# Method For Sending Product Template While Adding New Product
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
                                       )].message_id))'''

    # def send_adding_product_template(self, update, context, text,
    #                                  reply_markup=None):
    #     """Method For Sending Product Template While Adding New Product"""
        # todo mb don't delete media group until product adding finish

        # chat_id = update.effective_chat.id
        #
        # if len(self.content) == 0:
        #     context.user_data["to_delete"].append(
        #         context.bot.send_message(
        #             chat_id=chat_id,
        #             text=text,
        #             reply_markup=reply_markup,
        #             parse_mode=ParseMode.MARKDOWN))
        #
        # elif len(self.content) == 1:
        #     send_content(chat_id, context, self.content[0],
        #                  caption=text, reply_markup=reply_markup)
        # else:
        #     images = list()
        #     other_types = list()
        #     for content_dict in self.content[1:]:
        #         if "photo_file" in content_dict:
        #             images.append(content_dict)
        #         else:
        #             other_types.append(content_dict)
        #
            # First file - title file
            # send_content(chat_id, self.context, self.content[0])
            #
            # Then goes all images
            # if len(images) >= 2:
            #     full_media_group = [
            #         InputMediaPhoto(content_dict["photo_file"])
            #         for content_dict in images]
            #     send_media_arr(full_media_group, update, context)
            # elif len(images) == 1:
            #     other_types.insert(0, images[0])
            #
            # And then goes all other types of content
            # for content_dict in other_types:
            #     send_content(chat_id, self.context, content_dict)
            #
            # context.user_data["to_delete"].append(
            #     context.bot.send_message(
            #         chat_id=chat_id,
            #         text=text,
            #         reply_markup=reply_markup,
            #         parse_mode=ParseMode.MARKDOWN,
            #         reply_to_message_id=context.user_data["to_delete"][
            #             -len(self.content)].message_id))

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

    '''def send_admin_full_template(self, update, context,
                                 text=None, reply_markup=None):
        if len(self.content) == 0:
            pass
        elif len(self.content) == 1:
            send_content(update.effective_chat.id,
                         context, self.content[0],
                         caption=self.name)
        else:
            images = list()
            other_types = list()
            for content_dict in self.content[1:]:
                if "photo_file" in content_dict:
                    images.append(content_dict)
                else:
                    other_types.append(content_dict)

            # First file - title file
            send_content(update.effective_chat.id,
                         self.context, self.content[0])

            # Then goes all images
            if len(images) >= 2:
                full_media_group = [
                    InputMediaPhoto(content_dict["photo_file"])
                    for content_dict in images]
                send_media_arr(full_media_group, update, context)
            elif len(images) == 1:
                other_types.insert(0, images[0])

            # And then goes all other types of content
            for content_dict in other_types:
                send_content(update.effective_chat.id,
                             self.context, content_dict)
        if len(self.content):
            reply_to_message_id = context.user_data["to_delete"][
                -len(self.content)].message_id
        else:
            reply_to_message_id = None

        if len(self.description) > 250:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    self.admin_full_template(long_description=True),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply_to_message_id))

            if reply_to_message_id:
                reply_to_message_id = context.user_data["to_delete"][
                    -(1 + len(self.content))].message_id

            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    self.description,
                    reply_to_message_id=reply_to_message_id))

            context.user_data["to_delete"].append(
                context.bot.send_message(update.effective_chat.id,
                                         text, reply_markup=reply_markup,
                                         parse_mode=ParseMode.MARKDOWN))
        else:
            context.user_data["to_delete"].append(
                context.bot.send_message(
                    update.effective_chat.id,
                    self.admin_full_template() + "\n" + text,
                    reply_markup=reply_markup,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_to_message_id=reply_to_message_id))'''

    def send_full_template(self, update, context,
                           text=None, reply_markup=None):
        """Send full representation of the product.
        Must pass only full templates to this method

        Works for the both user and admin side.
        All templates, strings and keyboard must be passed as arguments"""

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
            if all("photo_file" in content_dict
                   for content_dict in self.content):
                full_media_group = [
                    InputMediaPhoto(content_dict["photo_file"])
                    for content_dict in self.content]
                send_media_arr(full_media_group, update, context)
            else:
                # First file - title file
                self.send_content(update.effective_chat.id,
                                  self.context, self.content[0])

                images = list()
                other_types = list()
                for content_dict in self.content[1:]:
                    if "photo_file" in content_dict:
                        images.append(content_dict)
                    else:
                        other_types.append(content_dict)

                # Then goes all images
                if len(images) >= 2:
                    full_media_group = [
                        InputMediaPhoto(content_dict["photo_file"])
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

    @staticmethod
    def send_content(chat_id, context, content_dict,
                     caption=None, parse_mode=ParseMode.MARKDOWN,
                     reply_markup=None):
        if "audio_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_audio(chat_id,
                                       content_dict["audio_file"],
                                       caption=caption,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup))
        if "voice_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_voice(chat_id,
                                       content_dict["voice_file"],
                                       caption=caption,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup))
        if "video_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_video(chat_id,
                                       content_dict["video_file"],
                                       caption=caption,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup))
        if "document_file" in content_dict:
            if (".png" in content_dict["document_file"] or
                    ".jpg" in content_dict["document_file"]):
                context.user_data["to_delete"].append(
                    context.bot.send_photo(chat_id,
                                           content_dict["document_file"],
                                           caption=caption,
                                           parse_mode=parse_mode,
                                           reply_markup=reply_markup))
            else:
                context.user_data["to_delete"].append(
                    context.bot.send_document(chat_id,
                                              content_dict["document_file"],
                                              caption=caption,
                                              parse_mode=parse_mode,
                                              reply_markup=reply_markup))

        if "photo_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_photo(chat_id,
                                       content_dict["photo_file"],
                                       caption=caption,
                                       parse_mode=parse_mode,
                                       reply_markup=reply_markup))

        if "animation_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_animation(chat_id,
                                           content_dict["animation_file"],
                                           caption=caption,
                                           parse_mode=parse_mode,
                                           reply_markup=reply_markup))

        # TODO video_note_file and sticker_file - don't have captions
        # if "video_note_file" in self.content[0]:
        #     context.user_data["to_delete"].append(
        #         context.bot.send_video_note(chat_id,
        #                                     self.content[0][
        #                                         "video_note_file"]))
        # if "sticker_file" in self.content[0]:
        #     context.user_data["to_delete"].append(
        #         context.bot.send_sticker(chat_id,
        #                                  self.content[0]["sticker_file"]))

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
            # self.images = product.get("images", list())
            self.content = product.get("content", list())
            self.in_trash = product.get("in_trash")
            self.category_id = product.get("category_id")
            self.quantity = product.get("quantity"),
            self.unlimited = product.get("unlimited")

        else:
            products_table.update_one(
                {"_id": self._id},
                {"$set": {"price": self.price,
                          "bot_id": self.bot_id,
                          "discount_price": self.discount_price,
                          "description": self.description,
                          "name": self.name,
                          "category_id": self.category_id,
                          # "images": self.images,
                          "content": self.content,
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
            "bot_id": self.context.bot.id,
            "price": self.price,
            "discount_price": 0,
            "description": self.description,
            "name": self.name,
            "category_id": self.category_id,
            # "images": self.images,
            "content": self.content,
            "sold": False,
            "in_trash": False,
            "on_sale": True,
            "order_ids": list(),
            "creation_timestamp": datetime.now(),
            "quantity": self.quantity,
            "unlimited": self.unlimited
        })

