
# lil guide
"""
тип данных - 'строка' в питоне обозначается в ' ' или " " кавычках
example:
BACK="🔙 Back"

с лева -> имя_перменной = 'строка' <- с права

что бы не писать большой текст в одну линию можно переносить 
часть строки на некст линию просто написав одну строчку за другой
example:
NEXT_EMAIL_REQUEST="Enter E-Mail addresses of the other admins. "
                   "They'll get a one-time password that they have to send to your bot."
                   "If you are already ready — press 'continue' ",

при этом перенос на некст линию не считается как абзац в строке,
что бы поставить абзац нужно написать знак -> \n
example:
bot_template='\nName: {}' 
             '\nAdmins: {}'
             '\nCreation date: {}'
             
в {} кавычках обозначаются динамические элементы, то есть строка является на подобие шаблона
в который ты вставляешь данные, и что бы обозначить место куда будут вставляться
данные в строку используют -> {}
example:
confirm_delete_admin='Are u sure u want to delete {} from {} admins?',
в первые кавычки {} - вставляется имя админа, а в вторые {} идёт имя бота ->

в боте -> 
Are u sure u want to delete keikoobro@gmail.com from TEST_CROWD_bot admins?



\n - абзац. Всё что после этого символа начинается с новой строки

{} - место где будут находиться данные -> 
     нельзя убирать. 
     Если убирать - еррора скорее всего не будет но может строка не правильно отображаться, 
        предупредить если менять
    
' ' или " "  -> одно и то же - символы в которые пишуться строки. 
    любой текст помещяется между кавычками и он готов к использованию
    Нельзя убрать - будет крит
    прим.: Если строку обозначать в одинарных кавычках ' ' то нельзя использовать одинарные кавычки в тексте
            То же самое и с двойными кавычками " " - нельзя в тексте использовать "
    То есть строку "I'm the man" всегда пишем в двойных кавычках потому что есть одинарная кавычка ' в тексте
    
    все строки записаны в словаре=dictionary=dict. 
    в данном случае словарь это массив который хранит 
        строки и ключи по которым можно получить доступ к этим строкам:
        
    strings_dict = {
        
        'ENG': dict(
            key='here is string'
            ),
            
        'RUS': dict(
            key='тут строка'        
        )
    }
    strings_dict - словарь с двумя ключами 'ENG', 'RUS'
    'ENG', 'RUS' - тоже два словаря в которых лежат названия строк в ключах и сами строки в значениях для этих ключей
"""

# BotFather emoji
new_bot_emoji = "🌟"
delete_bot_emoji = "🔴"
add_admin_emoji = "➕"
delete_admin_emoji = "➖"
# SupportBot emoji
my_report_menu_emoji = "📬"
answer_ready_emoji = "📧"
# AdminBot emoji
admin_new_report_emoji = "📨"


