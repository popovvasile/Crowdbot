import logging
from pprint import pprint

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from bson.objectid import ObjectId

from helper_funcs.misc import delete_messages
from helper_funcs.lang_strings.strings import emoji
from helper_funcs.misc import lang_timestamp, user_mention, get_obj
from database import users_messages_to_admin_table


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


class AnswerToMessage(object):
    """Handle answer to message from inbox and from users list

    The only difference is back button, state(it can be the same int)
    and final callback
    """
    def __init__(self, back_button: str, state: int, final_callback):
        """
        Args:
            back_button: callback_data of the back button
            state: State that handle answer content
            final_callback: callback to execute after sending answer
        """
        self.back_button = back_button
        self.STATE = state
        self.final_callback = final_callback

    def send_message(self, update, context):
        delete_messages(update, context, True)

        message = users_messages_to_admin_table.find_one(
            {"_id": ObjectId(update.callback_query.data.split("/")[1])})
        # context.user_data["chat_id"] = message["chat_id"]
        # context.user_data["message_id"] = message["_id"]
        context.user_data["answer_to"] = message

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                  callback_data=self.back_button)]
        ])
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=context.bot.lang_dict["send_message_3"],
            reply_markup=reply_markup)
        return self.STATE

    def received_message(self, update, context):
        delete_messages(update, context)
        add_to_content(update, context)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                  callback_data="send_message_finish")],
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                  callback_data=self.back_button)]
        ])
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.message.chat_id,
                text=context.bot.lang_dict["send_message_4"],
                reply_markup=reply_markup))
        return self.STATE

    def send_message_finish(self, update, context):
        users_messages_to_admin_table.update_one(
            {"_id": context.user_data["answer_to"]["_id"]},
            {"$set": {"answer_content": context.user_data["content"],
                      # "answer_string": answer_string
                      }})
        # TODO STRINGS
        user_message_temp = (
            "<b>You got the Answer!</b>"
            f"\n<b>Your message:</b>"
            f"\n{content_string(context.user_data['answer_to']['content'])}"
            f"\n<b>Answer:</b>"
            f"\n{content_string(context.user_data['content'])}")

        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                text="Show",
                callback_data="subscriber_open_message/"
                              + str(context.user_data["answer_to"]["_id"]))]])

        context.bot.send_message(
            chat_id=context.user_data["answer_to"]["chat_id"],
            text=user_message_temp,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML)

        logger.info("Admin {} on bot {}:{} sent a message to the user".format(
            update.effective_user.first_name,
            context.bot.first_name, context.bot.id))
        # TODO STRINGS
        update.callback_query.answer("Message sent")
        return self.final_callback(update, context)


def send_deleted_message_content(context, content, chat_id,
                                 delete_key_name="to_delete"):
    """Sends content and add message to the 'to_delete' list"""

    for content_dict in content:
        if "text" in content_dict:
            context.user_data[delete_key_name].append(
                context.bot.send_message(chat_id, content_dict["text"]))
        if "audio_file" in content_dict:
            context.user_data[delete_key_name].append(
                context.bot.send_audio(chat_id, content_dict["audio_file"]))
        if "voice_file" in content_dict:
            context.user_data[delete_key_name].append(
                context.bot.send_voice(chat_id, content_dict["voice_file"]))
        if "video_file" in content_dict:
            context.user_data[delete_key_name].append(
                context.bot.send_video(chat_id, content_dict["video_file"]))
        if "video_note_file" in content_dict:
            context.user_data[delete_key_name].append(
                context.bot.send_video_note(chat_id,
                                            content_dict["video_note_file"]))
        if "document_file" in content_dict:
            if (".png" in content_dict["document_file"] or
                    ".jpg" in content_dict["document_file"]):
                context.user_data[delete_key_name].append(
                    context.bot.send_photo(chat_id,
                                           content_dict["document_file"]))
            else:
                context.user_data[delete_key_name].append(
                    context.bot.send_document(chat_id,
                                              content_dict["document_file"]))
        if "photo_file" in content_dict:
            context.user_data[delete_key_name].append(
                context.bot.send_photo(chat_id, content_dict["photo_file"]))
        if "animation_file" in content_dict:
            context.user_data[delete_key_name].append(
                context.bot.send_animation(chat_id,
                                           content_dict["animation_file"]))
        if "sticker_file" in content_dict:
            context.user_data[delete_key_name].append(
                context.bot.send_sticker(chat_id,
                                         content_dict["sticker_file"]))


