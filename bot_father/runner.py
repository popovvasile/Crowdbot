# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram.ext import CommandHandler, Updater
from bot_father.main.support_bot import \
    START_SUPPORT_HANDLER, SEND_REPORT_HANDLER, \
    USER_REPORTS_HANDLER, ADMIN_REPORTS_HANDLER, Welcome

from bot_father.main.bot_father import \
    START_HANDLER, CREATE_BOT_HANDLER, MANAGE_BOT_HANDLER, \
    LANG_MENU, SET_LANG, BACK_TO_MAIN_MENU_HANDLER


def main():
    updater = Updater("836123673:AAE6AyfFCcRxjHZZhJHtdE8mKt8WNfgRm5Q")  # @crowd_supportbot
    dp = updater.dispatcher

    dp.add_handler(START_HANDLER)

    dp.add_handler(CREATE_BOT_HANDLER)
    dp.add_handler(MANAGE_BOT_HANDLER)
    dp.add_handler(LANG_MENU)
    dp.add_handler(SET_LANG)

    dp.add_handler(START_SUPPORT_HANDLER)
    dp.add_handler(CommandHandler('admin', Welcome().test_admin, pass_user_data=True))
    # dp.add_handler(CONTACTS_HANDLER)
    dp.add_handler(SEND_REPORT_HANDLER)
    dp.add_handler(USER_REPORTS_HANDLER)
    dp.add_handler(ADMIN_REPORTS_HANDLER)

    dp.add_handler(BACK_TO_MAIN_MENU_HANDLER)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
