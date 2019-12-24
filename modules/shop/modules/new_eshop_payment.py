#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bson import ObjectId
from telegram import LabeledPrice, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (MessageHandler, Filters, PreCheckoutQueryHandler,
                          ConversationHandler, CallbackQueryHandler)
import logging
import datetime
# Enable logging
from database import purchases_table, products_table, chatbots_table, orders_table
from helper_funcs.misc import get_obj

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ORDER_DESCRIPTION = 1


class PurchaseBot(object):  # TODO finish this

    def start_purchase(self, update, context):
        button_callback_data = update.callback_query.data

        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id, )
        product_id = ObjectId(button_callback_data.replace(
                                                        "buy/", ""))
        purchase_request = get_obj(table=products_table, obj=product_id)
        context.bot.send_message(update.callback_query.message.chat.id, "Pay:{} {}".format(
            str(purchase_request.price), str(purchase_request.currency)))
        title = purchase_request.name
        description = purchase_request.description

        if purchase_request.online_payment:
            shop = chatbots_table.find_one({"bot_id": context.bot.id})["shop"]
            payload = "Purchase"
            start_parameter = "shop-payment"
            currency = purchase_request.currency
            prices = [LabeledPrice(title, int(float(purchase_request.price)*100))]
            # TODO stupid as fuck (i know), change later
            context.bot.sendInvoice(update.callback_query.message.chat_id, title, description, payload,
                                    shop["payment_token"], start_parameter, currency, prices,
                                    need_name=True, need_phone_number=True,
                                    need_email=True, need_shipping_address=purchase_request.shipping, is_flexible=True
                                    )
            context.bot.send_message(update.callback_query.message.chat.id,
                                     text=context.bot.lang_dict["back_text"],
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                                callback_data="help_back")]]))
            logger.info("User {} on bot {} requested a purchase".format(
                update.effective_user.first_name, context.bot.first_name))

            return ConversationHandler.END
        else:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     text="Tell the seller some details about your order",
                                     reply_markup=InlineKeyboardMarkup(
                                         [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                                callback_data="help_back")]]))
            return ORDER_DESCRIPTION

    def nopayment_order_finish(self, update, context):
        # self.context = context
        # self._id = order.get("_id")
        # self.bot_id = context.bot.id
        # self.status = order.get("status")
        # self.timestamp = order.get("creation_timestamp", ".").split(".")[0]
        # self.name = order.get("name")
        # self.phone_number = order.get("phone_number")
        # self.price = order.get("price")
        # self.in_trash = order.get("in_trash")
        # self.items_json = order.get("items")
        # self.items = [OrderItem(order_item) for order_item in self.items_json]
        # self.all_items_exists = not any(item.item_exist is False
        #                                 for item in self.items)
        orders_table.insert_one({"status": "Pending",  # TODO ask about the status
                                 "bot_id": context.bot.id,
                                 "product_id": context.user_data["product_id"],
                                 "description": update.message.text,
                                 "timestamp": datetime.datetime.now(),
                                 "name": context.user_data["name"],
                                 "phone_number": context.user_data["phone_number"],
                                 "price": context.user_data["price"],
                                 "in_trash": False,
                                 })
        return ConversationHandler.END

    def precheckout_callback(self, update, context):
        # query = update.callback_query
        # if query:
        #     if query.data == "help_back":
        #         return ConversationHandler.END
        query = update.pre_checkout_query

        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)
        return ConversationHandler.END

    # finally, after contacting to the purchase provider...
    def successful_payment_callback(self, update, context):
        # TODO add counting of purchases and prepare for callback_query
        # do something after successful receive of purchase?
        buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="help_back")]]
        # TODO add a back function with deleting of old message
        markup = InlineKeyboardMarkup(buttons)
        context.user_data = dict()
        context.user_data["status"] = "Paid"
        context.user_data['timestamp_paid'] = datetime.datetime.now()
        context.user_data["amount"] = update.message.successful_payment.total_amount
        context.user_data["chat_id"] = update.message.chat_id
        context.user_data["bot_id"] = context.bot.id

        purchases_table.insert_one(context.user_data)
        update.message.reply_text(context.bot.lang_dict["thank_purchase"], markup=markup)
        context.user_data.clear()
        return ConversationHandler.END


PURCHASE_HANDLER = CallbackQueryHandler(callback=PurchaseBot().start_purchase,
                                        pattern=r'buy')

HANDLE_PRECHECKOUT = PreCheckoutQueryHandler(PurchaseBot().precheckout_callback)

HANDLE_SUCCES = MessageHandler(Filters.successful_payment,
                               PurchaseBot().successful_payment_callback)
