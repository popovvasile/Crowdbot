#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import logging
import os
import re

from telegram.utils import request
import telegram.ext as tg
from telegram import Bot
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from logs import logger
from helper_funcs.misc import dismiss
from helper_funcs.helper import (help_button, button_handler, get_help, WelcomeBot,
                                 back_from_button_handler, back_to_modules, error_callback)

# CHANNELS
# from modules.chanells.channels import (MY_CHANNELS_HANDLER, ADD_CHANNEL_HANDLER,
#                                        REMOVE_CHANNEL_HANDLER, SEND_POST_HANDLER, CHANELLS_MENU)
# from modules.chanells.channels_polls_surveys_donate import (
#     SEND_POLL_TO_CHANNEL_HANDLER, SEND_SURVEY_TO_CHANNEL_HANDLER,
#     SEND_DONATION_TO_CHANNEL_HANDLER)
#
# GROUPS
# from modules.groups.groups import (
#     MY_GROUPS_HANDLER, REMOVE_GROUP_HANDLER, SEND_POST_TO_GROUP_HANDLER, ADD_GROUP_HANLDER,
#     GROUPS_MENU)
# from modules.groups.groups_polls_surveys_donate import (
#     SEND_POLL_TO_GROUP_HANDLER, SEND_SURVEY_TO_GROUP_HANDLER, SEND_DONATION_TO_GROUP_HANDLER)

# SETTINGS
from modules.settings.menu_description import EDIT_BOT_DESCRIPTION_HANDLER
from modules.settings.settings import (
    BUTTON_ADD_HANDLER, DELETE_BUTTON_HANDLER, LINK_BUTTON_ADD_HANDLER,
    CREATE_BUTTON_CHOOSE, BUTTONS_MENU, ONE_BUTTON_MENU, BACK_TO_BUTTONS_MENU,
    BACK_TO_ONE_BUTTON_MENU, CHANGE_BUTTON_NAME_HANDLER, EDIT_BUTTON_CONTENT_HANDLER,
    EDIT_BUTTON_LINK_HANDLER)
# from modules.settings.manage_button import (
#     BUTTON_EDIT_HANDLER, BUTTON_EDIT_FINISH_HANDLER, DELETE_CONTENT_HANDLER,
#     BUTTON_ADD_FINISH_HANDLER, back_from_edit_button_handler)
from modules.settings.user_mode import USER_MODE_OFF, USER_MODE_ON
from modules.settings.admins import ADMINS_LIST_HANDLER
from modules.settings.notification import NOTIFICATION_MENU, NOTIFICATION_EDIT
# from modules.donations.donation_payment import (DONATE_HANDLER, HANDLE_SUCCES,
#                                                 HANDLE_PRECHECKOUT)

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

# STATISTIC
# from modules.statistic.statistic_main import (
#     STATISTIC_MAIN_MENU, BACK_TO_STATISTIC_MAIN)
from modules.statistic.user_statistic import USERS_STATISTIC_HANDLER
# from modules.statistic.donation_statistic import DONATION_STATISTIC_HANDLER

# SURVEYS
from modules.surveys.surveys_answer import ANSWER_SURVEY_HANDLER
from modules.surveys.surveys_create import (
    DELETE_SURVEYS_HANDLER, SHOW_SURVEYS_HANDLER, SEND_SURVEYS_HANDLER,
    CREATE_SURVEY_HANDLER, SURVEYS_MENU, SEND_SURVEYS_MENU_HANDLER)

# PAYMENTS
from modules.payments.payments_config import (
    # EDIT_DONATION_HANDLER, PAYMENTS_CONFIG_KEYBOARD, CHANGE_DONATIONS_CONFIG,
    # CONFIGS_DONATIONS_GENERAL,
    CONFIGS_SHOP_GENERAL, CHANGE_SHOP_CONFIG, EDIT_SHOP_HANDLER)
# from modules.donations.donation_enable_disable import (
#     CREATE_DONATION_HANDLER, DONATIONS_MENU)



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
    RENAME_CATEGORY_HANDLER, DELETE_CATEGORY_HANDLER)
from modules.shop.admin_side.eshop_enable_disable import CREATE_SHOP_HANDLER

# SHOP USER SIDE
from modules.shop.user_side.order_creator import OFFLINE_PURCHASE_HANDLER
from modules.shop.user_side.online_payment import HANDLE_SUCCES, HANDLE_PRECHECKOUT
from modules.shop.user_side.products import (
    USERS_PRODUCTS_LIST_HANDLER, ADD_TO_CART, REMOVE_FROM_CART, PRODUCTS_CATEGORIES,
    BACK_TO_CATEGORIES, VIEW_PRODUCT, BACK_TO_CUSTOMER_SHOP, SHOP_CONTACTS)
