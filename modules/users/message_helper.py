from telegram import ParseMode

from helper_funcs.lang_strings.strings import emoji
from helper_funcs.misc import lang_timestamp, user_mention


"""def send_deleted_message_content(context, content, chat_id):
    for content_dict in content:
        if "text" in content_dict:
            context.user_data["to_delete"].append(
                query.message.reply_text(text=content_dict["text"]))
        if "audio_file" in content_dict:
            context.user_data["to_delete"].append(
                query.message.reply_audio(content_dict["audio_file"]))
        if "voice_file" in content_dict:
            context.user_data["to_delete"].append(
                query.message.reply_audio(content_dict["voice_file"]))
        if "video_file" in content_dict:
            context.user_data["to_delete"].append(
                query.message.reply_video(content_dict["video_file"]))
        if "video_note_file" in content_dict:
            context.user_data["to_delete"].append(
                query.message.reply_video_note(
                    content_dict["video_note_file"]))
        if "document_file" in content_dict:
            if (".png" in content_dict["document_file"] or
                    ".jpg" in content_dict["document_file"]):
                context.user_data["to_delete"].append(
                    query.message.reply_photo(
                        photo=content_dict["document_file"]))
            else:
                context.user_data["to_delete"].append(
                    query.message.reply_document(
                        document=content_dict["document_file"]))
        if "photo_file" in content_dict:
            context.user_data["to_delete"].append(
                query.message.reply_photo(photo=content_dict["photo_file"]))
        if "animation_file" in content_dict:
            context.user_data["to_delete"].append(
                query.message.reply_animation(
                    photo=content_dict["animation_file"]))
        if "sticker_file" in content_dict:
            context.user_data["to_delete"].append(query.message.reply_sticker(
                photo=content_dict["sticker_file"]))"""


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
    context.user_data["to_delete"].append(
        context.bot.send_message(
            chat_id=update.callback_query.message.chat_id,
            text=(f"{emoji['new']}\n" if message["is_new"] else "")
            + context.bot.lang_dict["message_temp"].format(
                f"<code>{message['user_full_name']}</code>"
                if message["anonim"]
                else user_mention(message["user_id"],
                                  message["user_full_name"]),
                lang_timestamp(context, message["timestamp"]))
            + "\n\n" + text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML))
