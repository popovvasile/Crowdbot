#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os

import sys
import time
from queue import Queue
from threading import Thread

import telegram
from flask import Flask
from flask import request as flask_req

from telegram import Bot, Update
from telegram.error import Unauthorized
from telegram.ext import messagequeue as mq, Dispatcher
from telegram.ext import (CommandHandler, CallbackQueryHandler, MessageHandler, Filters)
from telegram.utils.request import Request

from database import chatbots_table
from logs import logger
from helper_funcs.misc import dismiss, update_user_unsubs
from helper_funcs.helper import (help_button, button_handler, get_help, WelcomeBot,
                                 back_from_button_handler, back_to_modules, error_callback,
                                 return_to_menu)

# SETTINGS
from modules.settings.language_switch import LANG_MENU, SET_LANG
from modules.settings.menu_description import EDIT_BOT_DESCRIPTION_HANDLER, EDIT_PICTURE_HANDLER
from modules.settings.button_manage import (
    BUTTON_ADD_HANDLER, DELETE_BUTTON_HANDLER, LINK_BUTTON_ADD_HANDLER,
    CREATE_BUTTON_CHOOSE, BUTTONS_MENU, ONE_BUTTON_MENU, BACK_TO_BUTTONS_MENU,
    BACK_TO_ONE_BUTTON_MENU, CHANGE_BUTTON_NAME_HANDLER, EDIT_BUTTON_CONTENT_HANDLER,
    EDIT_BUTTON_LINK_HANDLER)

from modules.settings.user_mode import USER_MODE_OFF, USER_MODE_ON
from modules.settings.admins import ADMINS_LIST_HANDLER
from modules.settings.notification import NOTIFICATION_MENU, NOTIFICATION_EDIT


# USERS AND MESSAGES
from modules.users.messages_admin import SEND_MESSAGE_ONLY_TO_ADMINS_HANDLER
from modules.users.messages_donators import SEND_MESSAGE_TO_DONATORS_HANDLER
from modules.users.messages import (
    SEND_MESSAGE_TO_ADMIN_HANDLER, SEND_MESSAGE_TO_USERS_HANDLER,
    SEE_MESSAGES_HANDLER, ANSWER_TO_MESSAGE_HANDLER, DELETE_MESSAGES_HANDLER,
    SEE_MESSAGES_FINISH_HANDLER, BACK_TO_INBOX, MESSAGES_MENU,
    BACK_TO_INBOX_VIEW_MESSAGE, FINISH_BLOCK_ANONIM_MESSAGING,
    CONFIRM_BLOCK_ANONIM_MESSAGING, UNBLOCK_ANONIM_MESSAGING,
    CONFIRM_BLOCK_MESSAGING_FROM_INBOX, FINISH_BLOCK_MESSAGING_FROM_INBOX,
    FINISH_UNBLOCK_MESSAGING_FROM_INBOX, SHOW_MESSAGE_HANDLER,
    HIDE_MESSAGE_HANDLER, BACK_TO_MESSAGES_MENU, DELETE_MESSAGES_MENU_HANDLER)
from modules.users.users import (
    USERS_LIST_HANDLER, USER_MESSAGES_LIST, ANSWER_TO_MESSAGE_FROM_USER_LIST_HANDLER,
    CONFIRM_BLOCK_MESSAGING, FINISH_BLOCK_MESSAGING, FINISH_UNBLOCK_MESSAGING, BACK_TO_USERS_LIST,
    VIEW_USER_MESSAGE, BACK_TO_OPEN_MESSAGE, CONFIRM_BAN_USER, FINISH_BAN_USER, FINISH_UNBUN_USER,
    SEND_MESSAGE_TO_USER_HANDLER, BACK_TO_USER_MESSAGES_LIST, DELETE_USER_MESSAGE_HANDLER,
    OPEN_USER_HANDLER, BACK_TO_OPEN_USER, SEARCH_USER)

from modules.statistic.user_statistic import USERS_STATISTIC_HANDLER

# PAYMENTS
from modules.shop.admin_side.shop_config import (
    CONFIGS_SHOP_GENERAL, CHANGE_SHOP_CONFIG, EDIT_SHOP_HANDLER)