def send_not_deleted_message_content(context, content, chat_id):
    """Sends content without adding message to the 'to_delete' list"""

    for content_dict in content:
        if "text" in content_dict:
            context.bot.send_message(chat_id, content_dict["text"])
        if "audio_file" in content_dict:
            context.bot.send_audio(chat_id, content_dict["audio_file"])
        if "voice_file" in content_dict:
            context.bot.send_voice(chat_id, content_dict["voice_file"])
        if "video_file" in content_dict:
            context.bot.send_video(chat_id, content_dict["video_file"])
        if "video_note_file" in content_dict:
            context.bot.send_video_note(chat_id,
                                        content_dict["video_note_file"])
        if "document_file" in content_dict:
            if (".png" in content_dict["document_file"] or
                    ".jpg" in content_dict["document_file"]):
                context.bot.send_photo(chat_id, content_dict["document_file"])
            else:
                context.bot.send_document(chat_id,
                                          content_dict["document_file"])
        if "photo_file" in content_dict:
            context.bot.send_photo(chat_id, content_dict["photo_file"])
        if "animation_file" in content_dict:
            context.bot.send_animation(chat_id,
                                       content_dict["animation_file"])
        if "sticker_file" in content_dict:
            context.bot.send_sticker(chat_id, content_dict["sticker_file"])


def add_to_content(update, context):
    """Adds message to the user_data 'content' key"""

    if "content" not in context.user_data:
        context.user_data["content"] = []

    if update.message.text:
        context.user_data["content"].append({"text": update.message.text})

    elif update.message.photo:
        photo_file = update.message.photo[-1].get_file().file_id
        context.user_data["content"].append({"photo_file": photo_file})

    elif update.message.audio:
        audio_file = update.message.audio.get_file().file_id
        context.user_data["content"].append(
            {"audio_file": audio_file, "name": update.message.audio.title})

    elif update.message.voice:
        voice_file = update.message.voice.get_file().file_id
        context.user_data["content"].append({"voice_file": voice_file})

    elif update.message.document:
        document_file = update.message.document.get_file().file_id
        context.user_data["content"].append(
            {"document_file": document_file,
             "name": update.message.document.file_name})

    elif update.message.video:
        video_file = update.message.video.get_file().file_id
        context.user_data["content"].append({"video_file": video_file})

    elif update.message.video_note:
        video_note_file = update.message.video_note.get_file().file_id
        context.user_data["content"].append(
            {"video_note_file": video_note_file})

    elif update.message.animation:
        animation_file = update.message.animation.get_file().file_id
        context.user_data["content"].append(
            {"animation_file": animation_file})

    elif update.message.sticker:
        sticker_file = update.message.sticker.get_file().file_id
        context.user_data["content"].append(
            {"sticker_file": sticker_file,
             "name": update.message.sticker.emoji})


