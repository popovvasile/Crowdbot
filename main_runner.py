#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import telegram.ext as tg
from telegram.ext import CommandHandler, CallbackQueryHandler,RegexHandler

from helper_funcs.admin_login import ADMIN_AUTHENTICATION_HANDLER
from modules.eshop.echop_customer import PURCHASE_HANDLER
from modules.eshop.eshop_admin import PRODUCT_ADD_HANDLER, DELETE_PRODUCT_HANDLER, PRODUCT_EDIT_HANDLER, \
    PRODUCT_EDIT_FINISH_HANDLER, PRODUCT_ADD_FINISH_HANDLER, DELETE_PRODUCT_CONTENT_HANDLER, PRODUCTS_MENU_HANDLER
from modules.groups.groups import MY_GROUPS_HANDLER, REMOVE_GROUP_HANDLER, SEND_POST_TO_GROUP_HANDLER, ADD_GROUP_HANLDER
from modules.groups.groups_polls_surveys_donate import SEND_POLL_TO_GROUP_HANDLER, SEND_SURVEY_TO_GROUP_HANDLER, \
    SEND_DONATION_TO_GROUP_HANDLER
from modules.settings.menu_description import EDIT_BOT_DESCRIPTION_HANDLER
from modules.settings.menu_buttons import BUTTON_ADD_HANDLER, DELETE_BUTTON_HANDLER, LINK_BUTTON_ADD_HANDLER, \
    CREATE_BUTTON_CHOOSE
from modules.users.messages_admin import SEND_MESSAGE_ONLY_TO_ADMINS_HANDLER
from modules.users.messages_donators import SEND_MESSAGE_TO_DONATORS_HANDLER
from modules.surveys.surveys_answer import ANSWER_SURVEY_HANDLER
from modules.donations.donation_enable import CREATE_DONATION_HANDLER
from modules.surveys.surveys_create import DELETE_SURVEYS_HANDLER, SHOW_SURVEYS_HANDLER, SEND_SURVEYS_HANDLER, \
    CREATE_SURVEY_HANDLER
from modules.donations.donations_edit_delete_results import EDIT_DONATION_HANDLER
from helper_funcs.main_runnner_helper import help_button, button_handler, get_help, WelcomeBot, \
    back_from_button_handler, product_handler
from modules.settings.manage_button import BUTTON_EDIT_HANDLER, BUTTON_EDIT_FINISH_HANDLER, DELETE_CONTENT_HANDLER, \
    BUTTON_ADD_FINISH_HANDLER, back_from_edit_button_handler
from modules.donations.donation_payment import DONATE_HANDLER, HANDLE_SUCCES, HANDLE_PRECHECKOUT
from modules.pollbot.polls import POLL_HANDLER, SEND_POLLS_HANDLER, BUTTON_HANDLER, DELETE_POLLS_HANDLER, POLLS_RESULTS_HANDLER
from modules.donations.donation_send_promotion import SEND_DONATION_TO_USERS_HANDLER
from modules.users.messages import SEND_MESSAGE_TO_ADMIN_HANDLER, SEND_MESSAGE_TO_USERS_HANDLER, SEE_MESSAGES_HANDLER, \
    ANSWER_TO_MESSAGE_HANDLER, DELETE_MESSAGES_HANDLER, SEE_MESSAGES_FINISH_HANDLER, SEE_MESSAGES_BACK_HANDLER, \
    SEE_MESSAGES_FINISH_BACK_HANDLER, BLOCK_USER, BLOCKED_USERS_LIST, UNBLOCK_USER
from modules.settings.user_mode import USER_MODE_OFF, USER_MODE_ON


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)


