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
        self.article = order.get("article")
        # TODO admin can change the status of the order- executed or not
        self.status = order.get("status")
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

        self.items = [OrderItem(self.context, order_item)
                      for order_item in self.items_json]
        self.all_items_exists = not any(item.item_exist is False
                                        for item in self.items)
        # Get chat member to get user information
        # because database data can be incorrect
        user = context.bot.get_chat_member(self.user_id, self.user_id).user
        # Create user html mention
        if user.username:
            self.user_mention = user_mention(user.username, user.full_name)
        else:
            self.user_mention = user.mention_html()

    """@property
    def template(self):
        return (
            self.context.bot.lang_dict["shop_admin_order_status_new"]
            if self.status is False
            else (
                     self.context.bot.lang_dict[
                         "shop_admin_order_status_true"])
                 + "\n"
                 + self.context.bot.lang_dict["shop_admin_order_temp"].format(
                self.article,
                self.creation_timestamp,
                self.str_status,
                self.user_mention,
                self.phone_number,
                self.total_price,
                self.str_order_items))"""
    """return (
            self.context.bot.lang_dict["shop_admin_order_status_new"]
            if self.status is False
            else (
                self.context.bot.lang_dict["shop_admin_order_status_true"]) 
                + "\n" 
                 + self.context.bot.lang_dict["shop_admin_order_temp"].format(
                   self.article,
                   self.creation_timestamp,
                   self.str_status,
                   self.user_mention,
                   self.phone_number,
                   self.total_price,
                   self.str_order_items))"""

    """@property
    def str_status(self):
        return self.context.bot.lang_dict["shop_admin_order_status_true"] if self.status is True \
            else self.context.bot.lang_dict["shop_admin_some_product_not_exist"] \
            if not self.all_items_exists \
            else self.context.bot.lang_dict["shop_admin_empty_order"] if not len(self.items) \
            else self.context.bot.lang_dict["shop_admin_all_products_exist"]"""

    # todo refactor for long order items texts
    @property
    def str_order_items(self):
        return "\n".join(
            [f'(article: {item.article} )'
             + (item.item_emoji if not self.status else "")
             for item in self.items])

    """@property
    def single_keyboard(self):
        kb = [[]]
        if self.in_trash:
            kb[0].append(InlineKeyboardButton(
                            text=self.context.bot.lang_dict["shop_admin_restore_btn"],
                            callback_data=f"restore/{self._id}"))
            return InlineKeyboardMarkup(kb)

        if self.status is False:
            if self.all_items_exists and len(self.items):
                kb[0].append(InlineKeyboardButton(
                                text=self.context.bot.lang_dict["shop_admin_to_done_btn"],
                                callback_data=f"to_done/{self._id}"))
            else:
                kb[0].append(InlineKeyboardButton(
                                text=self.context.bot.lang_dict["shop_admin_edit_btn"],
                                callback_data=f"edit/{self._id}"))

            kb[0].append(InlineKeyboardButton(
                            text=self.context.bot.lang_dict["shop_admin_to_trash_btn"],
                            callback_data=f"to_trash/{self._id}"))

        elif self.status is True:
            kb[0].append(InlineKeyboardButton(
                            text=self.context.bot.lang_dict["shop_admin_cancel_btn"],
                            callback_data=f"cancel_order/{self._id}"))
        return InlineKeyboardMarkup(kb)"""

    """def send_short_template(self, update, context, kb=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template,
                reply_markup=kb if kb else self.single_keyboard,
                parse_mode=ParseMode.MARKDOWN))"""

    def send_full_template(self, update, context, text, kb, delete_kb=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template,
                parse_mode=ParseMode.MARKDOWN))

        # PAGINATION OF ORDER ITEMS
        # all_data = [item for item in self.items]
        pagination = Pagination(
            self.items_json, per_page=3,
            page=context.user_data["item_page"])
        for item in pagination.page_content():
            OrderItem(self.context, item).send_template(
                update, context, delete_kb=delete_kb)
        pagination.send_keyboard(update, context)
        context.user_data["to_delete"].append(
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text, reply_markup=kb,
                                     parse_mode=ParseMode.MARKDOWN))

    def update(self, json=None):
        orders_table.update_one({"_id": self._id}, {"$set": json})
        self.__init__(self._id)

    # TODO CODE FROM SHOP-API - REFORMAT
    """def change_status(self, args):
        if args["new_status"] is not None:
            if args["new_status"] is False:
                self.move_to_new()
            if args["new_status"] is True:
                self.move_to_done()
        if args["new_trash_status"] is not None:
            self.change_delete_status(args["new_trash_status"])

    def move_to_new(self):
        if self.status is False:
            # todo 400
            abort(400, "Order already new")
        for order_item in self.items:
            order_item.product_item.current_quantity += 1
            if len(order_item.product_item.product.sizes_list()) > 0 \
                    and order_item.product_item.product.sold_out is True:
                order_item.product_item.product.sold_out = False
        self.status = False
        db.session.add(self)
        db.session.commit()

    def move_to_done(self):
        if self.status is True:
            # todo 400
            abort(400, "Order already done")
        order_errors = list()
        for order_item in self.items:
            if not order_item.exist():
                order_errors.append(order_item.item_error())
            else:
                order_item.product_item.current_quantity -= 1
                if len(order_item.product_item.product.sizes_list()) == 0:
                    order_item.product_item.product.sold_out = True
        if order_errors:
            # todo 400
            abort(400, order_errors)
        else:
            self.status = True
            db.session.add(self)
            db.session.commit()

    def add_items(self, items):
        order_errors = list()
        # price = self.price if self.price else 0
        self.price = self.price or 0
        for item in items:
            product_size = ProductSize.query.join(Size, Product).filter(
                (Size.name == item["size"]) &
                (Product.article == item["article"])).first()
            if not product_size or product_size.current_quantity == 0:
                order_errors.append(self.item_error(item["article"]))
            else:
                # product = Product.query.get_or_404(item["article"])
                # self.products.append(product)
                order_item = OrderItem(product_item=product_size,
                                       order=self)
                # product_size.size.orders.append(order_item)
                # self.items.append(order_item)
                self.price += product_size.product.price \
                    if product_size.product.discount_price == 0 \
                    else product_size.product.discount_price
        if order_errors:
            abort(409, order_errors)
        # if not order_errors:
            # self.price = price
            # self.price = sum(item.product_item.product.price
            #                  if item.product_item.product.discount_price==0
            #                  else item.product_item.product.discount_price
            #                  for item in self.items)
        #     return True
        # else:
        #     return order_errors

    def remove_item(self, id_to_remove):
        item = self.items.filter_by(id=id_to_remove).first()
        if item:
            self.items.remove(item)
            db.session.add(self)
            db.session.commit()
        else:
            abort(400, f"There are not item with given id -> {id_to_remove}")

    def change_delete_status(self, new_delete_status):
        if self.status is False:
            self.in_trash = new_delete_status
            # if new_delete_status is True:
            #     self.in_trash = True
            # elif new_delete_status is False:
            #     self.in_trash = False
            db.session.add(self)
            db.session.commit()
        elif self.status is True:
            # todo 400
            abort(400, "Order is done and can't be deleted")
"""

    """def remove_item(self, item_id):
        resp = requests.post(
            f"{conf['API_URL']}/order/{self._id}/edit_items",
            json={"id_to_remove": int(item_id)})
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException

    def add_item(self, item: dict):
        resp = requests.post(
            f"{conf['API_URL']}/order/{self._id}/edit_items",
            json={"to_add": [item]})
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException

    def change_status(self, json):
        resp = requests.patch(
            f"{conf['API_URL']}/order/{self._id}",
            json=json)
        if resp.status_code == 200:
            self.__init__(resp.json())
        else:
            raise RequestException"""

    def refresh(self):
        self.__init__(self._id)


