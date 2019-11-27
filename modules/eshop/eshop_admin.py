#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import logging
from database import products_table, chatbots_table
from helper_funcs.helper import get_help
from helper_funcs.auth import initiate_chat_id
from helper_funcs.lang_strings.strings import string_dict
from helper_funcs.misc import delete_messages

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)
CHOOSE_PRODUCT = 1
EDIT_FINISH = 1
TYPING_PRODUCT, TYPING_PRICE, CHOOSE_TYPE, TYPING_CURRENCY, TYPING_DESCRIPTION, DESCRIPTION_FINISH = range(6)
TYPING_TO_DELETE_PRODUCT = 17
TYPING_LINK, TYPING_PRODUCT_FINISH = range(2)


def eshop_menu(bot, update):
    string_d_str = string_dict(bot)
    bot.delete_message(chat_id=update.callback_query.message.chat_id,
                       message_id=update.callback_query.message.message_id)
    chatbot = chatbots_table.find_one({"bot_id": bot.id})
    admin_keyboard = []
    if chatbot["shop_enabled"] is True:
        admin_keyboard += [[InlineKeyboardButton(text=string_d_str["products"],
                                  callback_data="products")],
             [InlineKeyboardButton(text=string_d_str["add_product_button"],
                                  callback_data="create_product")],
             [InlineKeyboardButton(text=string_d_str["edit_product"],
                                  callback_data="edit_product")],
             [InlineKeyboardButton(text=string_d_str["delete_product"],
                                  callback_data="delete_product")],
             [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                   callback_data="help_module(shop)")]]
    else:
        admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                                    # TODO enforce to configure the tokens and everything first time
                                                    callback_data="change_donations_config")]),


    admin_keyboard.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                            callback_data="help_module(settings)")])

    bot.send_message(update.callback_query.message.chat.id,
                     string_dict(bot)["shop"], reply_markup=admin_keyboard)
    return ConversationHandler.END


class ProcductMenu(object):
    def send_product_menu(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = [InlineKeyboardButton(button["title"],
                                        callback_data="product_{}".format(button["title"].replace(" ", "").lower()))
                   for button in products_table.find({"bot_id": bot.id})]

        if len(buttons) > 0:
            if len(buttons) % 2 == 0:
                pairs = list(zip(buttons[::2], buttons[1::2]))
            else:
                pairs = list(zip(buttons[::2], buttons[1::2])) + [(buttons[-1],)] \
                        + [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                 callback_data="help_module(shop)")]]
            bot.send_message(chat_id=update.effective_chat.id,
                             text="Products menu",
                             parse_mode=ParseMode.MARKDOWN,
                             reply_markup=InlineKeyboardMarkup(
                                 pairs
                             ))
        else:
            bot.send_message(chat_id=update.callback_query.message.chat_id,
                             text=string_dict(bot)["manage_button_str_2"],
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(
                                     string_dict(bot)["add_product_button"],
                                     callback_data="create_product"),
                                     InlineKeyboardButton(
                                         string_dict(bot)["back_button"],
                                         callback_data="help_module(shop)")]]
                             ), parse_mode='Markdown')


