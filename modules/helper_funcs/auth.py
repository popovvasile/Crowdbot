from typing import Optional
from functools import wraps
from telegram import User, Bot, Update

from database import users_table, chatbots_table


def register_chat(bot, update):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    superuser = chatbots_table.find_one({"bot_id": bot.id})["superuser"]
    if user_id == superuser:
        users_table.update({"user_id": user_id},
                           {'bot_id': bot.id,
                            "chat_id": chat_id,
                            "user_id": user_id,
                            "username": update.effective_user.username,
                            "full_name": update.effective_user.full_name,
                            'registered': True,
                            "is_admin": True,
                            "tags": ["#all", "#user", "#admin"]
                            }, upsert=True)
    elif users_table.find({"user_id": user_id, "bot_id": bot.id}).count() == 0:
        users_table.insert(
                           {'bot_id': bot.id,
                            "chat_id": chat_id,
                            "user_id": user_id,
                            "username": update.effective_user.username,
                            "full_name": update.effective_user.full_name,
                            'registered': False,
                            "is_admin": False,
                            "tags": ["#all", "#user"]
                            })


def initiate_chat_id(update):
    chat_id = update.effective_chat.id
    txt = ""
    if update.message.text:
        txt = txt + update.message.text
    elif update.message.caption:
        txt = txt + update.message.caption
    return chat_id, txt


def if_admin(update, bot):
    if update.message:
        user_id = update.message.from_user.id
    else:
        user_id = update.callback_query.from_user.id
    superuser = chatbots_table.find_one({"bot_id": bot.id})["superuser"]
    if user_id == superuser:
        return True
    admin_chat = users_table.find_one({'user_id': user_id, "bot_id": bot.id})
    if admin_chat is not None:
        if admin_chat["registered"] and admin_chat["is_admin"]:
            return True
        else:
            return False
    else:
        return False


def user_admin(func):
    @wraps(func)
    def is_admin(bot: Bot, update: Update, *args, **kwargs):
        user = update.effective_user  # type: Optional[User]
        if user and if_admin(update, bot):
            return func(bot, update, *args, **kwargs)

        elif not user:
            pass

        else:
            update.effective_message.reply_text("Who dis non-admin telling me what to do?")

    return is_admin
