import logging
from pprint import pprint

from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from bson.objectid import ObjectId

from helper_funcs.misc import delete_messages
from helper_funcs.lang_strings.strings import emoji
from helper_funcs.misc import lang_timestamp, user_mention
from database import users_messages_to_admin_table


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)
logger = logging.getLogger(__name__)


def send_deleted_message_content(context, content, chat_id):
    for content_dict in content:
        if "text" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_message(chat_id, content_dict["text"]))
        if "audio_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_audio(chat_id, content_dict["audio_file"]))
        if "voice_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_voice(chat_id, content_dict["voice_file"]))
        if "video_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_video(chat_id, content_dict["video_file"]))
        if "video_note_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_video_note(chat_id,
                                            content_dict["video_note_file"]))
        if "document_file" in content_dict:
            if (".png" in content_dict["document_file"] or
                    ".jpg" in content_dict["document_file"]):
                context.user_data["to_delete"].append(
                    context.bot.send_photo(chat_id,
                                           content_dict["document_file"]))
            else:
                context.user_data["to_delete"].append(
                    context.bot.send_document(chat_id,
                                              content_dict["document_file"]))
        if "photo_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_photo(chat_id, content_dict["photo_file"]))
        if "animation_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_animation(chat_id,
                                           content_dict["animation_file"]))
        if "sticker_file" in content_dict:
            context.user_data["to_delete"].append(
                context.bot.send_sticker(chat_id,
                                         content_dict["sticker_file"]))


def send_not_deleted_message_content(context, content, chat_id):
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
    if "content" not in context.user_data:
        context.user_data["content"] = []
    if update.message.text:
        context.user_data["content"].append({"text": update.message.text})

    elif update.message.photo:
        photo_file = update.message.photo[-1].get_file().file_id
        context.user_data["content"].append({"photo_file": photo_file})

    elif update.message.audio:
        audio_file = update.message.audio.get_file().file_id
        context.user_data["content"].append({"audio_file": audio_file})

    elif update.message.voice:
        voice_file = update.message.voice.get_file().file_id
        context.user_data["content"].append({"audio_file": voice_file})

    elif update.message.document:
        document_file = update.message.document.get_file().file_id
        context.user_data["content"].append({"document_file": document_file})

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
        context.user_data["content"].append({"sticker_file": sticker_file})


def send_message_template(update, context, message, reply_markup, text=""):
    # Get chat member to get user information
    # because database data can be incorrect
    user = context.bot.get_chat_member(message["chat_id"],
                                       message["user_id"]).user
    if message["anonim"]:
        _user_mention = f"<code>{message['user_full_name']}</code>"
    elif user.username:
        _user_mention = user_mention(user.username, user.full_name)
    else:
        _user_mention = user.mention_html()

    context.user_data["to_delete"].append(
        context.bot.send_message(
            update.effective_chat.id,
            text=((emoji['new'] + "\n") if message["is_new"] else "")
            + context.bot.lang_dict["message_temp"].format(
                _user_mention, lang_timestamp(context, message["timestamp"]))
            + "\n\n" + text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML))


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
        context.user_data["chat_id"] = message["chat_id"]

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
        add_to_content(update, context)
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                  callback_data="send_message_finish")],
            [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                  callback_data=self.back_button)]
        ])
        context.bot.send_message(chat_id=update.message.chat_id,
                                 text=context.bot.lang_dict["send_message_4"],
                                 reply_markup=reply_markup)
        return self.STATE

    def send_message_finish(self, update, context):
        context.bot.send_message(
            chat_id=context.user_data["chat_id"],
            text=context.bot.lang_dict["send_message_answer_user"])
        send_not_deleted_message_content(
            context,
            chat_id=context.user_data["chat_id"],
            content=context.user_data["content"])
        logger.info("Admin {} on bot {}:{} sent a message to the user".format(
            update.effective_user.first_name,
            context.bot.first_name, context.bot.id))
        # TODO STRINGS
        update.callback_query.answer("Message sent")
        return self.final_callback(update, context)