# SHOP ADMIN SIDE
from modules.shop.admin_side.welcome import (
    START_SHOP_HANDLER, BACK_TO_MAIN_MENU_HANDLER, Welcome)
from modules.shop.admin_side.adding_product import ADD_PRODUCT_HANDLER
from modules.shop.admin_side.orders import ORDERS_HANDLER
from modules.shop.admin_side.products import PRODUCTS_HANDLER
from modules.shop.admin_side.trash import (TRASH_START, ORDERS_TRASH,
                                           PRODUCTS_TRASH)
from modules.shop.admin_side.categories import (
    ADD_CATEGORY_HANDLER, CATEGORIES_HANDLER, EDIT_CATEGORIES_HANDLER,
    RENAME_CATEGORY_HANDLER, DELETE_CATEGORY_HANDLER, BACK_TO_CATEGORIES_MENU)
from modules.shop.admin_side.eshop_enable_disable import CREATE_SHOP_HANDLER

# SHOP USER SIDE
from modules.shop.user_side.order_creator import OFFLINE_PURCHASE_HANDLER
from modules.shop.user_side.online_payment import HANDLE_SUCCES, HANDLE_PRECHECKOUT
from modules.shop.user_side.products import (
    USERS_PRODUCTS_LIST_HANDLER, ADD_TO_CART, REMOVE_FROM_CART, PRODUCTS_CATEGORIES,
    BACK_TO_CATEGORIES, VIEW_PRODUCT, BACK_TO_CUSTOMER_SHOP, SHOP_CONTACTS, MOVE_TO_CART)
from modules.shop.user_side.cart import (
    CART, REMOVE_FROM_CART_LIST, CHANGE_QUANTITY, BACK_TO_CART, MAKE_ORDER, VIEW_CART_PRODUCT)
from modules.shop.user_side.orders import (
    USERS_ORDERS_LIST_HANDLER, USER_ORDER_ITEMS_PAGINATION, BACK_TO_USER_ORDERS,
    ORDER_PAYMENT_MENU)


class MQBot(telegram.bot.Bot):
    """A subclass of Bot which delegates send method handling to MQ"""
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        """Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments

        @mq.queuedmessage is a decorator to be used with :attr:`telegram.Bot` send* methods.
        """
        return super(MQBot, self).send_message(*args, **kwargs)

    @mq.queuedmessage
    def send_audio(self, *args, **kwargs):
        return super(MQBot, self).send_audio(*args, **kwargs)

    @mq.queuedmessage
    def send_voice(self, *args, **kwargs):
        return super(MQBot, self).send_voice(*args, **kwargs)

    @mq.queuedmessage
    def send_video(self, *args, **kwargs):
        return super(MQBot, self).send_video(*args, **kwargs)

    @mq.queuedmessage
    def send_document(self, *args, **kwargs):
        return super(MQBot, self).send_document(*args, **kwargs)

    @mq.queuedmessage
    def send_photo(self, *args, **kwargs):
        return super(MQBot, self).send_photo(*args, **kwargs)

    @mq.queuedmessage
    def send_animation(self, *args, **kwargs):
        return super(MQBot, self).send_animation(*args, **kwargs)

    @mq.queuedmessage
    def send_sticker(self, *args, **kwargs):
        return super(MQBot, self).send_sticker(*args, **kwargs)