# New Version
strings_dict = {
    'ENG': dict(
        ADD_ADMINS="⭐️ Add admin",
        DELETE_ADMIN="❌ Delete admin",
        DELETE="❌ Delete Bot",
        BACK="🔙 Back",
        CREATE_NEW_BOT="🤖 Create a new bot",
        ADMIN="Admin",
        TOKEN_REQUEST="How to create a bot and get a token: https://telegra.ph/Guide-Chatbot-creation-06-03"
                      " ❗️ IMPORTANT: the bot should not be connected to other chatbot platforms"
                      "Insert token:",
        WRONG_TOKEN="Oops. Wrong token. Try again",
        SELECT_ADMIN_TO_REMOVE="Choose the admin that you want to remove",
        UNKNOWN_CHAT="At first create a bot, press 🤖 /create",
        WRONG_EMAIL="Oops. Wrong E-mail. Try again.",
        NO_BOTS="At first create a bot, press 🤖 /create ",
        RETURNED_TO_MAIN_MENU="Back to the menu",
        WELCOME_MESSAGE_REQUEST="Enter a welcome message for your users✌️. Don't worry, it can be changed later",
        OCCUPATION_REQUEST="What do you do? To skip click /next",
        NEXT_EMAIL_REQUEST="Enter E-Mail addresses of the other admins. "
                           "They'll get a one-time password that they have to send to your bot."
                           "If you are ready — press 'continue' ",
        YOU_ARE_THE_ONLY_ADMIN="You are the only one admin of this bot",
        ADMIN_EMAILS_REQUEST="Enter your E-mail",
        CHOOSE_ACTION='*Select action*',
        WELCOME=' Welcome to CrowdRobot! 🎉 Here you can create a chatbot 🤖 in 2 minutes, '
                'instead of an expensive website. Communicate with your audience, conduct surveys, '
                'publish content and collect donations ',
        NO_CONTEXT=" Press 🤖 /create to start. ",
        BOT_READY="Admins are added, the bot is ready ✅"
                  "Go to your bot({}) and click /start",
        SELECT_BOT_TO_MANAGE="<b>Choose bot</b>",
        ALL_BOTS_COMPLETED=" There is no exit. Create bot🤖 /create",
        BOT_DELETED='Bot({}) is deleted 🤕',
        CANCEL_CREATION="🛑 Cancel",
        en='🇬🇧English',
        ru='🇷🇺Русский',
        terms_of_use_menu='By clicking "Continue" you agree with terms of use. Read it before continue.'
        'If you do not agree to the Terms, you are not authorized to use any Services.',
        terms_of_use_in_text = "Please review the CrowdRobot's terms of use and its limitations. "
                               "\nThis user agreement is between me and CrowdRobot. "
                               "\n\n✅ Yes, I  agree, that CrowdRobot is not responsible for"
                               " any actions or inactions of my, users and chatbot's admins."
                               "\n✅ Yes, I undertake not to violate international law and the laws of the country of "
                               "my residence. "
                               "\n✅ Yes, I agree to transfer a subscription fee of 12.99 euros "
                               "each month through the PayPal service in favor of CrowdRobot. In the case of "
                               "non-payment within the prescribed period, CrowdRobot suspend the operation of your bot."
                               "\n✅ CrowdRobot reserves the right to change these terms and conditions at any time "
                               "without prior notice."
                               "\n✅ CrowdRobot undertakes not to disclose to third parties the information "
                               "and personal data."
                               "\n\nℹ️ I - an administrator(owner) created using Crowdrobot chatbot"
                               "\nℹ️ Chatbot - a computer program which conducts a conversation via textual "
                               "methods on Telegram' "
                               "\nℹ️ CrowdRobot – the program in the Telegram.  Creates chatbots "
                               "with the following functions:"
                               "\n• payment exchange, "
                               "\n• conducting surveys, "
                               "\n• posting legal content, "
                               "\n• messaging."
                               "\nℹ️ CrowdRobot connects to the API of the payment system chosen by the "
                               "chatbot administrator.'"
                               "\nℹ️ All payments are recorded in the database."
                               "\nℹ️ CrowdRobot acts as an intermediary between the chatbot administrator and the "
                               "payment system, without access to change the amount of payment. "
                               "The money is transferred from the Bank account of the chatbot user to the account "
                               "of the administrator in the chosen payment system. ",
        token_already_exist = 'You already got bot with this token -> {}. '
                              'If you want to create new one send me new token that '
                              'you can take from @BotFather',
        manage_bots_button='🛠  Manage my bots',
        contact_button='❓ Contact with Crowd Team',
        agree_with_terms_button='I have read it. Continue',
        continue_button_text='Continue',
        add_button='Add',
        your_bots='\n<b>Your bots:</b> \n{}',
        bot_template='\n*Name:* {}'
                     '\n*Admins:* {}'
                     '\n*Creation date:* `{}`',
        confirm_delete_bot="Are u sure u want to delete {} - {}?",
        ENTER_NEW_ADMIN_EMAIL="Enter E-Mail addresses of the admins. "
                                "They'll get a one-time password that they have to send to your bot."
                                "If you are ready — press 'Add' ",
        admins_added='Admins successfully added',
        only_one_admin="You are only one admin",
        add_already_exist_admin='Admin => {} already exist. ',
        confirm_delete_admin='Are you sure you want to delete {} from {} admins?',
        admin_removed_success='{} have been removed successfully',
        language_menu='Please select language you want to use.',
        # SENDING REPORT PART
        start_message="Hello. I'm the support bot.\n"
        "You can send message to the developers - click 'Send message'",
        choose_category="Choose what your message about, or send a message "
                          "that describe in few words what your report about",
        contacts='<i>Here is contacts:</i>\n'
                 '@keikoobro\n'
                 '@vasile_python\n'
                 '@Mykyto\n'
                 '@dvk88\n',
        enter_message="Please describe your problem and we will try to solve this issue. You can send photo, audio, "
                        "voice messages and other",
        admin_give_answer="*What do you want to answer?*",
        enter_message_2="Send a new message if you want to add more information to your report or press '✅ Done'",
        admin_give_answer_2="Send a new message if you want to add more information to your answer or press '✅ Done'",
        report_contains='*Your report contains:* ',
        admin_give_answer_3='*Your answer contains:* ',
        enter_message_4='*User report contains:*',
        confirm_message='Are you sure you want to send your report?',
        confirm_answer='Are you sure you want to send your answer?',
        confirm_delete='Are you sure you want to delete this report. You can restore it from trash anytime',
        finish_send_report="Thank you! We will review your this chatbot asap. You can find answer in 'Inbox messages', "
                             "We will send you notification when answer is ready",
        finish_send_answer='Reply successfully sent, User user received notification',
        finish_move_to_trash='Report successfully moved to trash. You can restore it from trash anytime',
        blink_success_send_report="Success Send, Thank you for report",
        blink_success_send_answer="Success Send Answer",
        my_reports_menu=my_report_menu_emoji + "*Here is the list of your reports*",
        admin_all_reports_menu="\n*Here is the list of all reports*",
        trash_menu='*Here is the deleted messages*',
        no_reports="There are no reports",
        not_yet='Not yet...',
        done_button="✅ Done",
        admin_notification=admin_new_report_emoji + '<b>New report!</b>\n',
        user_notification=answer_ready_emoji + '<b>Your question is answered!</b>\n',

        admin_report_template="\n<b>From:</b> {}"
                              "\n<b>Category:</b> <code>{}</code>"
                              "\n<b>Time:</b> <code>{}</code>"
                              "\n<b>Report:</b>\n {}"
                              "\n<b>Answer:</b>\n {}",

        user_report_template="\n<b>Category:</b> <code>{}</code>"
                             "\n<b>Time:</b> <code>{}</code>"
                             "\n<b>Your Report:</b>\n {}"
                             "\n<b>Answer:</b>\n {}",
        send_report_button='✉️ Send report',
        contacts_button='Contacts',
        my_reports_button='📤 My reports',
        inbox_msg_button='Inbox messages',
        manage_admins_button='Manage admins',
        black_list_button="Black list",
        trash_button='Trash',
        admin_menu='here is admin side',
        send_btn='Send',
        yes='Yes',
        delete_btn='Delete',
        reply_btn='Reply',
        open_btn="Open",
        restore_btn="Restore",
        current_page='*Current page:* `{}`',
        message='*Here is your Messages:*',
        answer='*Here is the Answer:*',



        lang_button='Language',
        accept='Yes, I agree to the terms of use of the CrowdRoBot service',
        admin_already_in_list='Admin already in the list\n',

        api_error_creating_bot='Sorry, but bot creation was interrupted due to internal error. '
                               '\nA notification was sent to the developers.',
        api_error_deleting_bot='Sorry, but the bot deletion was interrupted due to internal error. '
                               '\nA notification was sent to the developers.',
        api_error_adding_admins='Sorry, but the addition of administrators was interrupted due to internal error. '
                                '\nA notification was sent to the developers.',
        api_error_deleting_admins='Sorry, but the deletion of administrators was interrupted due to internal errors. '
                                  '\nA notification was sent to the developers.',

        finish_creating=new_bot_emoji + '*Bot Created*'
                        '\n\n*Name:* {}'
                        '\n*Admins:* {}'
                        '\n*Creation date:* `{}`',
        finish_deleting=delete_bot_emoji + '*Bot Deleted*'
                        '\n\n*Name:* {}'
                        '\n*Admins:* {}'
                        '\n*Creation date:* `{}`'
                        '\n*Deletion date:* `{}`',
        finish_admins_deleting=delete_admin_emoji + '*Admin deleted*'
                               '\n\n*Bot:* {}'
                               '\n*Admins:* {}'
                               '\n*Date:* `{}`',
        finish_admin_add=add_admin_emoji + '*Admins added*'
                         '\n\n*Bot:* {}'
                         '\n*Admins:* {}'
                         '\n*Date:* `{}`',
        finish_report_sending='Your report has been successfully sent'
                              "\n\n*Category:* `{}`"
                              "\n*Time:* `{}`"
                              "\n*Your Report:*\n {}"
                              "\n*Answer:*\n {}",
        report_file='one {} file.',
        report_file_2='{} {} file. ',
        report_files='{} {} files. '







    ),
    'RUS': dict(
        ADD_ADMINS="⭐️ Добавить Админа",
        DELETE_ADMIN="❌ Удалить Админа",
        DELETE="❌ Удалить Бота",
        BACK="🔙 Назад",
        CREATE_NEW_BOT="🤖 Создать бота",

        ADMIN="Админ",
        REMOVED="Удалён",
        TOKEN_REQUEST="Как создать бота и получить токен: https://telegra.ph/Gajd-Sozdat-chatbota-06-03"
                      "\n❗️ Не подключай бот, который уже используешь в других Чатбот платформах"
                      "\nВставь токен:",
        WRONG_TOKEN="Упс. Неверный токен. Скопируй его заново и попробуй снова",
        SELECT_ADMIN_TO_REMOVE="Выбери админа, которого хочешь удалить",
        UNKNOWN_CHAT="Чтобы создать бота, нажми 🤖 /create",
        WRONG_EMAIL="Упс. Неверный E-mail. Попробуй ввести снова.",
        NO_BOTS="Сначала создай бота, нажми 🤖 /create ",
        RETURNED_TO_MAIN_MENU="Назад в меню",
        WELCOME_MESSAGE_REQUEST="Введи приветствие для твоих юзеров."
                                "\nНе переживай, его можно потом поменять",
        OCCUPATION_REQUEST="Чем ты занимаешься? Чтобы пропустить нажми /next",
        NEXT_EMAIL_REQUEST="Напиши почту других админов, по очереди. "
                           "\nЧтобы получить права админа, они должны отправить твоёму боту одноразовый пароль. "
                           "Попроси их проверить почту."
                           "\nНажми 'Далее', если ты единственный админ",

        YOU_ARE_THE_ONLY_ADMIN="Ты единственный админ этого бота",
        ADMIN_EMAILS_REQUEST="Введи свою почту",
        CHOOSE_ACTION='*Выбери действие*',
        WELCOME='Добро пожаловать в CrowdRobot! Создай чатбота за 2 минуты,'
                'вместо дорогого веб-сайта. Общайся с аудиторией, проводи опросы, публикуй контент, 💶 '
                'собирай донаты.',
        NO_CONTEXT=" Нажми 🤖 /create, чтобы начать. ",
        BOT_READY="✅ Админы добавлены, бот(@{}) готов."
                  "\nЗайди в бот и нажми /start",
        SELECT_BOT_TO_MANAGE="<b>Выбери бота</b>",
        ALL_BOTS_COMPLETED=" Выхода нет. Создай бота 🤖 /create",
        BOT_DELETED='🤕 Бот({}) удалён',
        CANCEL_CREATION="🛑 Отменить",
        en='🇬🇧English',
        ru='🇷🇺Русский',
        terms_of_use_menu='Перед тем как продолжить, прочти Пользовательское соглашение и согласись с его положениями.',
        terms_of_use_in_text="Вы должны ознакомиться с условиями использования сервиса CrowdRobot и его ограничениями."
                             "\nНастоящее пользовательское соглашение заключается между мной и CrowdRobot. "
                             "\n\n✅ Да, я согласен с тем, CrowdRobot не несёт ответственности за любые действия или "
                             "бездействия пользователей и администраторов чатботов."
                             "\n✅ Да, при использовании CrowdRobot, я обязуюсь не нарушать нормы международного права "
                             "и нормы законодательства страны моего проживания."
                             "\n✅ Раз в месяц я обязуюсь переводить абонентскую плату в "
                             "размере 12,99 евро, через сервис PayPal в пользу CrowdRobot. В случае неуплаты в "
                             "установленный срок, CrowdRobot приостановит работу вашего бота"
                             "\n✅ CrowdRoBot оставляет за собой право вносить изменения в данное соглашение"
                             "\n✅ CrowdRobot обязуется не передавать персональные данные клиентов третьим лицам."
                             "\n\nℹ️ Я-администратор(владелец) созданного при помощи Crowdrobot чатбота"
                             "\nℹ️ Чатбот-виртуальный, автоматизированный собеседник на платформе Telegram"
                             "\nℹ️ CrowdRobot – программа в Telegram. Создаёт чатботов с следующими функциями: "
                             "\n• Обмен платежами,"
                             "\n• проведение опросов, "
                             "\n• размещение легального контента, "
                             "\n• обмен сообщениями."
                             "\nℹ️ CrowdRobot подключается к API той платёжной системы, которую выбрал "
                             "администратор чатбота. "
                             "\nℹ️ Все платежи записываются в базу данных."
                             "\nℹ ️CrowdRobot выступает посредником между администратором чатбота и платёжной "
                             "системой, без доступа на изменение суммы платежа. Деньги переводятся с банковского"
                             " счёта пользователя чатбота на на счёт администратора в выбранной им платёжной системе.",
        token_already_exist='Бот {} с этим токеном уже есть.'
                            'Если тебе нужен ещё один бот, то возьми его у @BotFather',

        manage_bots_button='🛠 Настроить ботов',
        contact_button='❓ Поддержка',
        terms_as_text_button='Показать соглашение',
        terms_as_doc_button='Send as .docx file',
        agree_with_terms_button='Я согласен',
        continue_button_text='Продолжить',
        add_button='➕ Add',

        your_bots='\n<b>Твои боты:</b> \n{}',
        bot_template='\n*Название:* {}'
                     '\n*Админы:* {}'
                     '\n*День рождения:* `{}`',
        confirm_delete_bot="Уверен, что хочешь удалить {} - {}?",
        ENTER_NEW_ADMIN_EMAIL="Введи почту новых админов."
                              "\nЧтобы получить права админа, они должны отправить "
                              "одноразовый пароль твоему боту пароль. Пусть проверят почту."
                              "\nНажми 'Добавить', если готово",
        admins_added='✅ Администраторы добавлены',
        only_one_admin="Ты единственный админ этого бота",
        add_already_exist_admin='Админ {} уже добавлен. ',
        confirm_delete_admin='Уверен, что хочешь удалить админа {} из {}?',
        admin_removed_success='Админ {} удалён',
        language_menu='Выбери язык.',
        start_message="Ку, я бот поддержки\n"
                      "Нажми 'Отправить сообщение' и мы ответим тебе в течение 24 часов",
        choose_category="Выбери раздел сообщения, которое его описывает.",
        contacts='<i>Если торопишься, то пиши сюда:</i>\n'
                 '@keikoobro\n'
                 '@vasile_python\n'
                 '@Mykyto\n'
                 '@dvk88\n',
        enter_message="Опиши свою проблему и мы её решим. Можешь отправлять любой медиа-файл.",
        admin_give_answer="*Что хочешь ответить?*",

        enter_message_2="Отправь ещё сообщение или нажми 'Отправить'",
        admin_give_answer_2="Отправь ещё сообщение или нажми '✅ Готово'",

        report_contains='*Твоё сообщение:* ',
        admin_give_answer_3='*Твой ответ:* ',

        enter_message_4='*Сообщение юзера:* ',

        confirm_message='Уверен, что хочешь отправить сообщение?',
        confirm_answer='Уверен, что хочешь отправить ответ?',
        confirm_delete='Уверен, что хочешь удалить сообщение? Ты можешь вернуть его из корзины в любое время.',

        finish_send_report="Спасибо! Мы ответим в течение 24 часов."
                           "Ответ ты найдёшь» в '📥 Входящих'."
        "Ты получишь уведомление, когда ответ будет готов",
        finish_send_answer='Ответ отправлен. Юзер получил уведомление',
        finish_move_to_trash='Сообщение удалено. Ты можешь вернуть его из корзины в любое время.',

        blink_success_send_report="✅ Успешно отправлено. Спасибо.",
        blink_success_send_answer="✅ Успешно отправлено. Спасибо.",

        my_reports_menu=my_report_menu_emoji + "*Список твоих сообщений:*",
        admin_all_reports_menu="*Список всех репортов*",
        trash_menu='*Все удалённые сообщения:*',
        no_reports="Нет сообщений",
        not_yet='Ещё нет',
        done_button="✅ Готово",
        admin_notification=admin_new_report_emoji + '<b>Новое сообщение</b>\n',
        user_notification=answer_ready_emoji + '<b>Ты получил ответ на свой вопрос.</b>\n',

        admin_report_template="\n<b>От:</b> {}"
                              "\n<b>Раздел:</b> <code>{}</code>"
                              "\n<b>Время:</b> <code>{}</code>"
                              "\n<b>Сообщение:</b>\n {}"
                              "\n<b>Ответ:</b>\n {}",

        user_report_template="\n<b>Раздел:</b> <code>{}</code>"
                             "\n<b>Время:</b> <code>{}</code>"
                             "\n<b>Твоё сообщение:</b>\n {}"
                             "\n<b>Ответ:</b>\n {}",

        send_report_button='✉️ Отправить сообщение',
        contacts_button='🙎‍♂️ Контакты',
        my_reports_button='📤 Отправленные',
        inbox_msg_button='📥 Входящие',
        manage_admins_button='Управлять админами',
        black_list_button="Чёрный список",
        trash_button='🗑 Корзина',
        admin_menu='🧛‍♂️Это сторона админа',
        send_btn='📤 Отправить',
        yes='Да',
        delete_btn='🗑 Удалить',
        reply_btn='Ответить',
        open_btn="Просмотр",
        restore_btn="Восстановить",
        current_page='*Страница:* `{}`',
        message='*Твоё сообщение:*',
        answer='*Ответ:*',




        lang_button='Язык',
        accept='Да, я согласен с условиями использования сервиса CrowdRoBot ',
        admin_already_in_list='Администратор уже добавлен в список\n',

        api_error_creating_bot='Извини но создание бота было прервано из за внутренней ошибки. '
                               '\nРазработчикам было отправлено уведомление.',
        api_error_deleting_bot='Извини но удаление бота было прервано из за внутренней ошибки. '
                               '\nРазработчикам было отправлено уведомление.',
        api_error_adding_admins='Извини но добавление администраторов было прервано из за внутренней ошибки. '
                                '\nРазработчикам было отправлено уведомление.',
        api_error_deleting_admins='Извини но удаление администраторов было прервано из за внутренних ошибок. '
                                  '\nРазработчикам было отправлено уведомление.',

        finish_creating=new_bot_emoji + '*Бот Создан*'
                        '\n\n*Название:* {}'
                        '\n*Админы:* {}'
                        '\n*День рождения:* `{}`',
        finish_deleting=delete_bot_emoji + '*Бот Удалён*'
                        '\n\n*Название:* {}'
                        '\n*Админы:* {}'
                        '\n*День рождения:* `{}`'
                        '\n*Дата удаления:* `{}`',
        finish_admins_deleting=delete_admin_emoji + '*Админ удалён*'  
                               '\n\n*Бот:* {}'
                               '\n*Админ:* {}'
                               '\n*Дата:* `{}`',
        finish_admin_add=add_admin_emoji + '*Админы добавлены*'
                         '\n\n*Бот:* {}'
                         '\n*Админы:* {}'
                         '\n*Дата:* `{}`',
        finish_report_sending='Your report has been successfully sent'
                              "\n\n*Category:* `{}`"
                              "\n*Time:* `{}`"
                              "\n*Your Report:*\n {}"
                              "\n*Answer:*\n {}",
        report_file='один {} файл.',
        report_file_2='{} {} файл. ',
        report_files='{} {} файла. '
    )}


