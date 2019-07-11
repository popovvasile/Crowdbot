from bot_father.db import bot_father_users_table
strings_dict = {
    'ENG': dict(
        UNKNOWN_COMMAND=" Oops. I don't know. Press 🚑 /help to view all commands",
        ADD_ADMINS="⭐️ Add admin",
        DELETE_ADMIN="❌ Delete admin",
        DELETE="❌ Delete Bot",
        BACK="🔙 Back",
        CREATE_NEW_BOT="🤖 Create a new bot",
        # MY_BOT ="📋 List of bots",
        # MANAGE_MY_BOTS="🔧 Settings",
        # GET_BOTS_INFO="ℹ️ Information about bot",
        ADMIN="Admin",
        REMOVED="Removed",
        # IS_DELETED='Deleted',
        # BOT='Bot',
        TOKEN_REQUEST="How to create a bot and get a token: https://telegra.ph/Gajd-Sozdat-chatbota-06-03"
                        " ❗️ IMPORTANT: the bot should not be connected to other chatbot platforms"
                        "Insert token:",
        WRONG_TOKEN="Oops. Wrong token. Try again",
        SELECT_ADMIN_TO_REMOVE="Choose the admin that you want to remove",
        # UNKNOWN_ACTION=" Oops. I don't know. Press 🚑 /help to view all commands ",
        UNKNOWN_CHAT="First create a bot, press 🤖 /create",
        WRONG_EMAIL="Oops. Wrong E-mail. Try typing again.",
        NO_BOTS="First create a bot, press 🤖 /create ",
        RETURNED_TO_MAIN_MENU="Back to the menu",
        # COMPLETE_CREATION_REQUEST=" You're not done with the last bot yet. Finish it or press ❌ /cancel to continue.",
        # CANCEL_CREATION_REQUEST=" To finish press ❌ /cancel ",
        WELCOME_MESSAGE_REQUEST="Enter a welcome message for your users✌️. Don't worry, it can be changed later",
        OCCUPATION_REQUEST="What do you do? To skip click /next",
        NEXT_EMAIL_REQUEST="Enter E-Mail addresses of the other admins. "
                           "They'll get a one-time password that they have to send to your bot."
                           "If you are already ready — press 'continue' ",
        YOU_ARE_THE_ONLY_ADMIN="You are the only admin of this bot",
        COMMANDS='/new – 🤖 Create a bot'
        '/mybots – 📋 Get list of bots'
        '/Info – ℹ️ Information about the bot'
        '/cancel – ❌ cancle the command'
        '/Settings – 🔧 Manage bots'
        '/help – 🚑 List of all bot commands'
        'Got problems? Connect us ➡️ @CrowdbotSupport, will reply soon ',
        ADMIN_EMAILS_REQUEST="Enter your E-mail",
        CHOOSE_ACTION='Select action',
        WELCOME=' Welcome to CrowdRobot! 🎉 Here you can create a chatbot 🤖 in 2 minutes, '
                'instead of an expensive website. Communicate with your audience, conduct surveys, ' 
                'publish content and collect donations ',
        NO_CONTEXT=" Press 🤖 /create to start. ",
        BOT_READY="Admins are added, the bot is ready ✅"
                  "Go to your bot({}) and click /start",
        SELECT_BOT_FOR_INFO="Choose bot",
        SELECT_BOT_TO_MANAGE="Choose bot",
        ALL_BOTS_COMPLETED=" There is no exit. Create bot🤖 /create",
        BOT_DELETED='Bot({}) is deleted 🤕',
        CANCEL_CREATION="🛑 Cancel",
        en='🇬🇧English',
        ru='🇷🇺Русский',
        terms_of_use_menu='By clicking continue you agree with terms of use. Read it before continue',
        terms_of_use_in_text='Вы должны ознакомиться с условиями использования сервиса CrowdRobot и его ограничениями.' \
                            '\nНастоящее пользовательское соглашение заключается между мной и CrowdRobot. ' \
                            '\n- Да, я согласен с тем, CrowdRobot не несёт ответственности за любые действия ' \
                            'или бездействия пользователей и администраторов чатботов.' \
                            '\n- Да, при использовании CrowdRobot, я обязуюсь не нарушать нормы международного права и нормы ' \
                            'законодательства страны моего проживания.' \
                            '\n- Да, до третьего числа каждого месяца, я обязуюсь переводить абонентскую плату в ' \
                            'размере 12,99 евро, через сервис PayPal в пользу CrowdRobot. В случае неуплаты ' \
                            'в установленный срок, CrowdRobot приостановит работу вашего бота' \
                            '\n- CrowdRoBot оставляет за собой право вносить изменения в данное соглашение' \
                            '\n- CrowdRobot обязуется не передавать персональные данные клиентов третьим лицам.' \
                            '\n*Я-администратор(владелец) созданного при помощи Crowdrobot чатбота' \
                            '\n*Чатбот-виртуальный, автоматизированный собеседник на платформе Telegram' \
                            '\n*CrowdRobot – программа в Telegram. Создаёт чатботов с следующими функциями: ' \
                            'Обмен платежами, проведение опросов, размещение легального контента, обмен сообщениями.' \
                            '\n*CrowdRobot подключается к API той платёжной системы, которую выбрал администратор' \
                            '\nчатбота. Все платежи записываются в базу данных.' \
                            '\n*CrowdRobot выступает посредником между администратором чатбота и платёжной системой, ' \
                            'без доступа на изменение суммы платежа. Деньги переводятся с банковского счёта' \
                            '\nпользователя чатбота на на счёт администратора в выбранной им платёжной системе.' \
                            '\n(У платёжки с админом тоже есть договор, который это регулирует)' \
                            '\n✅Да, я согласен с условиями использования сервиса CrowdRoBot ',
        token_already_exist='You already got bot with this token -> {}. '
                            'If you want to create new one send me new token that '
                            'you can take from @BotFather',

        manage_bots_button='Manage my bots',
        contact_button='Contact with Crowd Team',
        terms_as_text_button='Send as text',
        terms_as_doc_button='Send as .docx file',
        agree_with_terms_button='I have read. Continue',
        continue_button_text='Continue',
        add_button='Add',

        your_bots='\nYour bots: \n{}',
        bot_template='\nName: {}' 
                     '\nAdmins: {}'
                     '\nCreation date: {}',
        confirm_delete_bot="Are u sure u want to delete bot({})?",
        ENTER_NEW_ADMIN_EMAIL="Enter E-Mail addresses of the admins. "
                              "They'll get a one-time password that they have to send to your bot."
                              "If you are already ready — press 'Add' ",
        admins_added='Admins successfully added',
        only_one_admin="There are only one admin and it is you",
        add_already_exist_admin='Admin => {} already exist. ',
        confirm_delete_admin='Are u sure u want to delete {} from {} admins?',
        admin_removed_success='{} have been removed successfully',
        language_menu='Please select language you want to use.',
        # SENDING REPORT PART
        start_message="Hello. I'm support bot.\n" 
                        "U can send message to developers - click 'Send message'",
        choose_category="Choose what your message about, or send a message "
                        "that describe in few words what your report about",
        contacts='Here is contacts:\n' 
                 '@keikoobro\n' 
                 '@vasile_python\n'
                 '@Mykyto\n',
        enter_message="Please describe your problem and we will try to solve this issue. U can send photo, audio, " 
                        "voice messages and other",
        admin_give_answer="What do u want to answer?",

        enter_message_2="Send a new message if u want to add more information to your report or press '✅ Done'",
        admin_give_answer_2="Send a new message if u want to add more information to your answer or press '✅ Done'",

        report_contains='Your report contains: ',
        admin_give_answer_3='Your answer contains: ',

        enter_message_4='User report contains:',

        confirm_message='Are you sure u want to send your report?',
        confirm_answer='Are you sure u want to send your answer?',
        confirm_delete='Are u sure u want to delete report. You can restore it from trash anytime',

        finish_send_report="Thank you! We will review your this chatbot asap. You can find answer in 'Inbox messages', "
                             "We will send u notification when answer is ready",
        finish_send_answer='Reply successfully sent, User user received notification',
        finish_move_to_trash='Report successfully moved to trash. You can restore it from trash anytime',

        blink_success_send_report="Success Send, Thank you for report",
        blink_success_send_answer="Success Send Answer",

        my_reports_menu="*Here is the list of your reports*",
        admin_all_reports_menu="*Here is the list of all reports*",
        trash_menu='*Here is the deleted messages*',
        no_reports="There are no reports",
        not_yet='Not yet...',
        done_button="✅ Done",
        admin_notification='New report!\n',
        user_notification='Your question is answered!\n',

        admin_report_template="From: {}" 
                                "\nCategory: {}" 
                                "\nTime: {}" 
                                "\nReport: {}" 
                                "\nAnswer:{}",

        user_report_template="\nCategory: {}" 
                               "\nTime: {}" 
                               "\nYour Report: {}" 
                               "\nAnswer: {}",
        send_report_button='Send report',
        contacts_button='Contacts',
        my_reports_button='My reports',
        inbox_msg_button='Inbox messages',
        manage_admins_button='Manage admins',
        black_list_button="Black list",
        trash_button='Trash',
        admin_menu='here is admin side',
        send_btn='Send',
        yes='Yes',
        delete_btn='Delete',
        reply_btn='Reply',
        current_page='Current page: {}',
        message='Here is your Messages',
        answer='Here is the Answer'
    ),
    'RUS': dict(
        UNKNOWN_COMMAND=" Упс. Я такого не знаю. Нажми 🚑  /help, чтобы посмотреть все команды",
        ADD_ADMINS="⭐️ Добавить Админа",
        DELETE_ADMIN="❌ Удалить Админа",
        DELETE="❌ Удалить Бота",
        BACK="🔙 Назад",
        CREATE_NEW_BOT="🤖 Создать бота",
        MY_BOTS="📋 Список ботов",
        MANAGE_MY_BOTS="🔧 Настройки",
        GET_BOTS_INFO="ℹ️ Информация о боте",
        ADMIN="Админ",
        REMOVED="Удалён",
        IS_DELETED='Удалён',
        BOT='Бот',
        TOKEN_REQUEST="Как создать бота и получить токен: https://telegra.ph/Gajd-Sozdat-chatbota-06-03" 
                        " ❗️ ВАЖНО: Бот не должен быть подключен к другим Чатбот платформам\n"
                        "Вставь токен:",
        WRONG_TOKEN="Упс. Неверный токен. Попробуй снова",
        SELECT_ADMIN_TO_REMOVE="Выбери админа, которого хочешь удалить",
        UNKNOWN_ACTION=" Упс. Я такого не знаю. Нажми 🚑 /help, чтобы посмотреть все команды ",
        UNKNOWN_CHAT="Сначала создай бота, нажми 🤖 /create",
        WRONG_EMAIL="Упс. Странный E-mail. Попробуй ввести снова.",
        NO_BOTS="Сначала создай бота🤖 /create ",
        RETURNED_TO_MAIN_MENU="Обратно в меню",
        COMPLETE_CREATION_REQUEST=" Ты ещё не закончил с прошлым ботом. "
                                  "Доделай его или нажми ❌ /cancel, чтобы продолжить.",
        CANCEL_CREATION_REQUEST=" Чтобы завершить нажми ❌ /cancel ",
        WELCOME_MESSAGE_REQUEST="Введи приветственное сообщение для твоих юзеров✌️. "
                                  "Не переживай, его можно потом поменять",
        OCCUPATION_REQUEST="Чем ты занимаешься? Чтобы пропустить нажми /next",
        NEXT_EMAIL_REQUEST="Введи по очереди E-Mail других админов. " 
                           "Они получат одноразовый пароль, который должны отправить твоему боту."
                           "Если уже готов — напиши",
        YOU_ARE_THE_ONLY_ADMIN="Ты единственный админ этого бота",
        COMMANDS=
        '/new –  🤖 Создать бота'
        '/mybots  – 📋 Получить список ботов'
        '/Info – ℹ️ Информация о боте'
        '/cancel – ❌ завершить команду'
        '/Settings – 🔧 Управление ботами'
        '/help – 🚑 Список всех команд бота'
        'Проблема? Пиши ➡️ @CrowdbotSupport, скоро ответим ',
        ADMIN_EMAILS_REQUEST="Введи свой E-mail",
        CHOOSE_ACTION='Выбери действие',
        WELCOME=' Добро пожаловать в CrowdRobot! 🎉 Здесь ты можешь создать чатбота 🤖 за 2 минуты, '
                'вместо дорогого веб-сайта. Общайся с аудиторией, проводи опросы, публикуй контент, 💶 ' 
                'собирай донаты. 🆘Саппорт: @CrowdRobotSupport',
        NO_CONTEXT=" Нажми 🤖 /create чтобы начать. ",
        BOT_READY="Админы добавлены, бот(@{}) готов ✅ "
                    "Пройди в свой бот и нажми /start",
        SELECT_BOT_FOR_INFO="Выбери бота",
        SELECT_BOT_TO_MANAGE="Выбери бота",
        ALL_BOTS_COMPLETED=" Выхода нет. Создай бота🤖 /create",
        BOT_DELETED='Бот({}) удалён 🤕',
        CANCEL_CREATION="🛑 Отменить",
        en='🇬🇧English',
        ru='🇷🇺Русский',
        terms_of_use_menu='By clicking continue you agree with terms of use. Read it before continue',
        terms_of_use_in_text='Вы должны ознакомиться с условиями использования сервиса CrowdRobot и его ограничениями.' \
                             '\nНастоящее пользовательское соглашение заключается между мной и CrowdRobot. ' \
                             '\n- Да, я согласен с тем, CrowdRobot не несёт ответственности за любые действия ' \
                             'или бездействия пользователей и администраторов чатботов.' \
                             '\n- Да, при использовании CrowdRobot, я обязуюсь не нарушать нормы международного права и нормы ' \
                             'законодательства страны моего проживания.' \
                             '\n- Да, до третьего числа каждого месяца, я обязуюсь переводить абонентскую плату в ' \
                             'размере 12,99 евро, через сервис PayPal в пользу CrowdRobot. В случае неуплаты ' \
                             'в установленный срок, CrowdRobot приостановит работу вашего бота' \
                             '\n- CrowdRoBot оставляет за собой право вносить изменения в данное соглашение' \
                             '\n- CrowdRobot обязуется не передавать персональные данные клиентов третьим лицам.' \
                             '\n*Я-администратор(владелец) созданного при помощи Crowdrobot чатбота' \
                             '\n*Чатбот-виртуальный, автоматизированный собеседник на платформе Telegram' \
                             '\n*CrowdRobot – программа в Telegram. Создаёт чатботов с следующими функциями: ' \
                             'Обмен платежами, проведение опросов, размещение легального контента, обмен сообщениями.' \
                             '\n*CrowdRobot подключается к API той платёжной системы, которую выбрал администратор' \
                             '\nчатбота. Все платежи записываются в базу данных.' \
                             '\n*CrowdRobot выступает посредником между администратором чатбота и платёжной системой, ' \
                             'без доступа на изменение суммы платежа. Деньги переводятся с банковского счёта' \
                             '\nпользователя чатбота на на счёт администратора в выбранной им платёжной системе.' \
                             '\n(У платёжки с админом тоже есть договор, который это регулирует)' \
                             '\n✅Да, я согласен с условиями использования сервиса CrowdRoBot ',
        token_already_exist='You already got bot with this token -> {}. '
                            'If you want to create new one send me new token that '
                            'you can take from @BotFather',

        manage_bots_button='Manage my bots',
        contact_button='Contact with Crowd Team',
        terms_as_text_button='Send as text',
        terms_as_doc_button='Send as .docx file',
        agree_with_terms_button='I have read. Continue',
        continue_button_text='Continue',
        add_button='Add',

        your_bots='\nYour bots: \n{}',
        bot_template='\nName: {}'
                     '\nAdmins: {}'
                     '\nCreation date: {}',
        confirm_delete_bot="Are u sure u want to delete bot({})?",
        ENTER_NEW_ADMIN_EMAIL="Enter E-Mail addresses of the admins. "
                              "They'll get a one-time password that they have to send to your bot."
                              "If you are already ready — press 'Add' ",
        admins_added='Admins successfully added',
        only_one_admin="There are only one admin and it is you",
        add_already_exist_admin='Admin => {} already exist. ',
        confirm_delete_admin='Are u sure u want to delete {} from {} admins?',
        admin_removed_success='{} have been removed successfully',
        language_menu='Please select language you want to use.',
        start_message="Hello. I'm support bot.\n"
                      "U can send message to developers - click 'Send message'",
        choose_category="Choose what your message about, or send a message "
                        "that describe in few words what your report about",
        contacts='Here is contacts:\n'
                 '@keikoobro\n'
                 '@vasile_python\n'
                 '@Mykyto\n',
        enter_message="Please describe your problem and we will try to solve this issue. U can send photo, audio, "
                      "voice messages and other",
        admin_give_answer="What do u want to answer?",

        enter_message_2="Send a new message if u want to add more information to your report or press '✅ Done'",
        admin_give_answer_2="Send a new message if u want to add more information to your answer or press '✅ Done'",

        report_contains='Your report contains: ',
        admin_give_answer_3='Your answer contains: ',

        enter_message_4='User report contains:',

        confirm_message='Are you sure u want to send your report?',
        confirm_answer='Are you sure u want to send your answer?',
        confirm_delete='Are u sure u want to delete report. You can restore it from trash anytime',

        finish_send_report="Thank you! We will review your this chatbot asap. You can find answer in 'Inbox messages', "
                           "We will send u notification when answer is ready",
        finish_send_answer='Reply successfully sent, User user received notification',
        finish_move_to_trash='Report successfully moved to trash. You can restore it from trash anytime',

        blink_success_send_report="Success Send, Thank you for report",
        blink_success_send_answer="Success Send Answer",

        my_reports_menu="*Here is the list of your reports*",
        admin_all_reports_menu="*Here is the list of all reports*",
        trash_menu='*Here is the deleted messages*',
        no_reports="There are no reports",
        not_yet='Not yet...',
        done_button="✅ Done",
        admin_notification='New report!\n',
        user_notification='Your question is answered!\n',

        admin_report_template="From: {}"
                              "\nCategory: {}"
                              "\nTime: {}"
                              "\nReport: {}"
                              "\nAnswer:{}",

        user_report_template="\nCategory: {}"
                             "\nTime: {}"
                             "\nYour Report: {}"
                             "\nAnswer: {}",
        send_report_button='Send report',
        contacts_button='Contacts',
        my_reports_button='My reports',
        inbox_msg_button='Inbox messages',
        manage_admins_button='Manage admins',
        black_list_button="Black list",
        trash_button='Trash',
        admin_menu='here is admin side',
        send_btn='Send',
        yes='Yes',
        delete_btn='Delete',
        reply_btn='Reply',
        current_page='Current page: {}',
        message='Here is your Messages',
        answer='Here is the Answer'
    )}