# def catch_unauthorized(func):
#     def wrapper(token, lang):
#         try:
#             return func(token, lang)
#         except Unauthorized:
#             chatbots_table.update({"token": token},
#                                   {"$set": {"active": False,
#                                             # "deactivation_time": datetime.now()
#                                             }})
#             sys.exit()
#     return wrapper
#
#
# @catch_unauthorized
def create_dispatchers():
    megadict = {}
    app = Flask(__name__)
    for doc in chatbots_table.find({"active": True,
                                    "wehook": False}):

        token = doc["token"]
        request = Request(con_pool_size=104)
        q = mq.MessageQueue(all_burst_limit=25, all_time_limit_ms=1200)
        # bot_obj = MQBot(token, request=request, mqueue=q)
        bot_obj = Bot(token, request=request)
        update_queue = Queue()
        filename = 'logs/{}.log'.format(bot_obj.name)
        open(filename, "w+")
        hdlr = logging.FileHandler(filename)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger.setLevel(logging.ERROR)

        with open('languages.json') as f:
            lang_dicts = json.load(f)
        if doc["lang"] == "ENG":
            bot_obj.lang_dict = lang_dicts["ENG"]
        else:
            bot_obj.lang_dict = lang_dicts["RUS"]

        # job = updater.job_queue
        # job.run_repeating(update_user_unsubs, interval=3600*24, first=0)

        dispatcher = Dispatcher(bot_obj, update_queue, use_context=True)
        start_handler = CommandHandler("start", WelcomeBot().start)
        help_handler = CommandHandler("help", get_help)

        custom_button_callback_handler = CallbackQueryHandler(
            callback=button_handler,
            pattern=r"button_")

        custom_button_back_callback_handler = CallbackQueryHandler(
            callback=back_from_button_handler,
            pattern=r"back_from_button")

        help_callback_handler = CallbackQueryHandler(callback=help_button,
                                                     pattern=r"help_")

        back_to_modules_handler = CallbackQueryHandler(pattern=r"back_to_module",
                                                       callback=back_to_modules)
        dismiss_handler = CallbackQueryHandler(pattern="dismiss",
                                               callback=dismiss)
        dispatcher.add_handler(dismiss_handler)
        # TODO priority is very important!!!!!!!!!!!!!!!!!!!!
        dispatcher.add_handler(EDIT_BOT_DESCRIPTION_HANDLER)
        dispatcher.add_handler(EDIT_PICTURE_HANDLER)

        #  SHOP USER SIDE
        dispatcher.add_handler(EDIT_SHOP_HANDLER)
        # dispatcher.add_handler(ONLINE_PURCHASE_HANDLER)
        dispatcher.add_handler(OFFLINE_PURCHASE_HANDLER)
        dispatcher.add_handler(BACK_TO_CART)
        dispatcher.add_handler(USERS_PRODUCTS_LIST_HANDLER)
        dispatcher.add_handler(ADD_TO_CART)
        dispatcher.add_handler(REMOVE_FROM_CART)
        dispatcher.add_handler(CART)
        dispatcher.add_handler(MAKE_ORDER)
        dispatcher.add_handler(PRODUCTS_CATEGORIES)
        dispatcher.add_handler(BACK_TO_CATEGORIES)
        dispatcher.add_handler(REMOVE_FROM_CART_LIST)
        dispatcher.add_handler(CHANGE_QUANTITY)
        dispatcher.add_handler(USERS_ORDERS_LIST_HANDLER)
        dispatcher.add_handler(VIEW_CART_PRODUCT)
        dispatcher.add_handler(VIEW_PRODUCT)
        dispatcher.add_handler(MOVE_TO_CART)
        dispatcher.add_handler(BACK_TO_CUSTOMER_SHOP)
        dispatcher.add_handler(USER_ORDER_ITEMS_PAGINATION)
        dispatcher.add_handler(ORDER_PAYMENT_MENU)
        dispatcher.add_handler(BACK_TO_USER_ORDERS)
        dispatcher.add_handler(SHOP_CONTACTS)

        #  SHOP ADMIN SIDE
        # dispatcher.add_handler(product_handler_han)
        dispatcher.add_handler(CHANGE_SHOP_CONFIG)
        dispatcher.add_handler(CONFIGS_SHOP_GENERAL)
        dispatcher.add_handler(CREATE_SHOP_HANDLER)
        dispatcher.add_handler(START_SHOP_HANDLER)
        dispatcher.add_handler(ORDERS_TRASH)
        dispatcher.add_handler(PRODUCTS_TRASH)
        dispatcher.add_handler(ADD_PRODUCT_HANDLER)
        dispatcher.add_handler(ORDERS_HANDLER)
        dispatcher.add_handler(PRODUCTS_HANDLER)
        dispatcher.add_handler(TRASH_START)
        # dispatcher.add_handler(USERS_ORDERS_HANDLER)
        dispatcher.add_handler(ADD_CATEGORY_HANDLER)
        dispatcher.add_handler(CATEGORIES_HANDLER)
        dispatcher.add_handler(EDIT_CATEGORIES_HANDLER)
        dispatcher.add_handler(RENAME_CATEGORY_HANDLER)
        dispatcher.add_handler(RENAME_CATEGORY_HANDLER)
        dispatcher.add_handler(DELETE_CATEGORY_HANDLER)
        dispatcher.add_handler(BACK_TO_CATEGORIES_MENU)
        dispatcher.add_handler(HANDLE_SUCCES)
        dispatcher.add_handler(HANDLE_PRECHECKOUT)

        # BUTTONS
        dispatcher.add_handler(ONE_BUTTON_MENU)
        dispatcher.add_handler(CHANGE_BUTTON_NAME_HANDLER)
        dispatcher.add_handler(EDIT_BUTTON_CONTENT_HANDLER)
        dispatcher.add_handler(EDIT_BUTTON_LINK_HANDLER)
        dispatcher.add_handler(BUTTONS_MENU)
        dispatcher.add_handler(CREATE_BUTTON_CHOOSE)
        dispatcher.add_handler(LINK_BUTTON_ADD_HANDLER)
        dispatcher.add_handler(BUTTON_ADD_HANDLER)
        dispatcher.add_handler(DELETE_BUTTON_HANDLER)
        dispatcher.add_handler(BACK_TO_BUTTONS_MENU)
        dispatcher.add_handler(BACK_TO_ONE_BUTTON_MENU)
        dispatcher.add_handler(LANG_MENU)
        dispatcher.add_handler(SET_LANG)
        # USER MODE
        dispatcher.add_handler(USER_MODE_ON)
        dispatcher.add_handler(USER_MODE_OFF)

        # USERS
        dispatcher.add_handler(USERS_LIST_HANDLER)
        dispatcher.add_handler(CONFIRM_BLOCK_MESSAGING)
        dispatcher.add_handler(FINISH_BLOCK_MESSAGING)
        dispatcher.add_handler(FINISH_UNBLOCK_MESSAGING)
        dispatcher.add_handler(USER_MESSAGES_LIST)
        dispatcher.add_handler(VIEW_USER_MESSAGE)
        dispatcher.add_handler(ANSWER_TO_MESSAGE_FROM_USER_LIST_HANDLER)
        dispatcher.add_handler(BACK_TO_OPEN_MESSAGE)
        dispatcher.add_handler(FINISH_BAN_USER)
        dispatcher.add_handler(CONFIRM_BAN_USER)
        dispatcher.add_handler(FINISH_UNBUN_USER)
        dispatcher.add_handler(SEND_MESSAGE_TO_USER_HANDLER)
        dispatcher.add_handler(SEARCH_USER)
        dispatcher.add_handler(BACK_TO_USERS_LIST)
        dispatcher.add_handler(BACK_TO_USER_MESSAGES_LIST)
        dispatcher.add_handler(DELETE_USER_MESSAGE_HANDLER)
        dispatcher.add_handler(OPEN_USER_HANDLER)
        dispatcher.add_handler(BACK_TO_OPEN_USER)

        # STATISTIC
        dispatcher.add_handler(USERS_STATISTIC_HANDLER)

        # ADMINS
        dispatcher.add_handler(ADMINS_LIST_HANDLER)
        # dispatcher.add_handler(ADD_ADMIN_HANDLER)
        dispatcher.add_handler(NOTIFICATION_MENU)
        dispatcher.add_handler(NOTIFICATION_EDIT)

        # MESSAGES
        dispatcher.add_handler(MESSAGES_MENU)
        dispatcher.add_handler(ANSWER_TO_MESSAGE_HANDLER)
        dispatcher.add_handler(DELETE_MESSAGES_HANDLER)
        dispatcher.add_handler(SEND_MESSAGE_TO_ADMIN_HANDLER)
        dispatcher.add_handler(SEND_MESSAGE_TO_USERS_HANDLER)
        dispatcher.add_handler(SEE_MESSAGES_HANDLER)
        dispatcher.add_handler(SEE_MESSAGES_FINISH_HANDLER)
        dispatcher.add_handler(SEND_MESSAGE_ONLY_TO_ADMINS_HANDLER)
        dispatcher.add_handler(SEND_MESSAGE_TO_DONATORS_HANDLER)
        dispatcher.add_handler(FINISH_BLOCK_ANONIM_MESSAGING)
        dispatcher.add_handler(CONFIRM_BLOCK_ANONIM_MESSAGING)
        dispatcher.add_handler(BACK_TO_INBOX_VIEW_MESSAGE)
        dispatcher.add_handler(BACK_TO_INBOX)
        dispatcher.add_handler(UNBLOCK_ANONIM_MESSAGING)
        dispatcher.add_handler(CONFIRM_BLOCK_MESSAGING_FROM_INBOX)
        dispatcher.add_handler(FINISH_BLOCK_MESSAGING_FROM_INBOX)
        dispatcher.add_handler(FINISH_UNBLOCK_MESSAGING_FROM_INBOX)
        dispatcher.add_handler(SHOW_MESSAGE_HANDLER)
        dispatcher.add_handler(HIDE_MESSAGE_HANDLER)
        dispatcher.add_handler(BACK_TO_MESSAGES_MENU)
        dispatcher.add_handler(DELETE_MESSAGES_MENU_HANDLER)


        dispatcher.add_handler(custom_button_back_callback_handler)
        dispatcher.add_handler(custom_button_callback_handler)
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(help_handler)

        dispatcher.add_handler(back_to_modules_handler)

        dispatcher.add_handler(CallbackQueryHandler(Welcome.back_to_main_menu,
                                                    pattern=r"_back"))

        dispatcher.add_handler(BACK_TO_MAIN_MENU_HANDLER)

        dispatcher.add_handler(help_callback_handler)

        if os.environ['SHOP_PRODUCTION'] == "1":
            dispatcher.add_error_handler(error_callback)
        dispatcher.add_handler(CallbackQueryHandler(get_help,
                                                    pattern=r"back"))
        dispatcher.add_handler(CallbackQueryHandler(get_help,
                                                    pattern=r"cancel"))
        rex_help_handler = MessageHandler(Filters.regex(r"^((?!@).)*$"), return_to_menu)
        dispatcher.add_handler(rex_help_handler)

        # WEBHOOK SETTINGS
        megadict.update({token: {
            "queue": update_queue,
            "dispatcher": dispatcher,
            "bot": bot_obj
        }})
        try:
            s = bot_obj.set_webhook(url='https://64.227.14.144:8443/' + token,
                                    certificate=open('cert.pem', 'rb'))
            logger.info('webhook setup ok')
            chatbots_table.update({"token": doc["token"]},
                                  {"$set": {"webhook": True,
                                            # "deactivation_time": datetime.now()
                                            }})
        except Unauthorized:
            chatbots_table.update({"token": doc["token"]},
                                  {"$set": {"active": False,
                                            # "deactivation_time": datetime.now()
                                            }})
            logger.info('webhook setup ok')
            continue
        if s:
            print(s)
            logger.info('webhook setup ok')
        else:
            print(s)
            logger.info('webhook setup failed')
            continue

        def webhook():
            if flask_req.headers.get('content-type') == 'application/json':
                dp_dict = megadict[flask_req.path[1:]]
                update = Update.de_json(flask_req.get_json(force=True), dp_dict["bot"])
                logger.info('Update received! ' + str(update))
                dp_dict["queue"].put(update)
            return 'OK'
        app.add_url_rule(rule='/{}'.format(token),
                         endpoint=token,
                         view_func=webhook,
                         methods=['POST'])

        time.sleep(0.1)  # To avoid flood and give the script time to start all bots, one by one
    for token in megadict.values():
        dp = token["dispatcher"]
        thread = Thread(target=dp.start, name=dp.bot.username)
        thread.start()
    return app


# webhook = main()
#
#
# webhook.run(host='0.0.0.0',
#             port=8443,
#             ssl_context=('cert.pem', 'private.key'))