def main(token, port):
    updater = tg.Updater(token)  # TODO check the docs
    dispatcher = updater.dispatcher
    # dispatcher.add_error_handler(error_callback)
    start_handler = CommandHandler("start", WelcomeBot().start)
    help_handler = CommandHandler("help", get_help)
    rex_help_handler = RegexHandler(r"^((?!@).)*$", get_help)
    product_handler_han = CallbackQueryHandler(product_handler, pattern=r"product_", pass_user_data=True)

    custom_button_callback_handler = CallbackQueryHandler(button_handler, pattern=r"button_", pass_user_data=True)
    custom_button_back_callback_handler = CallbackQueryHandler(back_from_button_handler,
                                                               pattern=r"back_from_button", pass_user_data=True)
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_")

    dispatcher.add_handler(EDIT_BOT_DESCRIPTION_HANDLER)
    # ADD_BUTTONS
    dispatcher.add_handler(CREATE_BUTTON_CHOOSE)
    dispatcher.add_handler(LINK_BUTTON_ADD_HANDLER)
    dispatcher.add_handler(BUTTON_ADD_HANDLER)
    dispatcher.add_handler(DELETE_BUTTON_HANDLER)
    dispatcher.add_handler(BUTTON_EDIT_HANDLER)
    dispatcher.add_handler(BUTTON_EDIT_FINISH_HANDLER)
    dispatcher.add_handler(DELETE_CONTENT_HANDLER)
    dispatcher.add_handler(BUTTON_ADD_FINISH_HANDLER)
    # USER MODE
    dispatcher.add_handler(USER_MODE_ON)
    dispatcher.add_handler(USER_MODE_OFF)

    # DONATIONS
    dispatcher.add_handler(CREATE_DONATION_HANDLER)
    dispatcher.add_handler(DONATE_HANDLER)
    dispatcher.add_handler(HANDLE_SUCCES)
    dispatcher.add_handler(HANDLE_PRECHECKOUT)
    dispatcher.add_handler(EDIT_DONATION_HANDLER)
    dispatcher.add_handler(SEND_DONATION_TO_USERS_HANDLER)
    # MESSAGES
    dispatcher.add_handler(SEE_MESSAGES_FINISH_BACK_HANDLER)
    dispatcher.add_handler(SEE_MESSAGES_BACK_HANDLER)
    dispatcher.add_handler(ANSWER_TO_MESSAGE_HANDLER)
    dispatcher.add_handler(DELETE_MESSAGES_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_ADMIN_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_USERS_HANDLER)
    dispatcher.add_handler(SEE_MESSAGES_HANDLER)
    dispatcher.add_handler(SEE_MESSAGES_FINISH_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_ONLY_TO_ADMINS_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_DONATORS_HANDLER)
    dispatcher.add_handler(BLOCK_USER)
    dispatcher.add_handler(BLOCKED_USERS_LIST)
    dispatcher.add_handler(UNBLOCK_USER)
    # dispatcher.add_handler(ADD_MESSAGE_CATEGORY_HANDLER)
    # dispatcher.add_handler(DELETE_MESSAGE_CATEGORY_HANDLER)
    # dispatcher.add_handler(MESSAGE_CATEGORY_HANDLER)

    # SURVEYS
    dispatcher.add_handler(ANSWER_SURVEY_HANDLER)
    dispatcher.add_handler(SHOW_SURVEYS_HANDLER)
    dispatcher.add_handler(SEND_SURVEYS_HANDLER)
    dispatcher.add_handler(CREATE_SURVEY_HANDLER)
    dispatcher.add_handler(DELETE_SURVEYS_HANDLER)

    # POLLS
    dispatcher.add_handler(POLL_HANDLER)
    dispatcher.add_handler(SEND_POLLS_HANDLER)
    dispatcher.add_handler(BUTTON_HANDLER)
    dispatcher.add_handler(DELETE_POLLS_HANDLER)
    dispatcher.add_handler(POLLS_RESULTS_HANDLER)

    # GROUPS
    dispatcher.add_handler(MY_GROUPS_HANDLER)
    dispatcher.add_handler(REMOVE_GROUP_HANDLER)
    dispatcher.add_handler(SEND_POST_TO_GROUP_HANDLER)
    dispatcher.add_handler(SEND_POLL_TO_GROUP_HANDLER)
    dispatcher.add_handler(SEND_SURVEY_TO_GROUP_HANDLER)
    dispatcher.add_handler(SEND_DONATION_TO_GROUP_HANDLER)
    dispatcher.add_handler(ADD_GROUP_HANLDER)
    # PRODUCTS
    dispatcher.add_handler(PRODUCT_ADD_HANDLER)
    dispatcher.add_handler(DELETE_PRODUCT_HANDLER)
    dispatcher.add_handler(PRODUCT_EDIT_HANDLER)
    dispatcher.add_handler(PRODUCT_EDIT_FINISH_HANDLER)
    dispatcher.add_handler(PRODUCT_ADD_FINISH_HANDLER)
    dispatcher.add_handler(DELETE_PRODUCT_CONTENT_HANDLER)
    dispatcher.add_handler(PRODUCTS_MENU_HANDLER)
    dispatcher.add_handler(PURCHASE_HANDLER)
    dispatcher.add_handler(product_handler_han)


    dispatcher.add_handler(custom_button_back_callback_handler)
    dispatcher.add_handler(custom_button_callback_handler)
    dispatcher.add_handler(back_from_edit_button_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)

    dispatcher.add_handler(ADMIN_AUTHENTICATION_HANDLER)  # TODO priority is very important!!!!!!!!!!!!!!!!!!!!
    dispatcher.add_handler(rex_help_handler)

    dispatcher.add_handler(help_callback_handler)

    # error_help_callback_handler = CallbackQueryHandler(get_help, pattern=r"error_back")
    # dispatcher.add_handler(error_help_callback_handler)

    LOGGER.info("Using long polling.")
    # updater.start_webhook(listen='0.0.0.0',
    #                       port=port,
    #                       url_path=token,
    #                       key='private.key',
    #                       cert='cert.pem',
    #                       webhook_url='https://104.248.82.166:{}/'.format(port) + token)
    print(token)
    updater.start_polling(timeout=60, read_latency=60, clean=True, bootstrap_retries=5)

    updater.idle()
#
# if __name__ == '__main__':
#     main("633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg")
