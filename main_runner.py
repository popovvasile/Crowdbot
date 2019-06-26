#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import telegram.ext as tg
from telegram.ext import CommandHandler, CallbackQueryHandler,RegexHandler

from modules.channels_polls_surveys_donate import SEND_SURVEY_TO_CHANNEL_HANDLER, SEND_POLL_TO_CHANNEL_HANDLER
from modules.menu_description import EDIT_BOT_DESCRIPTION_HANDLER
from modules.helper_funcs.admin_login import ADMIN_AUTHENTICATION_HANDLER
from modules.menu_buttons import BUTTON_ADD_HANDLER, DELETE_BUTTON_HANDLER
from modules.surveys_answer import ANSWER_SURVEY_HANDLER
from modules.donation_enable import CREATE_DONATION_HANDLER
from modules.surveys_create import DELETE_SURVEYS_HANDLER, SHOW_SURVEYS_HANDLER, SEND_SURVEYS_HANDLER, \
    CREATE_SURVEY_HANDLER
from modules.donations_edit_delete_results import EDIT_DONATION_HANDLER
from modules.helper_funcs.main_runnner_helper import help_button, button_handler, get_help, WelcomeBot, error_callback
from modules.manage_button import BUTTON_EDIT_HANDLER, BUTTON_EDIT_FINISH_HANDLER, DELETE_CONTENT_HANDLER, \
    BUTTON_ADD_FINISH_HANDLER
from modules.donation_payment import DONATE_HANDLER, HANDLE_SUCCES, HANDLE_PRECHECKOUT
from modules.polls import POLL_HANDLER, SEND_POLLS_HANDLER, BUTTON_HANDLER, DELETE_POLLS_HANDLER, POLLS_RESULTS_HANDLER
from modules.donation_send_promotion import SEND_DONATION_TO_USERS_HANDLER
from modules.messages import SEND_MESSAGE_TO_ADMIN_HANDLER, SEND_MESSAGE_TO_USERS_HANDLER, SEE_MESSAGES_HANDLER, \
    ANSWER_TO_MESSAGE_HANDLER, DELETE_MESSAGES_HANDLER, SEE_MESSAGES_FINISH_HANDLER, ADD_MESSAGE_CATEGORY_HANDLER, \
    DELETE_MESSAGE_CATEGORY_HANDLER, MESSAGE_CATEGORY_HANDLER
from modules.user_mode import USER_MODE_OFF, USER_MODE_ON
from modules.channels import MY_CHANNELS_HANDLER, ADD_CHANNEL_HANDLER, REMOVE_CHANNEL_HANDLER,  SEND_POST_HANDLER
from modules.users import USER_CATEGORY_HANDLER, DELETE_USER_CATEGORY_HANDLER, USER_CHOOSES_CATEGORY_HANDLER, \
    ADD_USER_CATEGORY_HANDLER, SEND_USER_QUESTION_HANDLER

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)


def main(token):
    updater = tg.Updater(token)  # TODO check the docs
    dispatcher = updater.dispatcher
    dispatcher.add_error_handler(error_callback)
    start_handler = CommandHandler("start", WelcomeBot().start)
    help_handler = CommandHandler("help", get_help)
    rex_help_handler = RegexHandler(r"^help$", get_help)
    rex_help_handler2 = RegexHandler(r"^Help$", get_help)

    custom_button_callback_handler = CallbackQueryHandler(button_handler, pattern=r"button_")
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_")
    dispatcher.add_handler(custom_button_callback_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(rex_help_handler)
    dispatcher.add_handler(rex_help_handler2)

    dispatcher.add_handler(ADMIN_AUTHENTICATION_HANDLER)

    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_handler(EDIT_BOT_DESCRIPTION_HANDLER)
    # ADD_BUTTONS
    dispatcher.add_handler(BUTTON_ADD_HANDLER)
    dispatcher.add_handler(DELETE_BUTTON_HANDLER)
    dispatcher.add_handler(BUTTON_EDIT_HANDLER)
    dispatcher.add_handler(BUTTON_EDIT_FINISH_HANDLER)
    dispatcher.add_handler(DELETE_CONTENT_HANDLER)
    dispatcher.add_handler(BUTTON_ADD_FINISH_HANDLER)
    # USER MODE
    dispatcher.add_handler(USER_MODE_ON)
    dispatcher.add_handler(USER_MODE_OFF)

    # USERS
    dispatcher.add_handler(USER_CATEGORY_HANDLER)
    dispatcher.add_handler(DELETE_USER_CATEGORY_HANDLER)
    dispatcher.add_handler(USER_CHOOSES_CATEGORY_HANDLER)
    dispatcher.add_handler(ADD_USER_CATEGORY_HANDLER)
    dispatcher.add_handler(SEND_USER_QUESTION_HANDLER)
    # DONATIONS
    dispatcher.add_handler(CREATE_DONATION_HANDLER)
    dispatcher.add_handler(DONATE_HANDLER)
    dispatcher.add_handler(HANDLE_SUCCES)
    dispatcher.add_handler(HANDLE_PRECHECKOUT)
    dispatcher.add_handler(EDIT_DONATION_HANDLER)
    dispatcher.add_handler(SEND_DONATION_TO_USERS_HANDLER)
    # MESSAGES
    dispatcher.add_handler(ANSWER_TO_MESSAGE_HANDLER)
    dispatcher.add_handler(DELETE_MESSAGES_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_ADMIN_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_USERS_HANDLER)
    dispatcher.add_handler(SEE_MESSAGES_HANDLER)
    dispatcher.add_handler(SEE_MESSAGES_FINISH_HANDLER)
    dispatcher.add_handler(ADD_MESSAGE_CATEGORY_HANDLER)
    dispatcher.add_handler(DELETE_MESSAGE_CATEGORY_HANDLER)
    dispatcher.add_handler(MESSAGE_CATEGORY_HANDLER)

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

    # CHANNELS
    dispatcher.add_handler(MY_CHANNELS_HANDLER)
    dispatcher.add_handler(ADD_CHANNEL_HANDLER)
    dispatcher.add_handler(REMOVE_CHANNEL_HANDLER)
    dispatcher.add_handler(SEND_POST_HANDLER)
    dispatcher.add_handler(SEND_POLL_TO_CHANNEL_HANDLER)
    dispatcher.add_handler(SEND_SURVEY_TO_CHANNEL_HANDLER)
    LOGGER.info("Using long polling.")
    # updater.start_webhook(listen='0.0.0.0',
    #                       port=8443,
    #                       url_path=token,
    #                       key='private.key',
    #                       cert='cert.pem',
    #                       webhook_url='https://142.93.109.14:8443/' + token)
    print(token)
    updater.start_polling(timeout=15, read_latency=4)

    updater.idle()

#
# if __name__ == '__main__':
#     main("633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg")
