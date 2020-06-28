import datetime
# Bot
from mongoengine import Document, StringField, DateTimeField, IntField, EmbeddedDocument, \
    BooleanField, ReferenceField


class Shop(EmbeddedDocument):
    shop_type = StringField(required=True, max_length=200)
    shipping = BooleanField(default=False)
    description = StringField(required=True, max_length=200)
    currency = StringField(required=True, max_length=200)
    payment_token = StringField(required=True, max_length=200)


class Chatbots(Document):
    bot_id = IntField(required=True)
    superuser = IntField(required=True)
    active = BooleanField(default=True)
    lang = StringField(required=True, max_length=200)
    welcomeMessage = StringField(required=True, max_length=200)
    token = StringField(required=True, max_length=200)
    name = StringField(required=True, max_length=200)
    username = StringField(required=True, max_length=200)
    shop_enabled = BooleanField(default=False)
    creation_timestamp = DateTimeField(default=datetime.datetime.now)
    shop = ReferenceField(Shop)


class AdminPasswords(Document):
    bot_id = IntField(required=True)
    password = StringField(required=True, max_length=200)
    timestamp = DateTimeField(default=datetime.datetime.now)


class Users(Document):
    bot_id = IntField(required=True)
    chat_id = IntField(required=True)
    user_id = IntField(required=True)
    username = StringField(required=True, max_length=200)
    full_name = StringField(required=True, max_length=200)
    is_admin = BooleanField(default=True)
    superuser = BooleanField(default=True)
    timestamp = DateTimeField(default=datetime.datetime.now)
    regular_messages_blocked = BooleanField(default=False)
    anonim_messages_blocked = BooleanField(default=False)
    order_notification = BooleanField(default=True)
    messages_notification = BooleanField(default=True)
    blocked = BooleanField(default=False)
    unsubscribed = BooleanField(default=False)


class UserMode(Document):
    bot_id = IntField(required=True)
    user_id = IntField(required=True)
    user_mode = BooleanField(default=False)
