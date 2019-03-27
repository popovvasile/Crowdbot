
import logging
import telegram.ext as tg
from telegram.ext import CommandHandler, CallbackQueryHandler,RegexHandler
from admin_login import ADMIN_AUTHENTICATION_HANDLER
from modules import ALL_MODULES
from modules.add_menu_buttons import BUTTON_ADD_HANDLER, DELETE_BUTTON_HANDLER
from modules.answer_surveys import ANSWER_SURVEY_HANDLER
from modules.create_donation import CREATE_DONATION_HANDLER
from modules.create_survey import DELETE_SURVEYS_HANDLER, SHOW_SURVEYS_HANDLER, SEND_SURVEYS_HANDLER, \
    CREATE_SURVEY_HANDLER
from modules.helper_funcs.main_runnner_helper import help_button, button_handler, get_help, WelcomeBot, error_callback, \
    ADMIN_HELPABLE, VISITOR_HELPABLE
from modules.pay_donation import DONATE_HANDLER
from modules.send_message import SEND_MESSAGE_TO_ADMIN_HANDLER, SEND_MESSAGE_TO_USERS_HANDLER, SEE_MESSAGES_HANDLER
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)

LOGGER = logging.getLogger(__name__)


def main(token):
    updater = tg.Updater(token, workers=8)
    dispatcher = updater.dispatcher
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
    dispatcher.add_error_handler(error_callback)

    # POLLS
    # dispatcher.add_handler(POLL_HANDLER)
    # dispatcher.add_handler(SEND_POLLS_HANDLER)
    # dispatcher.add_handler(BUTTON_HANDLER)  # TODO fix this to use another callback
    # dispatcher.add_handler(DELETE_POLLS_HANDLER)

    # ADD_BUTTONS
    dispatcher.add_handler(BUTTON_ADD_HANDLER)
    dispatcher.add_handler(DELETE_BUTTON_HANDLER)

    # DONATIONS
    dispatcher.add_handler(CREATE_DONATION_HANDLER)
    dispatcher.add_handler(DONATE_HANDLER)

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

    LOGGER.info("Using long polling.")
    updater.start_polling(timeout=15, read_latency=4)

    updater.idle()


# if __name__ == '__main__':
#     LOGGER.info("Successfully loaded modules: " + str(ALL_MODULES))
#     main()
