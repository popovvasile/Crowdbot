import datetime
# Bot
from mongoengine import Document, StringField, DateTimeField, IntField, ListField, ReferenceField, \
    EmbeddedDocument, BooleanField, FloatField


class Content(EmbeddedDocument):
    file_id = StringField(required=True, max_length=200)
    type = StringField(required=True, max_length=200)
    id = StringField(required=True, max_length=200)


class Category(Document):
    name = StringField(required=True, max_length=200)
    query_name = StringField(required=True, max_length=200)
    bot_id = IntField(required=True)


class Product(Document):
    bot_id = IntField(required=True)
    name = StringField(required=True, max_length=200)
    description = StringField(required=True)
    discount_price = FloatField(default=0)
    price = FloatField(default=0)
    creation_timestamp = DateTimeField(default=datetime.datetime.now)
    last_modify_timestamp = DateTimeField(default=datetime.datetime.now)
    content = ListField(ReferenceField(Content))
    quantity = IntField(required=True, default=0)
    unlimited = BooleanField(default=True)
    in_trash = BooleanField(default=False)
    on_sale = BooleanField(default=False)
    category_id = ReferenceField(Category)


class Item(EmbeddedDocument):
    product_id = ListField(ReferenceField(Product))
    quantity = 0


class Orders(Document):
    bot_id = IntField(required=True)
    user_id = IntField(required=True)
    total_price = FloatField(default=0)
    currency = StringField(required=True, max_length=200)
    user_comment = StringField(required=True)
    phone_number = StringField(required=True, max_length=200)
    address = StringField(required=True, max_length=200)
    shipping = BooleanField(default=False)
    status = BooleanField(default=False)
    creation_timestamp = DateTimeField(default=datetime.datetime.now)
    last_modify_timestamp = DateTimeField(default=datetime.datetime.now)
    in_trash = BooleanField(default=False)
    paid = BooleanField(default=False)
    intems = ListField(ReferenceField(Item))


class CartProduct(EmbeddedDocument):
    product_id = ReferenceField(Product)
    quantity = IntField(required=True, default=1)


class Carts(Document):
    bot_id = IntField(required=True)
    user_id = IntField(required=True)
    products = ListField(ReferenceField(CartProduct))


class Address(EmbeddedDocument):
    address = StringField(required=True, max_length=200)


class PhoneNumber(EmbeddedDocument):
    number = StringField(required=True, max_length=200)


class CustomersContacts(Document):
    addresses = ListField(ReferenceField(Address))
    phone_numbers = ListField(ReferenceField(PhoneNumber))
