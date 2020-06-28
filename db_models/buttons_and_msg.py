import datetime
# Bot
from mongoengine import Document, StringField, DateTimeField, IntField, \
    BooleanField, ListField, ReferenceField

from db_models.shop_models import Content


class CustomButtons(Document):
    bot_id = IntField(required=True)
    admin_id = IntField(required=True)
    button = StringField(required=True, max_length=200)
    lower_button = StringField(required=True, max_length=200)
    content = ListField(ReferenceField(Content))
    link_button = BooleanField(default=False)
    published = DateTimeField(default=datetime.datetime.now)


class UsersMessagesToAdmin(Document):
    bot_id = IntField(required=True)
    chat_id = IntField(required=True)
    user_id = IntField(required=True)
    anonim = BooleanField(default=False)
    is_new = BooleanField(default=False)
    deleted = BooleanField(default=False)
    user_full_name = StringField(required=True)
    content = ListField(ReferenceField(Content))
    answer_content = ListField(ReferenceField(Content))
    timestamp = DateTimeField(required=True, default=datetime.datetime.now)