from modules.shop.user_side.cart import (
    CART, REMOVE_FROM_CART_LIST, CHANGE_QUANTITY, BACK_TO_CART, MAKE_ORDER, VIEW_CART_PRODUCT)
from modules.shop.user_side.orders import (
    USERS_ORDERS_LIST_HANDLER, USER_ORDER_ITEMS_PAGINATION, BACK_TO_USER_ORDERS,
    ORDER_PAYMENT_MENU)




def main(token, lang):

    # https://github.com/python-telegram-bot/python-telegram-bot/issues/787
    req = request.Request(con_pool_size=8)
    bot_obj = Bot(token=token, request=req)
    filename = 'logs/{}.log'.format(bot_obj.name)
    open(filename, "w+")
    hdlr = logging.FileHandler(filename)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.INFO)

    with open('languages.json') as f:
        lang_dicts = json.load(f)
    if lang == "ENG":
        Bot.lang_dict = lang_dicts["ENG"]
    else:
        Bot.lang_dict = lang_dicts["RUS"]
    updater = tg.Updater(use_context=True, bot=bot_obj)
    dispatcher = updater.dispatcher
    # os.environ['SHOP_PRODUCTION'] is True --- returns False, dunno why
    # if os.environ['SHOP_PRODUCTION'] == "1":
    #     dispatcher.add_error_handler(error_callback)
    start_handler = CommandHandler("start", WelcomeBot().start)
    help_handler = CommandHandler("help", get_help)
    # product_handler_han = CallbackQueryHandler(
    #   product_handler, pattern=r"product_")  # TODO think if to use this one

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
    # dispatcher.add_handler(BUTTON_EDIT_HANDLER)
    # dispatcher.add_handler(BUTTON_EDIT_FINISH_HANDLER)
    # dispatcher.add_handler(DELETE_CONTENT_HANDLER)
    # dispatcher.add_handler(BUTTON_ADD_FINISH_HANDLER)
    dispatcher.add_handler(BACK_TO_BUTTONS_MENU)
    dispatcher.add_handler(BACK_TO_ONE_BUTTON_MENU)

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
    # dispatcher.add_handler(STATISTIC_MAIN_MENU)
    # dispatcher.add_handler(BACK_TO_STATISTIC_MAIN)
    # dispatcher.add_handler(DONATION_STATISTIC_HANDLER)
    dispatcher.add_handler(USERS_STATISTIC_HANDLER)

    # ADMINS
    dispatcher.add_handler(ADMINS_LIST_HANDLER)
    # dispatcher.add_handler(ADD_ADMIN_HANDLER)
    dispatcher.add_handler(NOTIFICATION_MENU)
    dispatcher.add_handler(NOTIFICATION_EDIT)

    # DONATIONS
    # dispatcher.add_handler(CREATE_DONATION_HANDLER)
    # dispatcher.add_handler(DONATE_HANDLER)
    # dispatcher.add_handler(HANDLE_SUCCES)
    # dispatcher.add_handler(HANDLE_PRECHECKOUT)
    # dispatcher.add_handler(EDIT_DONATION_HANDLER)
    # dispatcher.add_handler(SEND_DONATION_TO_USERS_HANDLER)
    # dispatcher.add_handler(CHANGE_DONATIONS_CONFIG)
    # dispatcher.add_handler(PAYMENTS_CONFIG_KEYBOARD)
    # dispatcher.add_handler(CONFIGS_DONATIONS_GENERAL)
    # dispatcher.add_handler(DONATIONS_MENU)

    # MESSAGES
    dispatcher.add_handler(MESSAGES_MENU)
    # dispatcher.add_handler(SEE_MESSAGES_FINISH_BACK_HANDLER)
    # dispatcher.add_handler(SEE_MESSAGES_BACK_HANDLER)
    dispatcher.add_handler(ANSWER_TO_MESSAGE_HANDLER)
    dispatcher.add_handler(DELETE_MESSAGES_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_ADMIN_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_USERS_HANDLER)
    dispatcher.add_handler(SEE_MESSAGES_HANDLER)
    dispatcher.add_handler(SEE_MESSAGES_FINISH_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_ONLY_TO_ADMINS_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_DONATORS_HANDLER)
    # dispatcher.add_handler(BLOCK_USER)
    # dispatcher.add_handler(BLOCKED_USERS_LIST)
    # dispatcher.add_handler(UNBLOCK_USER)
    # dispatcher.add_handler(SEE_MESSAGES_PAGINATION_HANDLER)
    # dispatcher.add_handler(ADD_MESSAGE_CATEGORY_HANDLER)
    # dispatcher.add_handler(DELETE_MESSAGE_CATEGORY_HANDLER)
    # dispatcher.add_handler(MESSAGE_CATEGORY_HANDLER)
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

    # SURVEYS
    dispatcher.add_handler(SURVEYS_MENU)
    dispatcher.add_handler(ANSWER_SURVEY_HANDLER)
    dispatcher.add_handler(SHOW_SURVEYS_HANDLER)
    dispatcher.add_handler(SEND_SURVEYS_HANDLER)
    dispatcher.add_handler(CREATE_SURVEY_HANDLER)
    dispatcher.add_handler(DELETE_SURVEYS_HANDLER)
    dispatcher.add_handler(SEND_SURVEYS_MENU_HANDLER)

    # POLLS
    # dispatcher.add_handler(POLLS_MENU)
    # dispatcher.add_handler(POLL_HANDLER)
    # dispatcher.add_handler(SEND_POLLS_HANDLER)
    # dispatcher.add_handler(BUTTON_HANDLER)
    # dispatcher.add_handler(DELETE_POLLS_HANDLER)
    # dispatcher.add_handler(POLLS_RESULTS_HANDLER)
    # dispatcher.add_handler(POLLS_SEND_MENU)

    # GROUPS
    # dispatcher.add_handler(GROUPS_MENU)
    # dispatcher.add_handler(MY_GROUPS_HANDLER)
    # dispatcher.add_handler(REMOVE_GROUP_HANDLER)
    # dispatcher.add_handler(SEND_POST_TO_GROUP_HANDLER)
    # dispatcher.add_handler(SEND_POLL_TO_GROUP_HANDLER)
    # dispatcher.add_handler(SEND_SURVEY_TO_GROUP_HANDLER)
    # dispatcher.add_handler(SEND_DONATION_TO_GROUP_HANDLER)
    # dispatcher.add_handler(ADD_GROUP_HANLDER)

    # CHANNELS
    # dispatcher.add_handler(CHANELLS_MENU)
    # dispatcher.add_handler(MY_CHANNELS_HANDLER)
    # dispatcher.add_handler(ADD_CHANNEL_HANDLER)
    # dispatcher.add_handler(REMOVE_CHANNEL_HANDLER)
    # dispatcher.add_handler(SEND_POST_HANDLER)
    # dispatcher.add_handler(SEND_POLL_TO_CHANNEL_HANDLER)
    # dispatcher.add_handler(SEND_SURVEY_TO_CHANNEL_HANDLER)
    # dispatcher.add_handler(SEND_DONATION_TO_CHANNEL_HANDLER)

    dispatcher.add_handler(custom_button_back_callback_handler)
    dispatcher.add_handler(custom_button_callback_handler)
    # dispatcher.add_handler(back_from_edit_button_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)

    dispatcher.add_handler(back_to_modules_handler)

    dispatcher.add_handler(CallbackQueryHandler(Welcome.back_to_main_menu,
                                                pattern=r"back_"))
    dispatcher.add_handler(BACK_TO_MAIN_MENU_HANDLER)

    dispatcher.add_handler(help_callback_handler)

    # rex_help_handler = MessageHandler(Filters.regex(r"^((?!@).)*$"), get_help)
    # dispatcher.add_handler(rex_help_handler)
    # rex_help_handler = MessageHandler(Filters.regex(re.compile(r"help", re.IGNORECASE))|
    #                                   Filters.regex(re.compile(r"menu", re.IGNORECASE))|
    #                                   Filters.regex(re.compile(r"hello", re.IGNORECASE))|
    #                                   Filters.regex(re.compile(r"hi", re.IGNORECASE))|
    #                                   Filters.regex(re.compile(r"але", re.IGNORECASE))|
    #                                   Filters.regex(re.compile(r"меню", re.IGNORECASE))|
    #                                   Filters.regex(re.compile(r"помощь", re.IGNORECASE)),
    #                                   get_help)
    #
    # dispatcher.add_handler(rex_help_handler)
    logger.info("Using long polling.")
    # updater.start_webhook(listen='0.0.0.0',
    #                       port=port,
    #                       url_path=token,
    #                       key='private.key',
    #                       cert='cert.pem',
    #                       webhook_url='https://104.248.82.166:{}/'.format(port) + token)
    updater.start_polling(timeout=60, read_latency=60, clean=True, bootstrap_retries=5)

    updater.idle()
#
# if __name__ == '__main__':
#     main("633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg", "ENG")