class AdminOrder(Order):
    def __init__(self, context, obj: (ObjectId, dict, str) = None):
        super(AdminOrder, self).__init__(context, obj)

    @property
    def template(self):
        if self.status:
            template = self.context.bot.lang_dict[
                "shop_admin_order_status_true"]
        else:
            template = self.context.bot.lang_dict[
                "shop_admin_order_status_new"]

        template += (
            "\n" + self.context.bot.lang_dict["shop_admin_order_temp"].format(
                self.article,
                self.creation_timestamp,
                self.str_status,
                self.user_mention,
                self.phone_number,
                self.total_price,
                self.str_order_items))
        return template

    @property
    def str_status(self):
        return self.context.bot.lang_dict[
            "shop_admin_order_status_true"] if self.status is True \
            else self.context.bot.lang_dict[
            "shop_admin_some_product_not_exist"] \
            if not self.all_items_exists \
            else self.context.bot.lang_dict[
            "shop_admin_empty_order"] if not len(self.items) \
            else self.context.bot.lang_dict["shop_admin_all_products_exist"]

    @property
    def single_keyboard(self):
        kb = [[]]
        if self.in_trash:
            kb[0].append(InlineKeyboardButton(
                text=self.context.bot.lang_dict["shop_admin_restore_btn"],
                callback_data=f"restore/{self._id}"))
            return InlineKeyboardMarkup(kb)

        if self.status is False:
            if self.all_items_exists and len(self.items):
                kb[0].append(InlineKeyboardButton(
                    text=self.context.bot.lang_dict["shop_admin_to_done_btn"],
                    callback_data=f"to_done/{self._id}"))
            else:
                kb[0].append(InlineKeyboardButton(
                    text=self.context.bot.lang_dict["shop_admin_edit_btn"],
                    callback_data=f"edit/{self._id}"))

            kb[0].append(InlineKeyboardButton(
                text=self.context.bot.lang_dict["shop_admin_to_trash_btn"],
                callback_data=f"to_trash/{self._id}"))

        elif self.status is True:
            kb[0].append(InlineKeyboardButton(
                text=self.context.bot.lang_dict["shop_admin_cancel_btn"],
                callback_data=f"cancel_order/{self._id}"))
        return InlineKeyboardMarkup(kb)

    def send_short_template(self, update, context, reply_markup=None):
        context.user_data["to_delete"].append(
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.template,
                reply_markup=reply_markup if reply_markup
                else self.single_keyboard,
                parse_mode=ParseMode.HTML))


