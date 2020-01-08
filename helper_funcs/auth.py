import logging
from typing import Optional
from functools import wraps
from datetime import datetime

from telegram import User, Bot, Update

from database import users_table, chatbots_table, admin_passwords_table


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)


def register_chat(update, context):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    superuser = chatbots_table.find_one({"bot_id": context.bot.id})["superuser"]
    if user_id == superuser:
        users_table.update({"user_id": user_id,
                            "bot_id": context.bot.id},
                           {'bot_id': context.bot.id,
                            "chat_id": chat_id,
                            "user_id": user_id,
                            "username": update.effective_user.username,
                            "full_name": update.effective_user.full_name,
                            # "mention_markdown": update.effective_user.mention_markdown(),
                            # "mention_html": update.effective_user.mention_html(),
                            'registered': True,
                            "is_admin": True,
                            "superuser": True,
                            "timestamp": datetime.now(),
                            "regular_messages_blocked": False,
                            "anonim_messages_blocked": False,
                            "blocked": False,
                            "unsubscribed": False,
                            "tags": ["#all", "#user", "#admin"]
                            }, upsert=True)
    elif not users_table.find_one({"user_id": user_id,
                                   "bot_id": context.bot.id}):
        users_table.insert({'bot_id': context.bot.id,
                            "chat_id": chat_id,
                            "user_id": user_id,
                            "username": update.effective_user.username,
                            "full_name": update.effective_user.full_name,
                            # "mention_markdown": update.effective_user.mention_markdown(),
                            # "mention_html": update.effective_user.mention_html(),
                            "timestamp": datetime.now(),
                            'registered': False,
                            "is_admin": False,
                            "superuser": False,
                            "regular_messages_blocked": False,
                            "anonim_messages_blocked": False,
                            "blocked": False,
                            "unsubscribed": False,
                            "tags": ["#all", "#user"]})


def register_admin(update, context):
    """
    Registers user as an administrator.
    """
    # For first delete all expired passwords
    for admin_password in admin_passwords_table.find(
            {"bot_id": context.bot.id}):
        if ((datetime.today() - admin_password["timestamp"]).total_seconds()
                > 3600):
            admin_passwords_table.delete_one({"_id": admin_password["_id"]})
    # Check if the user already admin if so - just back
    if users_table.find_one({"bot_id": context.bot.id,
                             "user_id": update.effective_user.id})[
            "is_admin"]:
        return False
    # Take password from update
    password = update.message.text.split("registration")[-1]
    # Check db for the password. We deleted all the wrong passwords,
    # so if the password is found, then it is valid
    # and never used before(coz we delete password after registration)
    admin_password = admin_passwords_table.find_one({"bot_id": context.bot.id,
                                                     "password": password})
    # Register user only if the password is correct
    # and date not expired and password never used before
    if admin_password:
        # Invalidate password(delete it)
        admin_passwords_table.delete_one({"_id": admin_password["_id"]})
        # Set user as administrator
        users_table.update_one(
            {"user_id": update.effective_user.id, "bot_id": context.bot.id},
            {"$set": {
                'bot_id': context.bot.id,
                "chat_id": update.effective_chat.id,
                "user_id": update.effective_user.id,
                "email": "No emails for now",
                "username": update.effective_user.username,
                "full_name": update.effective_user.full_name,
                "timestamp": datetime.now(),
                'registered': True,
                "is_admin": True,
                "regular_messages_blocked": False,
                "anonim_messages_blocked": False,
                "superuser": False,
                "blocked": False,
                "unsubscribed": False,
                "tags": ["#all", "#user", "#admin"]}}, upsert=True)

        context.bot.send_message(
            chat_id=update.effective_chat.id,
            # TODO STRINGS
            text=f"Hello, {update.effective_user.full_name} New Admin!")

        logger.info(f"New admin {update.effective_user.full_name} "
                    f"on bot {context.bot.first_name}:{context.bot.id}")
        return True
    else:
        logger.info(f"Admin authentication failed for "
                    f"{update.effective_user.full_name} "
                    f"on bot {context.bot.first_name}:{context.bot.id}")
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            # TODO STRINGS
            text="Registration link is no longer active. "
                 "Ask admins for the new one")
        return False


def initiate_chat_id(update):
    chat_id = update.effective_chat.id
    txt = ""
    if update.message.text:
        txt = txt + update.message.text
    elif update.message.caption:
        txt = txt + update.message.caption
    return chat_id, txt


def if_admin(update, context):
    if update.message:
        user_id = update.message.from_user.id
    else:
        user_id = update.callback_query.from_user.id
    superuser = chatbots_table.find_one({"bot_id": context.bot.id})["superuser"]
    if user_id == superuser:
        return True
    admin_chat = users_table.find_one({'user_id': user_id, "bot_id": context.bot.id})
    if admin_chat is not None:
        if admin_chat["registered"] and admin_chat["is_admin"]:
            return True
        else:
            return False
    else:
        return False


def user_admin(func):
    @wraps(func)
    def is_admin(update, context, *args, **kwargs):
        user = update.effective_user  # type: Optional[User]
        if user and if_admin(update, context.bot):
            return func(context.bot, update, *args, **kwargs)

        elif not user:
            pass

        else:
            update.effective_message.reply_text("Who dis non-admin telling me what to do?")

    return is_admin
