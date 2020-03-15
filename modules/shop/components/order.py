from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from bson.objectid import ObjectId

from .product import Product
from database import orders_table, chatbots_table
from helper_funcs.misc import get_obj
from helper_funcs.pagination import Pagination
from helper_funcs.misc import user_mention


class Order(object):
    def __init__(self, context,  obj: (ObjectId, dict, str) = None):
        order = get_obj(orders_table, obj)
        self.context = context
        self._id = order.get("_id")
        self.article = str(self._id)
        self.status = order.get("status")  # True or False
        self.bot_id = order.get("bot_id") or context.bot.id
        self.user_id = order.get("user_id")
        self.creation_timestamp = str(
            order.get("creation_timestamp", ".")).split(".")[0]
        self.in_trash = order.get("in_trash")
        self.total_price = order.get("total_price")
        self.items_json = order.get("items", list())
        self.currency = order.get("currency")
        self.shipping = order.get("shipping")
        self.user_comment = order.get("user_comment")
        self.phone_number = order.get("phone_number")
        self.address = order.get("address")
        # self.name = order.get("name")
        # self.is_canceled = order.get("is_canceled")

    def create_fields(self, context=None, obj=None):
        """Same as __init__ method"""
        if obj:
            order = get_obj(orders_table, obj)
        else:
            order = get_obj(orders_table, self._id)
        self.context = context or self.context
        self._id = order.get("_id")
        self.article = str(self._id) if self._id else None
        self.status = order.get("status")  # True or False
        self.bot_id = order.get("bot_id") or context.bot.id
        self.user_id = order.get("user_id")
        self.creation_timestamp = str(
            order.get("creation_timestamp", ".")).split(".")[0]
        self.in_trash = order.get("in_trash")
        self.total_price = order.get("total_price")
        self.items_json = order.get("items", list())
        self.currency = order.get("currency")
        self.shipping = order.get("shipping")
        self.user_comment = order.get("user_comment")
        self.phone_number = order.get("phone_number")
        self.address = order.get("address")
        # self.name = order.get("name")
        # self.is_canceled = order.get("is_canceled")

    @property
    def items(self):
        return [OrderItem(self.context, order_item)
                for order_item in self.items_json]

    @property
    def all_items_exists(self):
        return not any(item.item_exist is False
                       for item in self.items)

    @property
    def id_(self):
        return self._id

    # todo refactor for long order items texts
    def str_order_items(self, currency=None):
        if not currency:
            currency = chatbots_table.find_one(
                {"bot_id": self.context.bot.id})["shop"]["currency"]
        return "\n".join(
            ["<i>{}</i> - <code>{}</code>\n"
             "x{} - <code>{}</code> {}".format(
                item.article,
                item.name,
                item.order_quantity,
                item.price,
                currency)
             # + (item.item_emoji if not self.status else "")
             for item in self.items])

    def update(self, json):
        orders_table.update_one({"_id": self._id}, {"$set": json})
        self.create_fields(self.context, self._id)


class AdminOrder(Order):
    def __init__(self, context, obj: (ObjectId, dict, str) = None):
        super(AdminOrder, self).__init__(context, obj)

    @property
    def user_mention(self):
        mention = ""
        if self.user_id:
            user = self.context.bot.get_chat_member(self.user_id,
                                                    self.user_id).user
            # Create user html mention
            # if user.username:
            #     mention = user_mention(user.username, user.full_name)
            # else:
            mention = user.mention_html()
        return mention

    @property
    def template(self):
        currency = chatbots_table.find_one(
            {"bot_id": self.context.bot.id})["shop"]["currency"]

        template = (
            "\n" + self.context.bot.lang_dict["shop_admin_order_temp"].format(
                self.str_status,
                self.article,
                self.creation_timestamp,
                # self.str_product_status,
                self.user_mention,
                self.phone_number,
                self.user_comment,
                self.total_price,
                currency,
                self.str_order_items(currency)))
        return template

    # @property
    # def str_product_status(self):
    #     if self.status is True:
    #         string = self.context.bot.lang_dict[
    #             "shop_admin_order_status_true"]
    #     elif not self.all_items_exists:
    #         string = self.context.bot.lang_dict[
    #             "shop_admin_some_product_not_exist"]
    #     elif not len(self.items):
    #         string = self.context.bot.lang_dict[
    #             "shop_admin_empty_order"]
    #     else:
    #         string = self.context.bot.lang_dict[
    #             "shop_admin_all_products_exist"]
    #     return string

    @property
    def str_status(self):
        if self.in_trash:
            string = self.context.bot.lang_dict["order_status_canceled"]
        elif self.status:
            string = self.context.bot.lang_dict["shop_admin_order_status_true"]
        else:
            string = self.context.bot.lang_dict["shop_admin_order_status_new"]

        if self.shipping:
            string += self.context.bot.lang_dict["delivery_to"].format(self.address)
        else:
            shop_address = chatbots_table.find_one(
                {"bot_id": self.context.bot.id})["shop"].get("address", "")
            string += self.context.bot.lang_dict["pick_up_from"].format(shop_address)
        return string

    def send_short_template(self, update, context,
                            text="", reply_markup=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template + "\n\n" + text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML
            ))

    def send_full_template(self, update, context, text="", reply_markup=None,
                           item_reply_markup=None):
        # PAGINATION OF ORDER ITEMS
        pagination = Pagination(
            self.items_json, page=context.user_data["item_page"])
        for item in pagination.page_content():
            OrderItem(self.context, item).send_template(
                update, context, reply_markup=item_reply_markup)
        pagination.send_keyboard(update, context,
                                 page_prefix="admin_order_item_pagination")

        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template + "\n\n" + text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML))


