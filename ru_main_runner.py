# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging
import telegram.ext as tg
from telegram.ext import CommandHandler, CallbackQueryHandler,RegexHandler

from ru_modules.edit_bot_description import EDIT_BOT_DESCRIPTION_HANDLER
from ru_modules.helper_funcs.admin_login import ADMIN_AUTHENTICATION_HANDLER
from ru_modules.add_menu_buttons import BUTTON_ADD_HANDLER, DELETE_BUTTON_HANDLER, AddCommands
from ru_modules.answer_surveys import ANSWER_SURVEY_HANDLER
from ru_modules.create_donation import CREATE_DONATION_HANDLER
from ru_modules.create_survey import DELETE_SURVEYS_HANDLER, SHOW_SURVEYS_HANDLER, SEND_SURVEYS_HANDLER, \
    CREATE_SURVEY_HANDLER, SurveyHandler
from ru_modules.donations_edit_delete_results import EDIT_DONATION_HANDLER
from ru_modules.helper_funcs.main_runnner_helper import help_button, button_handler, get_help, WelcomeBot, error_callback
from ru_modules.manage_button import BUTTON_EDIT_HANDLER, BUTTON_EDIT_FINISH_HANDLER
from ru_modules.pay_donation import DONATE_HANDLER, DonationBot, HANDLE_SUCCES, HANDLE_PRECHECKOUT
from ru_modules.polls import POLL_HANDLER, SEND_POLLS_HANDLER, BUTTON_HANDLER, DELETE_POLLS_HANDLER, POLLS_RESULTS_HANDLER
from ru_modules.send_donation_request import SEND_DONATION_TO_USERS_HANDLER
from ru_modules.send_message import SEND_MESSAGE_TO_ADMIN_HANDLER, SEND_MESSAGE_TO_USERS_HANDLER, SEE_MESSAGES_HANDLER, \
    SendMessageToUsers
from ru_modules.user_mode import USER_MODE_OFF, USER_MODE_ON

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)


def ru_main(token):
    updater = tg.Updater(token, workers=15)  # TODO check the docs
    dispatcher = updater.dispatcher
    start_handler = CommandHandler("start", WelcomeBot().start)
    help_handler = CommandHandler("help", get_help)
    rex_help_handler = RegexHandler(r"^help$", get_help)
    rex_help_handler2 = RegexHandler(r"^Help$", get_help)

    custom_button_callback_handler = CallbackQueryHandler(button_handler, pattern=r"button_")
    help_callback_handler = CallbackQueryHandler(help_button, pattern=r"help_")

    # dispatcher.add_handler(CallbackQueryHandler(callback=SendMessageToUsers().back, pattern=r"cancel_send_message"))
    # dispatcher.add_handler(CallbackQueryHandler(callback=AddCommands().back,
    #                                             pattern=r"cancel_add_button",
    #                                             pass_user_data=True))
    # dispatcher.add_handler(CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"))
    # dispatcher.add_handler(CallbackQueryHandler(callback=DonationBot().back, pattern=r"cancel_donation_payment"))

    dispatcher.add_handler(custom_button_callback_handler)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(rex_help_handler)
    dispatcher.add_handler(rex_help_handler2)

    dispatcher.add_handler(ADMIN_AUTHENTICATION_HANDLER)

    dispatcher.add_handler(help_callback_handler)
    dispatcher.add_error_handler(error_callback)
    dispatcher.add_handler(EDIT_BOT_DESCRIPTION_HANDLER)
    # ADD_BUTTONS
    dispatcher.add_handler(BUTTON_ADD_HANDLER)
    dispatcher.add_handler(DELETE_BUTTON_HANDLER)
    dispatcher.add_handler(BUTTON_EDIT_HANDLER)
    dispatcher.add_handler(BUTTON_EDIT_FINISH_HANDLER)
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
    dispatcher.add_handler(SEND_MESSAGE_TO_ADMIN_HANDLER)
    dispatcher.add_handler(SEND_MESSAGE_TO_USERS_HANDLER)
    dispatcher.add_handler(SEE_MESSAGES_HANDLER)

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