categories = {
    'ENG': {
        'Musician': [
            "Discography",
            "Concerts",
            "Battles",
            "New Projects",
            "Live photos"
        ],
        'Art': [
            "Works ",
            "Sketches-New Projects ",
            "Exhibitions  ",
            "Photos of Studio "
        ],
        'Start up': [
            "Idea ",
            "Business plan ",
            "Outlay  ",
            "Team  "
        ],
        'Society': [
            "Activity",
            "Archive of Project",
            "New projects",
            "Report and accreditation"
        ],
        "Writer": [
            "Bibliography",
            "Drafts and Passages",
            "Thoughts",
            "Poems"
        ],
        "Blog": [
            "Activity",
            "My Life",
            "Adventure",
            "Links"
        ],
        "Food": [
            "Recipes",
            "Food",
            "Videos",
            "Kitchen"
        ],
        "Fashion": [
            "My Style",
            "Clothes",
            "References",
            "Exhibitions"
        ],
        "Events": [
            "Idea",
            "Calendar",
            "Team",
            "Last Events"
        ]
    },
    'RUS': {
        'Musician': [
            "Discography",
            "Concerts",
            "Battles",
            "New Projects",
            "Live photos"
        ],
        'Art': [
            "Works ",
            "Sketches-New Projects ",
            "Exhibitions  ",
            "Photos of Studio "
        ],
        'Start up': [
            "Idea ",
            "Business plan ",
            "Outlay  ",
            "Team  "
        ],
        'Society': [
            "Activity",
            "Archive of Project",
            "New projects",
            "Report and accreditation"
        ],
        "Writer": [
            "Bibliography",
            "Drafts and Passages",
            "Thoughts",
            "Poems"
        ],
        "Blog": [
            "Activity",
            "My Life",
            "Adventure",
            "Links"
        ],
        "Food": [
            "Recipes",
            "Food",
            "Videos",
            "Kitchen"
        ],
        "Fashion": [
            "My Style",
            "Clothes",
            "References",
            "Exhibitions"
        ],
        "Events": [
            "Idea",
            "Calendar",
            "Team",
            "Last Events"
        ]
    }}

report_categories = {
                        'ENG': ['Sentence', 'Complaint', 'Usage Question'],
                        'RUS': ['Предложение', 'Жалоба', 'Usage Question']
                    }


def get_str(lang, string, *args):
    return strings_dict.get(lang)[string].format(*args)