class AddProducts(object):

    def start(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        user_data["to_delete"] = []
        reply_products = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)

        user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                       string_dict(bot)["add_products_str_1"]))
        user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                       string_dict(bot)["back_text"], reply_markup=reply_markup))
        return TYPING_PRODUCT

    def product_handler(self, bot, update,
                        user_data):  # TODO add price and yes or not for delivery- ask address or not?
        user_data["to_delete"].append(update.message)
        reply_products = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        chat_id, txt = initiate_chat_id(update)
        product_list_of_dicts = products_table.find({
            "bot_id": bot.id,
            "title": txt})
        if product_list_of_dicts.count() == 0:

            user_data['title'] = txt
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["great_text"],
                                                                    reply_markup=ReplyKeyboardRemove()))
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_products_price"],
                                                                    reply_markup=reply_markup))
            return TYPING_PRICE
        else:
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_products_str_title_taken"],
                                                                    reply_markup=reply_markup))

            return TYPING_PRODUCT

    def type_price(self, bot, update, user_data):
        reply_products = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        chat_id, txt = initiate_chat_id(update)
        try:
            amount = int(float(txt) * 100)
            user_data["price"] = amount
            currency_keyboard = [["RUB", "USD", "EUR", "GBP"],
                                 ["CHF", "AUD", "RON", "PLN"]]
            update.message.reply_text(string_dict(bot)["add_products_str_currency"],
                                      reply_markup=ReplyKeyboardMarkup(currency_keyboard, one_time_keyboard=True))

            return TYPING_CURRENCY
        except ValueError:
            update.message.reply_text(text=string_dict(bot)["add_products_str_correct_format_price"],
                                      reply_markup=reply_markup)
            return TYPING_PRICE

    def handle_currency(self, bot, update, user_data):
        currency_keyboard = [["With shipping"], ["Without shipping"]]
        chat_id, txt = initiate_chat_id(update)
        user_data["currency"] = txt
        user_data["to_delete"].append(
            update.message.reply_text(string_dict(bot)
                                      ["add_products_str_shipment"],
                                      reply_markup=ReplyKeyboardMarkup(currency_keyboard)))
        return CHOOSE_TYPE

    def handle_type(self, bot, update, user_data):

        reply_products = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        chat_id, txt = initiate_chat_id(update)
        if txt == "With shipping":
            user_data["shipping"] = True
        else:
            user_data["shipping"] = False
        user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_products_str_description"],
                                                                reply_markup=reply_markup))
        return TYPING_DESCRIPTION

    def description_handler(self, bot, update, user_data):
        user_data["to_delete"].append(update.message)
        reply_products = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        if "content" not in user_data:
            user_data["content"] = []
        general_list = user_data["content"]
        if update.callback_query:
            if update.message.callback_query.data == string_dict(bot)["done_button"]:
                self.description_finish(bot, update, user_data)
                return ConversationHandler.END
        if update.message.text:
            general_list.append({"text": update.message.text})

        if update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            general_list.append({"photo_file": photo_file})

        if update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            general_list.append({"audio_file": audio_file})

        if update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            general_list.append({"voice_file": voice_file})

        if update.message.document:
            document_file = update.message.document.get_file().file_id
            general_list.append({"document_file": document_file})

        if update.message.video:
            video_file = update.message.video.get_file().file_id
            general_list.append({"video_file": video_file})

        if update.message.video_note:
            video_note_file = update.message.video_note.get_file().file_id
            general_list.append({"video_note_file": video_note_file})
        if update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            general_list.append({"animation_file": animation_file})
        if update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            general_list.append({"sticker_file": sticker_file})
        user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["back_text"],
                                                                reply_markup=reply_markup))
        done_products = [[InlineKeyboardButton(text=string_dict(bot)["done_button"], callback_data="DONE")]]
        done_reply_markup = InlineKeyboardMarkup(
            done_products)
        user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_products_str_description_add"],
                                                                reply_markup=done_reply_markup))
        user_data["content"] = general_list
        return TYPING_DESCRIPTION

    def description_finish(self, bot, update, user_data):
        print(user_data)
        delete_messages(bot, update, user_data)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        user_id = update.effective_user.id
        user_data.update({"title": user_data['title'],
                          "title_lower": user_data['title'].replace(" ", "").lower(),
                          "admin_id": user_id,
                          "bot_id": bot.id,
                          "link_button": False,
                          })
        user_data.pop('to_delete', None)
        products_table.save(user_data)
        reply_products = [
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["add_products_str_added"].format(user_data["title"]),
                         reply_markup=reply_markup)
        logger.info("Admin {} on bot {}:{} added a new product:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["title"]))
        user_data.clear()
        return ConversationHandler.END

    def delete_product(self, bot, update):
        finish_products = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                 callback_data="help_module(shop)")]]
        finish_markup = InlineKeyboardMarkup(
            finish_products)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        product_list_of_dicts = products_table.find({
            "bot_id": bot.id})
        if product_list_of_dicts.count() != 0:
            product_list = [product['title'] for product in product_list_of_dicts]
            reply_keyboard = [product_list]

            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["products_str_choose_the_product_to_del"],
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["back_text"], reply_markup=finish_markup)
            return TYPING_TO_DELETE_PRODUCT
        else:
            reply_products = [[InlineKeyboardButton(text=string_dict(bot)["create_product"],
                                                    callback_data="create_product"),
                               InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")
                               ]]
            reply_markup = InlineKeyboardMarkup(
                reply_products)
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["no_products"], reply_markup=reply_markup)

            return ConversationHandler.END

    def delete_product_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        products_table.delete_one({
            "title": txt,
            "bot_id": bot.id
        })
        update.message.reply_text(
            string_dict(bot)["add_products_str_deleted"].format(txt), reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id=update.message.chat_id,  # TODO send as in polls
                         text=string_dict(bot)["add_products_products_deleted_str"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(string_dict(bot)["add_product_button"],
                                                    callback_data="create_product"),
                               InlineKeyboardButton(string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")]]
                         ))
        logger.info("Admin {} on bot {}:{} deleted the button:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, txt))
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
        return ConversationHandler.END


class ProductEdit(object):
    def start(self, bot, update, user_data):
        user_data["to_delete"] = []
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        all_products = products_table.find({"bot_id": bot.id})
        if all_products.count() > 0:
            user_data["to_delete"].append(bot.send_message(chat_id=update.callback_query.message.chat_id,
                                                           text=string_dict(bot)["manage_button_str_1"],
                                                           reply_markup=ReplyKeyboardMarkup(
                                                               [[product_name["title"]] for product_name in
                                                                all_products]
                                                           ),
                                                           parse_mode='Markdown'))
            return CHOOSE_PRODUCT
        else:
            user_data["to_delete"].append(bot.send_message(chat_id=update.callback_query.message.chat_id,
                                                           text=string_dict(bot)["manage_button_str_2"],
                                                           reply_markup=InlineKeyboardMarkup(
                                                               [[InlineKeyboardButton(
                                                                   string_dict(bot)["add_product_button"],
                                                                   callback_data="create_product"),
                                                                   InlineKeyboardButton(
                                                                       string_dict(bot)["back_button"],
                                                                       callback_data="help_module(shop)")]]
                                                           ), parse_mode='Markdown'))
            return ConversationHandler.END

    def choose_product(self, bot, update, user_data):

        try:
            product_info = products_table.find_one(
                {"bot_id": bot.id, "title": update.message.text}
            )
            for content in product_info["content"]:
                if "text" in content:
                    user_data["to_delete"].append(update.message.reply_text(
                        text=content["text"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(content["text"][:10],
                                                                                   update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["text"][:10],
                                                                                   update.message.text))
                        ]]),
                        parse_mode='Markdown'))
                if "audio_file" in content:
                    user_data["to_delete"].append(update.message.reply_audio(
                        content["audio_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(
                                                     content["audio_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["audio_file"][:10],
                                                                                   update.message.text))
                        ]])
                    ))
                if "voice_file" in content:
                    user_data["to_delete"].append(update.message.reply_voice(
                        content["voice_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(
                                                     content["voice_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["voice_file"][:10],
                                                                                   update.message.text))
                        ]])
                    ))
                if "video_file" in content:
                    user_data["to_delete"].append(update.message.reply_video(
                        content["video_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(
                                                     content["video_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["video_file"][:10],
                                                                                   update.message.text))
                        ]])
                    ))
                if "video_note_file" in content:
                    user_data["to_delete"].append(update.message.reply_video_note(
                        content["video_note_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(
                                                     content["video_note_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["video_note_file"][:10],
                                                                                   update.message.text))
                        ]])
                    ))
                if "document_file" in content:
                    user_data["to_delete"].append(update.message.reply_document(
                        content["document_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(
                                                     content["document_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["document_file"][:10],
                                                                                   update.message.text))
                        ]])
                    ))
                if "photo_file" in content:
                    user_data["to_delete"].append(update.message.reply_photo(
                        content["photo_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(
                                                     content["photo_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["photo_file"][:10],
                                                                                   update.message.text))
                        ]])
                    ))
                if "animation_file" in content:
                    user_data["to_delete"].append(update.message.reply_animation(
                        content["animation_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(
                                                     content["animation_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["animation_file"][:10],
                                                                                   update.message.text))
                        ]])
                    ))
                if "sticker_file" in content:
                    user_data["to_delete"].append(update.message.reply_sticker(
                        content["photo_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="bp_{}___{}".format(
                                                     content["sticker_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="dp_{}___{}".format(content["sticker_file"][:10],
                                                                                   update.message.text))
                        ]])
                    ))
        except BadRequest as excp:
            if excp.message == "Message is not modified":
                pass
            elif excp.message == "Query_id_invalid":
                pass
            elif excp.message == "Message can't be deleted":
                pass
            else:
                LOGGER.exception("Exception in edit buttons")
        user_data["to_delete"].append(bot.send_message(parse_mode='Markdown',
                                                       chat_id=update.message.chat_id,
                                                       text=string_dict(bot)["manage_button_str_3"],
                                                       reply_markup=ReplyKeyboardRemove()))
        user_data["to_delete"].append(bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id,
                                                       text=string_dict(bot)["add_button_content"],
                                                       reply_markup=InlineKeyboardMarkup(
                                                           [[InlineKeyboardButton(text=string_dict(bot)["add_button"],
                                                                                  callback_data="add_content{}".format(
                                                                                      update.message.text))]])))
        user_data["to_delete"].append(bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id,
                                                       text=string_dict(bot)["back_text"],
                                                       reply_markup=InlineKeyboardMarkup(
                                                           [[
                                                               InlineKeyboardButton(
                                                                   string_dict(bot)["back_button"],
                                                                   callback_data="help_module(shop)")]])))
        return ConversationHandler.END

    def edit_product(self, bot, update, user_data):
        reply_products = [
            [InlineKeyboardButton(text=string_dict(bot)["cancel_button"], callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("bp_", "").split("___")  # here is the problem
        user_data["content_id"] = content_data[0]
        user_data["title"] = content_data[1]
        user_data["to_delete"].append(
            bot.send_message(parse_mode='Markdown', chat_id=update.callback_query.message.chat_id,
                             text=string_dict(bot)["manage_button_str_4"],
                             reply_markup=reply_markup))
        return EDIT_FINISH

    def edit_product_finish(self, bot, update, user_data):
        # Remove the old file or text
        product_info = products_table.find_one(
            {"bot_id": bot.id, "title": user_data["title"]}
        )
        content_index = len(product_info["content"])
        for index, content_dict in enumerate(product_info["content"]):
            if any(user_data["content_id"] in ext for ext in content_dict.values()):
                content_index = index
                product_info["content"].remove(content_dict)

        if update.message.text:
            product_info["content"].insert(content_index, {"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            product_info["content"].insert(content_index, {"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            product_info["content"].insert(content_index, {"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            product_info["content"].insert(content_index, {"voice_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            product_info["content"].insert(content_index, {"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            product_info["content"].insert(content_index, {"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            product_info["content"].insert(content_index, {"video_note_file": video_note_file})
        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            product_info["content"].insert(content_index, {"sticker_file": sticker_file})
        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            product_info["content"].insert(content_index, {"animation_file": animation_file})
        products_table.replace_one(
            {"bot_id": bot.id, "title": user_data["title"]},
            product_info
        )
        products = [
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(shop)")]]
        bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id,
                         text=string_dict(bot)["manage_button_str_5"],
                         reply_markup=InlineKeyboardMarkup(products))
        logger.info("Admin {} on bot {}:{} did  the following edit button: {}".format(
            update.effective_use.first_name, bot.first_name, bot.id, user_data["title"]))
        user_data.clear()
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["manage_button_str_6"], reply_markup=ReplyKeyboardRemove(),
                         parse_mode='Markdown'
                         )
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
        return ConversationHandler.END

    def cancel(self, bot, update):
        bot.delete_message(chat_id=update.message.chat_id,
                           message_id=update.message.message_id)
        bot.send_message(update.message.chat.id,
                         "Command is cancelled", reply_markup=ReplyKeyboardRemove(), parse_mode='Markdown'
                         )

        get_help(bot, update)
        return ConversationHandler.END


class AddProductContent(object):
    def add_content_product(self, bot, update, user_data):
        reply_products = [
            [InlineKeyboardButton(text=string_dict(bot)["cancel_button"], callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("add_content", "")  # here is the problem
        user_data["title"] = content_data
        bot.send_message(parse_mode='Markdown', chat_id=update.callback_query.message.chat_id,
                         text=string_dict(bot)["manage_button_str_4"],
                         reply_markup=reply_markup)
        return EDIT_FINISH

    def add_content_product_finish(self, bot, update, user_data):
        product_info = products_table.find_one(
            {"bot_id": bot.id, "title": user_data["title"]}
        )
        if update.message.text:
            product_info["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            product_info["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            product_info["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            product_info["content"].append({"voice_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            product_info["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            product_info["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            product_info["content"].append({"video_note_file": video_note_file})
        elif update.message.animation:
            animation_file = update.message.audio.get_file().file_id
            product_info["content"].append({"animation_file": animation_file})
        elif update.message.sticker:
            sticker_file = update.message.audio.get_file().file_id
            product_info["content"].append({"sticker_file": sticker_file})

        products_table.replace_one(
            {"bot_id": bot.id, "title": user_data["title"]},
            product_info
        )
        products = [
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(shop)")]]
        bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id,
                         text=string_dict(bot)["manage_button_str_5"],
                         reply_markup=InlineKeyboardMarkup(products))
        logger.info("Admin {} on bot {}:{} did  the following edit button: {}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["title"]))
        user_data.clear()
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["manage_button_str_6"], reply_markup=ReplyKeyboardRemove()
                         )
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
        return ConversationHandler.END

    def cancel(self, bot, update):
        bot.delete_message(chat_id=update.message.chat_id,
                           message_id=update.message.message_id)
        bot.send_message(update.message.chat.id,
                         "Command is cancelled", reply_markup=ReplyKeyboardRemove()
                         )

        get_help(bot, update)
        return ConversationHandler.END


class DeleteProductContent(object):

    def delete_message(self, bot, update, user_data):
        products = list()
        products.append(
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            products)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("dp_", "").split("___")  # here is the problem
        user_data["content_id"] = content_data[0]
        user_data["title"] = content_data[1]
        product_info = products_table.find_one(
            {"bot_id": bot.id, "title": user_data["title"]}
        )
        for content_dict in product_info["content"]:
            if any(user_data["content_id"] in ext for ext in content_dict.values()):
                product_info["content"].remove(content_dict)
        bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text=string_dict(bot)["delete_content"],
                         reply_markup=reply_markup)
        products_table.replace_one(
            {"bot_id": bot.id, "title": user_data["title"]},
            product_info
        )
        return ConversationHandler.END


class SeePurcheses(object):
    def add_content_product(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        reply_products = [
            [InlineKeyboardButton(text=string_dict(bot)["cancel_button"], callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("add_content", "")  # here is the problem
        user_data["title"] = content_data
        bot.send_message(parse_mode='Markdown', chat_id=update.callback_query.message.chat_id,
                         text=string_dict(bot)["manage_button_str_4"],
                         reply_markup=reply_markup)
        return EDIT_FINISH


ESHOP_MENU=CallbackQueryHandler(callback=eshop_menu, pattern="shop_menu")
PRODUCTS_MENU_HANDLER = CallbackQueryHandler(ProcductMenu().send_product_menu, pattern="products")
PRODUCT_ADD_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddProducts().start,
                                       pattern=r"create_product",
                                       pass_user_data=True)],

    states={
        TYPING_PRODUCT: [
            MessageHandler(Filters.text,
                           AddProducts().product_handler, pass_user_data=True)],
        TYPING_PRICE: [
            MessageHandler(Filters.text,
                           AddProducts().type_price, pass_user_data=True)],

        TYPING_CURRENCY: [
            MessageHandler(Filters.text,
                           AddProducts().handle_currency, pass_user_data=True)],
        CHOOSE_TYPE: [MessageHandler(Filters.all,
                                     AddProducts().handle_type, pass_user_data=True)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.all,
                                            AddProducts().description_handler, pass_user_data=True)],
        DESCRIPTION_FINISH: [MessageHandler(Filters.text,
                                            AddProducts().description_finish, pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=AddProducts().description_finish, pattern=r"DONE", pass_user_data=True),

        CallbackQueryHandler(callback=AddProducts().back,
                             pattern=r"help_back", pass_user_data=True),
    ]
)
DELETE_PRODUCT_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=AddProducts().delete_product,
                             pattern=r"delete_product")
    ],

    states={
        TYPING_TO_DELETE_PRODUCT: [MessageHandler(Filters.text,
                                                  AddProducts().delete_product_finish,
                                                  pass_user_data=True)],
    },

    fallbacks=[CallbackQueryHandler(callback=AddProducts().back,
                                    pattern=r"help_back", pass_user_data=True),
               ]
)
# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
PRODUCT_EDIT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ProductEdit().start,
                                       pattern=r"edit_product",
                                       pass_user_data=True)],

    states={
        CHOOSE_PRODUCT: [MessageHandler(Filters.text, ProductEdit().choose_product, pass_user_data=True),
                         ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ProductEdit().back,
                             pattern=r"help_back", pass_user_data=True),
    ]
)

PRODUCT_EDIT_FINISH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ProductEdit().edit_product,
                                       pattern=r"bp_", pass_user_data=True)],

    states={

        EDIT_FINISH: [MessageHandler(Filters.all, ProductEdit().edit_product_finish, pass_user_data=True),
                      CallbackQueryHandler(callback=ProductEdit().back,
                                           pattern=r"help_back", pass_user_data=True),
                      ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ProductEdit().back,
                             pattern=r"help_back", pass_user_data=True)
    ]
)
PRODUCT_ADD_FINISH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddProductContent().add_content_product,
                                       pattern=r"add_content", pass_user_data=True)],

    states={

        EDIT_FINISH: [MessageHandler(Filters.all, AddProductContent().add_content_product_finish, pass_user_data=True),
                      ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ProductEdit().back,
                             pattern=r"help_back", pass_user_data=True),
    ]
)
DELETE_PRODUCT_CONTENT_HANDLER = CallbackQueryHandler(pattern="dp_",
                                                      callback=DeleteProductContent().delete_message,
                                                      pass_user_data=True)