class MessageTemplate(object):
    def __init__(self, obj: (ObjectId, dict, str), context):
        self.context = context
        message_obj = get_obj(users_messages_to_admin_table, obj)
        self.chat_id = message_obj["chat_id"]
        self.user_id = message_obj["user_id"]
        # self.is_new = message_obj["is_new"]
        # self.anonim = message_obj["anonim"]
        self.timestamp = message_obj["timestamp"]
        self.content = message_obj["content"]
        self.answer_content = message_obj["answer_content"]
        self.user_full_name = message_obj["user_full_name"]
        # Get chat member to get user information
        # because database data can be incorrect
        user = context.bot.get_chat_member(self.chat_id, self.user_id).user
        # Create user html mention
        if message_obj["anonim"]:
            self.user_mention = f"<code>{self.user_full_name}</code>"
        elif user.username:
            self.user_mention = user_mention(user.username, user.full_name)
        else:
            self.user_mention = user.mention_html()
        # If message is new - add emoji near it
        if message_obj["is_new"]:
            self.title_emoji = emoji['new'] + "\n"
        else:
            self.title_emoji = ""

    def super_short_temp(self):
        return self.title_emoji + "<b>From:</b> " + self.user_mention

    def short_temp(self):
        return (self.title_emoji
                + self.context.bot.lang_dict["short_message_temp"].format(
                    self.user_mention,
                    lang_timestamp(self.context, self.timestamp)))

    def full_temp(self):
        template = (self.title_emoji
                    + self.context.bot.lang_dict["message_temp"].format(
                        self.user_mention,
                        lang_timestamp(self.context, self.timestamp),
                        content_string(self.content)))
        if self.answer_content:
            template += self.context.bot.lang_dict["answer_field"].format(
                content_string(self.answer_content))
        return template

    def send(self, chat_id, temp="full", reply_markup=None, text=""):
        if temp == "short":
            template = self.short_temp()
        elif temp == "super_short":
            template = self.super_short_temp()
        else:
            template = self.full_temp()

        self.context.user_data["to_delete"].append(
            self.context.bot.send_message(
                chat_id=chat_id,
                text=template + "\n\n" + text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML))

    # def template(self, context, short=False):
        # Get chat member to get user information
        # because database data can be incorrect
        # user = context.bot.get_chat_member(self.chat_id, self.user_id).user
        # Create user html mention
        # if self.anonim:
        #     _user_mention = f"<code>{self.user_full_name}</code>"
        # elif user.username:
        #     _user_mention = user_mention(user.username, user.full_name)
        # else:
        #     _user_mention = user.mention_html()

        # If message is new - add emoji near it
        # title_emoji = ""
        # if self.is_new:
        #     title_emoji = emoji['new'] + "\n"
        # if short:
        #     template = (title_emoji
        #                 + context.bot.lang_dict["short_message_temp"].format(
        #                     _user_mention,
        #                     lang_timestamp(context, self.timestamp)))
        # else:
        #     template = (title_emoji
        #                 + context.bot.lang_dict["message_temp"].format(
        #                     _user_mention,
        #                     lang_timestamp(context, self.timestamp),
        #                     content_string(self.content)))
        #     if self.answer_content:
        #         template += context.bot.lang_dict["answer_field"].format(
        #             content_string(self.answer_content))
        # return template

    # def send(self, chat_id, context, reply_markup, text="", short=False):
    #     context.user_data["to_delete"].append(
    #         context.bot.send_message(
    #             chat_id=chat_id,
    #             text=self.template(context, short) + "\n\n" + text,
    #             reply_markup=reply_markup,
    #             parse_mode=ParseMode.HTML))


# TODO STRINGS
def content_string(content):
    """Makes message content as string"""
    string = ""
    for content_dict in content:
        if "text" in content_dict:
            str_for_text = content_dict['text'][:20]
            if len(content_dict['text']) > 20:
                str_for_text += "..."
            string += f"• <code>{str_for_text}</code>\n"

        if "photo_file" in content_dict:
            string += "• Photo\n"

        if "voice_file" in content_dict:
            string += "• Voice message\n"

        if ("audio_file" in content_dict or
                "document_file" in content_dict or
                "sticker_file" in content_dict):
            string += f"• {content_dict['name']}\n"

        if "video_file" in content_dict:
            string += "• Video\n"

        if "video_note_file" in content_dict:
            string += "• Video message\n"

        if "animation_file" in content_dict:
            string += "• Animation\n"
    return string[:-1]