class UserOrder(Order):
    def __init__(self, context,  obj: (ObjectId, dict, str) = None):
        super(UserOrder, self).__init__(context, obj)

    @property
    def template(self):
        template = self.context.bot.lang_dict["user_order_temp"].format(
            self.article,
            self.str_status,
            self.total_price,
            self.currency,
            self.phone_number,
            self.user_comment)
        template += "\n\n" + self.str_order_items()
        return template

    @property
    def str_status(self):
        if self.in_trash:
            return self.context.bot.lang_dict["order_status_canceled"]
        if self.status:
            string = self.context.bot.lang_dict["shop_admin_order_status_true"]
        elif self.shipping:
            string = self.context.bot.lang_dict["order_on_way_to"].format(self.address)
        else:
            shop = chatbots_table.find_one({"bot_id": self.context.bot.id})["shop"]
            string = self.context.bot.lang_dict["order_wait_on"].format(shop['address'])
        return string

    def send_full_template(self, update, context, text="", reply_markup=None,
                           item_reply_markup=None):
        # PAGINATION OF ORDER ITEMS
        pagination = Pagination(
            self.items_json, page=context.user_data["item_page"])
        for item in pagination.page_content():
            OrderItem(self.context, item).send_template(
                update, context, reply_markup=item_reply_markup)
        pagination.send_keyboard(update, context,
                                 page_prefix="user_order_item_pagination")

        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template + "\n\n" + text,
                reply_markup=reply_markup,
                parse_mode=ParseMode.HTML))


class OrderItem(Product):
    """For showing and check orders items.
    Works for both user and admin side"""

    def __init__(self, context, order_item):
        # change order_item["product_id"] to order_item["product"]
        # and item data will be taken from order document.
        # Items data that was on the order creation moment
        super(OrderItem, self).__init__(context, order_item["product_id"])
        # Units of item that customer ordered
        self.order_quantity = order_item.get("quantity")
        # Check if the product exist, ready for sale, and quantity is right
        # self.item_exist = (
        #     self._id  # if _id == None - mean find_one() call returns None
        #     and self.on_sale
        #     and (self.unlimited or (self.order_quantity <= self.quantity)))
        # price of the item
        self.item_price = self.price * self.order_quantity

    @property
    def item_exist(self):
        return (self._id  # if _id == None - mean find_one() call returns None
                and self.on_sale
                and (self.unlimited or (self.order_quantity <= self.quantity)))

    def send_template(self, update, context, reply_markup=None):
        currency = chatbots_table.find_one(
            {"bot_id": self.context.bot.id})["shop"]["currency"]

        text = self.context.bot.lang_dict["order_item_template"].format(
            self.article,
            # self.item_exist,
            self.category["name"],
            # quantity,
            self.order_quantity,
            self.item_price,
            currency)
        self.send_short_template(update, context, text, reply_markup)

    # @property
    # def item_emoji(self):
    #     """If product can't be sold returns red sticker, else empty string"""
    #     return " 📛" if not self.item_exist else ""