class UserOrder(Order):
    def __init__(self, context,  obj: (ObjectId, dict, str) = None):
        super(UserOrder, self).__init__(context, obj)

    @property
    def template(self):
        template = ("\n*Order article:* `{}`"
                    "\n*Order status:* {}"
                    "\n*Order price:* `{}` {}"
                    "\n*Your phone number:* `{}`"
                    "\n*Your comment:*: `{}`").format(
            self.article,
            self.str_status,
            self.total_price,
            self.currency,
            self.phone_number,
            self.user_comment)

        if self.shipping:
            template += f"\n🚚 *Delivery to* `{self.address}`"
        else:
            shop = chatbots_table.find_one(
                {"bot_id": self.context.bot.id})["shop"]
            template += f"\n🖐 *Pick up from* `{shop['address']}`"
        return template

    @property
    def str_status(self):
        if self.status:
            string = "DONE"
        else:
            if self.shipping:
                string = f"On my way to `{self.address}`"
            else:
                shop = chatbots_table.find_one(
                    {"bot_id": self.context.bot.id})["shop"]
                string = f"Your order wait for you `{shop['address']}`"
        return string


class OrderItem(Product):
    """For Showing Orders Items - Need to change for not cloth shop"""
    def __init__(self, context, order_item):
        super(OrderItem, self).__init__(context, order_item["product"])
        self.item_obj = order_item
        self.item_exist = True  # TODO

    def send_template(self, update, context, delete_kb=None):
        if delete_kb:
            delete_kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton(
                    context.bot.lang_dict["shop_admin_cancel_btn"],
                    callback_data=f"remove_item/{self.item_obj['id']}")]])

        text = context.bot.lang_dict["shop_admin_product_temp_for_order_item"].format(
            self.article,
            self.category["name"], self.price,
            f" {self.item_emoji}")
        # self.send_admin_short_template(update, context, text, delete_kb)

    @property
    def item_emoji(self):
        return " 📛" if not self.item_exist else ""
