#!/usr/bin/env python
# -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.error import BadRequest
from telegram.ext import MessageHandler, Filters, ConversationHandler, CallbackQueryHandler
import logging
from database import products_table, chatbots_table
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.lang_strings.strings import string_dict
from modules.helper_funcs.misc import delete_messages

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
LOGGER = logging.getLogger(__name__)
CHOOSE_PRODUCT = 1
EDIT_FINISH = 1
TYPING_PRODUCT, TYPING_DESCRIPTION, DESCRIPTION_FINISH = range(3)
TYPING_TO_DELETE_PRODUCT = 17
TYPING_LINK, TYPING_PRODUCT_FINISH = range(2)


class AddButtons(object):

    def start(self, bot, update):
        reply_products = [
                          [InlineKeyboardButton(text=string_dict(bot)["simple_button_str"],
                                                callback_data="create_simple_button")],
                          [InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text=string_dict(bot)["choose_button_type_text"],
                         reply_markup=reply_markup)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        return ConversationHandler.END


class AddCommands(object):

    def start(self, bot, update, user_data):
        user_data["to_delete"] = []
        reply_products = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        products = chatbots_table.find_one({"bot_id": bot.id})["buttons"]
        if products is not None and products != []:
            markup = ReplyKeyboardMarkup([products], one_time_keyboard=True)
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(bot)["add_products_str_1"],
                                                           reply_markup=markup))
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(bot)["back_text"], reply_markup=reply_markup))
            return TYPING_PRODUCT
        else:
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(bot)["add_products_str_1_1"]))
            user_data["to_delete"].append(bot.send_message(update.callback_query.message.chat.id,
                                                           string_dict(bot)["back_text"], reply_markup=reply_markup))
            return TYPING_PRODUCT

    def product_handler(self, bot, update, user_data):
        user_data["to_delete"].append(update.message)
        reply_products = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        chat_id, txt = initiate_chat_id(update)
        product_list_of_dicts = products_table.find({
            "bot_id": bot.id,
            "button": txt})
        if product_list_of_dicts.count() == 0:

            user_data['button'] = txt
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["great_text"],
                                                                    reply_markup=ReplyKeyboardRemove()))
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_products_str_2"],
                                                                    reply_markup=reply_markup))
            return TYPING_DESCRIPTION
        else:
            user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_products_str_3"],
                                                                    reply_markup=reply_markup))

            return TYPING_PRODUCT

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
            print(audio_file)
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
        user_data["to_delete"].append(update.message.reply_text(string_dict(bot)["add_products_str_4"],
                                                                reply_markup=done_reply_markup))
        user_data["content"] = general_list
        return TYPING_DESCRIPTION

    def description_finish(self, bot, update, user_data):
        print(user_data)
        delete_messages(bot, update, user_data)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        user_id = update.effective_user.id
        user_data.update({"button": user_data['button'],
                          "button_lower": user_data['button'].replace(" ", "").lower(),
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
                         string_dict(bot)["add_products_str_5"].format(user_data["button"]),
                         reply_markup=reply_markup)
        logger.info("Admin {} on bot {}:{} added a new button:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["button"]))
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
            product_list = [product['button'] for product in product_list_of_dicts]
            reply_keyboard = [product_list]

            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["add_products_str_6"],
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
                             string_dict(bot)["add_products_str_7"], reply_markup=reply_markup)

            return ConversationHandler.END

    def delete_product_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        products_table.delete_one({
            "button": txt,
            "bot_id": bot.id
        })
        update.message.reply_text(
            string_dict(bot)["add_products_str_8"].format(txt), reply_markup=ReplyKeyboardRemove())
        bot.send_message(chat_id=update.message.chat_id,  # TODO send as in polls
                         text=string_dict(bot)["add_products_str_10"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(string_dict(bot)["create_product_button"],
                                                    callback_data="create_product"),
                               InlineKeyboardButton(string_dict(bot)["back_button"],
                                                    callback_data="help_module(shop)")]]
                         ))
        logger.info("Admin {} on bot {}:{} deleted the button:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, txt))
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        bot.send_message(update.callback_query.message.chat.id,
                         string_dict(bot)["add_products_str_9"], reply_markup=ReplyKeyboardRemove()
                         )
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        user_data.clear()
        return ConversationHandler.END


class ButtonEdit(object):
    def start(self, bot, update, user_data):
        user_data["to_delete"] = []
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        all_products = products_table.find({"bot_id": bot.id})
        if all_products.count() > 0:
            user_data["to_delete"].append(bot.send_message(chat_id=update.callback_query.message.chat_id,
                                                           text=string_dict(bot)["manage_button_str_1"],
                                                           reply_markup=ReplyKeyboardMarkup(
                                                               [[product_name["button"]] for product_name in
                                                                all_products]
                                                           ),
                                                           parse_mode='Markdown'))
            return CHOOSE_PRODUCT
        else:
            user_data["to_delete"].append(bot.send_message(chat_id=update.callback_query.message.chat_id,
                                                           text=string_dict(bot)["manage_button_str_2"],
                                                           reply_markup=InlineKeyboardMarkup(
                                                               [[InlineKeyboardButton(
                                                                   string_dict(bot)["create_product_button"],
                                                                   callback_data="create_product"),
                                                                   InlineKeyboardButton(
                                                                       string_dict(bot)["back_button"],
                                                                       callback_data="help_module(shop)")]]
                                                           ), parse_mode='Markdown'))
            return ConversationHandler.END

    def choose_product(self, bot, update, user_data):

        try:
            product_info = products_table.find_one(
                {"bot_id": bot.id, "button": update.message.text}
            )
            for content in product_info["content"]:
                if "text" in content:
                    user_data["to_delete"].append(update.message.reply_text(
                        text=content["text"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(content["text"][:10],
                                                                                  update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["text"][:10],
                                                                                  update.message.text))
                        ]]),
                        parse_mode='Markdown'))
                if "audio_file" in content:
                    user_data["to_delete"].append(update.message.reply_audio(
                        content["audio_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(
                                                     content["audio_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["audio_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "voice_file" in content:
                    user_data["to_delete"].append(update.message.reply_voice(
                        content["voice_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(
                                                     content["voice_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["voice_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "video_file" in content:
                    user_data["to_delete"].append(update.message.reply_video(
                        content["video_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(
                                                     content["video_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["video_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "video_note_file" in content:
                    user_data["to_delete"].append(update.message.reply_video_note(
                        content["video_note_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(
                                                     content["video_note_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["video_note_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "document_file" in content:
                    user_data["to_delete"].append(update.message.reply_document(
                        content["document_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(
                                                     content["document_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["document_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "photo_file" in content:
                    user_data["to_delete"].append(update.message.reply_photo(
                        content["photo_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(
                                                     content["photo_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["photo_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "animation_file" in content:
                    user_data["to_delete"].append(update.message.reply_animation(
                        content["animation_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(
                                                     content["animation_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["animation_file"][:10],
                                                                                  update.message.text))
                        ]])
                    ))
                if "sticker_file" in content:
                    user_data["to_delete"].append(update.message.reply_sticker(
                        content["photo_file"],
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton(text=string_dict(bot)["edit_product"],
                                                 callback_data="b_{}___{}".format(
                                                     content["sticker_file"][:10], update.message.text)),
                            InlineKeyboardButton(text=string_dict(bot)["delete_button_str"],
                                                 callback_data="d_{}___{}".format(content["sticker_file"][:10],
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
        content_data = update.callback_query.data.replace("b_", "").split("___")  # here is the problem
        user_data["content_id"] = content_data[0]
        user_data["button"] = content_data[1]
        user_data["to_delete"].append(
            bot.send_message(parse_mode='Markdown', chat_id=update.callback_query.message.chat_id,
                             text=string_dict(bot)["manage_button_str_4"],
                             reply_markup=reply_markup))
        return EDIT_FINISH

    def edit_product_finish(self, bot, update, user_data):
        # Remove the old file or text
        product_info = products_table.find_one(
            {"bot_id": bot.id, "button": user_data["button"]}
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
            {"bot_id": bot.id, "button": user_data["button"]},
            product_info
        )
        products = [
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(shop)")]]
        bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id,
                         text=string_dict(bot)["manage_button_str_5"],
                         reply_markup=InlineKeyboardMarkup(products))
        logger.info("Admin {} on bot {}:{} did  the following edit button: {}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["button"]))
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


class AddButtonContent(object):
    def add_content_product(self, bot, update, user_data):
        reply_products = [
            [InlineKeyboardButton(text=string_dict(bot)["cancel_button"], callback_data="help_module(shop)")]]
        reply_markup = InlineKeyboardMarkup(
            reply_products)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("add_content", "")  # here is the problem
        user_data["button"] = content_data
        bot.send_message(parse_mode='Markdown', chat_id=update.callback_query.message.chat_id,
                         text=string_dict(bot)["manage_button_str_4"],
                         reply_markup=reply_markup)
        return EDIT_FINISH

    def add_content_product_finish(self, bot, update, user_data):
        product_info = products_table.find_one(
            {"bot_id": bot.id, "button": user_data["button"]}
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
            {"bot_id": bot.id, "button": user_data["button"]},
            product_info
        )
        products = [
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(shop)")]]
        bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id,
                         text=string_dict(bot)["manage_button_str_5"],
                         reply_markup=InlineKeyboardMarkup(products))
        logger.info("Admin {} on bot {}:{} did  the following edit button: {}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["button"]))
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


class DeleteButtonContent(object):

    def delete_message(self, bot, update, user_data):
        products = list()
        products.append(
            [InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_module(shop)")])
        reply_markup = InlineKeyboardMarkup(
            products)

        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        content_data = update.callback_query.data.replace("d_", "").split("___")  # here is the problem
        user_data["content_id"] = content_data[0]
        user_data["button"] = content_data[1]
        product_info = products_table.find_one(
            {"bot_id": bot.id, "button": user_data["button"]}
        )
        for content_dict in product_info["content"]:
            if any(user_data["content_id"] in ext for ext in content_dict.values()):
                product_info["content"].remove(content_dict)
        bot.send_message(chat_id=update.callback_query.message.chat_id,
                         text=string_dict(bot)["delete_content"],
                         reply_markup=reply_markup)
        products_table.replace_one(
            {"bot_id": bot.id, "button": user_data["button"]},
            product_info
        )
        return ConversationHandler.END


CREATE_PRODUCT_CHOOSE = CallbackQueryHandler(callback=AddButtons().start, pattern="create_product")


PRODUCT_ADD_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddCommands().start,
                                       pattern=r"create_simple_button",
                                       pass_user_data=True)],

    states={
        TYPING_PRODUCT: [
            MessageHandler(Filters.text,
                           AddCommands().product_handler, pass_user_data=True)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.all,
                                            AddCommands().description_handler, pass_user_data=True)],
        DESCRIPTION_FINISH: [MessageHandler(Filters.text,
                                            AddCommands().description_finish, pass_user_data=True)],

    },

    fallbacks=[
        CallbackQueryHandler(callback=AddCommands().description_finish, pattern=r"DONE", pass_user_data=True),

        CallbackQueryHandler(callback=AddCommands().back,
                             pattern=r"help_module", pass_user_data=True),
    ]
)
DELETE_PRODUCT_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(callback=AddCommands().delete_product,
                             pattern=r"delete_button")
    ],

    states={
        TYPING_TO_DELETE_PRODUCT: [MessageHandler(Filters.text,
                                                 AddCommands().delete_product_finish,
                                                 pass_user_data=True)],
    },

    fallbacks=[CallbackQueryHandler(callback=AddCommands().back,
                                    pattern=r"help_module", pass_user_data=True),
               ]
)
# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
PRODUCT_EDIT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ButtonEdit().start,
                                       pattern=r"edit_product",
                                       pass_user_data=True)],

    states={
        CHOOSE_PRODUCT: [MessageHandler(Filters.text, ButtonEdit().choose_product, pass_user_data=True),
                        ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"help_module", pass_user_data=True),
    ]
)

PRODUCT_EDIT_FINISH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=ButtonEdit().edit_product,
                                       pattern=r"b_", pass_user_data=True)],

    states={

        EDIT_FINISH: [MessageHandler(Filters.all, ButtonEdit().edit_product_finish, pass_user_data=True),
                      CallbackQueryHandler(callback=ButtonEdit().back,
                                           pattern=r"help_module", pass_user_data=True),
                      ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"help_module", pass_user_data=True)
    ]
)
PRODUCT_ADD_FINISH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=AddButtonContent().add_content_product,
                                       pattern=r"add_content", pass_user_data=True)],

    states={

        EDIT_FINISH: [MessageHandler(Filters.all, AddButtonContent().add_content_product_finish, pass_user_data=True),
                      ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=ButtonEdit().back,
                             pattern=r"help_module", pass_user_data=True),
    ]
)
DELETE_PRODUCT_CONTENT_HANDLER = CallbackQueryHandler(pattern="d_",
                                              callback=DeleteButtonContent().delete_message, pass_user_data=True)