categories = {
    'ENG': {
        'Musician': [
            "Discography",
            "Concerts",
            "Battles",
            "Songs",
            "Photos"
        ],
        'Art': [
            "Works",
            "Sketches",
            "Exhibitions",
            "Inspiration"
        ],
        'Start up': [
            "Problem",
            "Solution",
            "Experiment",
            "Team "
        ],
        'Society': [
            "Activity",
            "Projects",
            "Costs",
            "Reports and Accreditation"
        ],
        "Writer": [
            "Bibliography",
            "Drafts and Passages",
            "Photos",
            "Thoughts"
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
            "Style",
            "Clothes",
            "References",
            "Exhibitions"
        ],
        "Events": [
            "Idea",
            "Calendar",
            "Team",
            "Last Events"
        ],
        "None of the above": None
    },
    'RUS': {
        'Музыка': [
            "Дискография",
            "Концерты",
            "Баттлы",
            "Песни",
            "Фото"
        ],
        'Искусство': [
            "Работы",
            "Черновики",
            "Выставки",
            "Вдохновение"
        ],
        'Бизнес': [
            "Проблема",
            "Решение",
            "Эксперимент",
            "Команда"
        ],
        'Общество': [
            "Активность",
            "Проекты",
            "Расходы",
            "Отчёты и аккредитация"
        ],
        "Издательство": [
            "Библиография",
            "Черновики",
            "Мысли",
            "Фото"
        ],
        "Блог": [
            "Дело",
            "Жизнь",
            "Приключения",
            "Ссылки"
        ],
        "Еда": [
            "Рецепты",
            "Еда",
            "Видео",
            "Кухня"
        ],
        "Мода": [
            "Стиль",
            "Одежда",
            "Вдохновение",
            "Выставки"
        ],
        "Эвенты": [
            "Идея",
            "Календарь",
            "Команда",
            "События"
        ],
        "Ничего из выше перечисленного": None
    }}

# TODO better
#   saving category keys in db, don't change it
report_categories = {
    'ENG': dict(
        complaint="Complaint",
        suggestion="Suggestion",
        advertising="Advertising",
        feedback="Feedback"
    ),
    'RUS': dict(
        complaint="Предложение",
        suggestion="Жалоба",
        advertising="Реклама",
        feedback="Отзыв"
    )
}


def boolmoji(boolean: bool):
    emoji_yes = "✅"
    emoji_no = '🔲'
    # emoji_no = '☑️'
    return emoji_yes if boolean else emoji_no


def get_str(user_data, update, string, *args):
    if not user_data.get("lang"):
        user_data["lang"] = bot_father_users_table.find_one(
            {'user_id': update.effective_user.id})["lang"]
    return strings_dict.get(user_data["lang"])[string].format(*args)
