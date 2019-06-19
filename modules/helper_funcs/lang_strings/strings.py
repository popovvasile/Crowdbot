from database import chatbots_table

string_dict_dict = {
    "ENG": dict(
        channels_str_1='Here u can manage your channels',
        channels_str_2='List of your channels',
        # Click "Add" to configure your first channel or "Back" for main menu
        no_channels='You have no channel configured yet. Click "Add channel" to configure your first channel',
        wrong_channel_link_format='Send me link or username of your channel. ' \
                                  'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"',
        bot_is_not_admin_of_channel='Bot is not admin in this({}) channel. ' \
                                    'Add bot as admin to the channel and then back to this menu ' \
                                    'and send me link or username of your channel. ' \
                                    'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"',
        bot_is_not_admin_of_channel_2="Bot is not admin in this({}) channel or can't send message to the channel" \
                                      "So channel was deleted. Add bot as admin to the channel, " \
                                      "let it send message to the channel " \
                                      "and then add channel again by Clicking 'Add channel'",
        channels_str_4="To add channel u need to add this bot as admin to your channel " \
                       "and then back to this menu and send " \
                       "link or username of your channel. " \
                       "Send me link or username of your channel",
        allow_bot_send_messages='U need to allow bot send messages to the channel. ' \
                                'And than back to this menu and send username of channel',
        no_such_channel='There are no such channel. ',
        choose_channel_to_remove='Choose channel you want to remove',
        channel_has_been_removed='Channel({}) has been deleted.',
        channel_added_success='Now you can send posts to the channel({}) using this commands.',
        choose_channel_to_post='Choose channel u want to post',
        post_message='What do u want to do?',
        send_post="What do you want to post on your channel({})?\n" \
                  "We will forward your message to channel.",
        choose_channel_to_send_poll='Choose channel u want to send poll',
        choose_channel_to_send_survey='Choose channel u want to send survey',
        try_to_add_already_exist_channel='This channel already exists',

        user_mode_help_admin="""
Press “On" to turn on the bot in the user mode. 
Press “Off" to return to the normal mode 
""",
        user_mode_on_finish="✅ Ready, now look at the bot in user mode",
        user_mode_off_finish="🔚 User mode is off",

        user_mode_str="User mode",
        send_a_post_to_channel='Write a post on the channel',

        promotion_send_message_module_str="Promotion",
        promotion_send_message_button_1="📤 Send message",
        promotion_send_message_button_2="📥 Mailbox",
        promotion_send_message_1="Write a message",
        promotion_send_message_2="Thanks, the homing pigeon's on its way. 🕊!",
        promotion_send_message_3="Write a message to users\n" \
                                 "Thanks, the homing pigeon's on its way. 🕊!",
        promotion_send_message_4="Write a new message and press '✅ Done",
        promotion_send_message_5="✅The message is sent",
        promotion_send_message_6="Forever alone 😉 ",
        promotion_send_message_admin="""
Here you can:
📤 Send message to users
📥 Check email
🦖 Meet the dinosaur


Send a message to users and get feedback
""",
        promotion_send_message_user="""
Here you can order promotion from this chatbot and their channels
""",
        delete_button_str="Delete",
        delete_button_str_all="Delete all messages",
        delete_button_str_last_week="Delete last week",
        delete_button_str_last_month="Delete last month",

        delete_message_str_1="Chosen messages have been deleted",
        send_message_module_str="✉️ Messages",
        send_message_button_1="📤 Send message",
        send_message_button_2="📥 Mailbox",
        send_message_1="Write a message",
        send_message_2="Thanks, the homing pigeon's on its way. 🕊!",
        send_message_3="Write a message to users\n" \
                       "Thanks, the homing pigeon's on its way. 🕊!",
        send_message_4="Write a new message and press '✅ Done",
        send_message_5="✅The message is sent",
        send_message_6="Forever alone 😉 ",
        send_message_admin="""
Here you can:
📤 Send message to users
📥 Check email
🦖 Meet the dinosaur


Send a message to users and get feedback
""",
        send_message_user="""
Say Hello to the admin!
""",
        send_donation_request_1="Tell everyone about the fundraising and how you will utilize the money\n" \
                                "The 'Support project' button will be attached to the message'",
        send_donation_request_2="Write a new message and press '✅ Done",
        send_donation_request_3="💸 The message is sent!",

        answer_button_str="Answer",
        send_donation_request_button="Send donation request",
        cancel_button_survey="🔚 Cancel survey",
        donate_button="💰 Manage payments",
        back_button="🔙 Back",
        cancel_button="Cancel",
        remove_button="Remove",
        send_survey_to_channel='Send a survey',
        send_poll_to_channel='Send a poll',
        send_post_to_channel='Write a post',
        done_button="✅ Done",
        create_button="Create",
        delete_button="🗑 Delete",
        send_button="📤 Send",
        results_button="📊 Results",
        menu_button="ℹ️ Menu",
        allow_donations_button=" 💰 Create a payment",
        configure_button="🛠 Settings",
        ask_donation_button="Ask for money",
        title_button="Name",
        description_button="Description",
        currency_button="Currency",
        delete_donation_button="🗑 Delete the payment",
        great_text="Well done!",
        create_button_button="📌 Create a button ",
        edit_button="✏️ Edit",
        start_button="🏁 Start",
        main_survey_button="The main survey",
        back_text="Press '🔙 Back ' to return to the menu ",
        polls_affirmations=[
            "OK",
            "Cool",
            "Great",
            "Perfectly",
            "Okeydokey",
            "Easy-peasy",
            "Yuhu",
            "Yo",
            "Good",
        ],
        polls_str_1='Enter the name of the poll',
        polls_str_2="Choose your poll type?",
        polls_str_3="Enter the first answer",
        polls_str_4="Send the next answer",
        polls_str_5="Enter the next answer and press'✅ Done'",
        polls_str_6="Oops, too many answers. There is one more option",
        polls_str_7="Thank you! Press '📤 Send' to allow users to take the poll.\n",
        polls_str_8="You haven't done the poll yet. Click 'Create'",
        polls_str_9="List of active polls",
        polls_str_10="Choose a poll to send to users",
        polls_str_11="Damn it, the poll is not sent 🤨 \n you have no users. Share the link of your bot in the social networks and  online resource or invite your friends. Somebody will come along soon 🐣",
        polls_str_12="✅ The poll is sent",
        polls_str_13="Choose a poll to view 📊 theresults",
        polls_str_14="🗑 Choose a poll to delete",
        polls_str_15="Press '🔙 Back' to cancel",
        polls_str_16=""" You haven't created a survey yet. \n
Click 'Create' or '🔙 Back'""",
        polls_str_17="🗑 Poll with name {} removed from all chats.",
        polls_str_18="These are the results. You can create a new poll or return to menu",
        polls_help_admin="""
Here you can:
🙌🏻 Create a poll
📊 Get the results
🗑 Delete the poll
📤 Send a poll to users
🚭 Smoking is prohibited


""",
        polls_module_str="Poll",

        pay_donation_str_admin="""
Here you can:
💸 Send payment
💰 Create a payment for yourself and notify the users of the bot
🛠 Set up payment


""",
        pay_donation_mode_str="Make a payment",
        pay_donation_str_1="How much do you want to pay? Enter the amount. ❗️ Cents and pennies separated by commas.",
        pay_donation_str_2="The main currency of the administrator ❗️ {}",
        allow_donation_text="Press '💰 Create a payment'\n'\
'or press '🔙 Back'",
        pay_donation_str_4="Admin has not yet set up payments 🤷‍ ",
        pay_donation_str_5="Oops, you entered the wrong number. Try again.",

        add_menu_module_button="Edit menu",
        manage_button_str_1="✏️Choose the button you want to edit or press '🔙 Back'",
        manage_button_str_2="Hopla, you haven't made the button yet. Press'📌 Create a button'",
        manage_button_str_3="✏️ Choose the content you want to replace",
        manage_button_str_4="Send a new content",
        manage_button_str_5="✅ Super! Content is updated",
        manage_button_str_6="🛑 You canceled the creation of a button.",

        edit_button_str_1="Enter a new 🤝 greeting for users",
        edit_button_str_2="✅ It's done.!",

        donations_edit_str_1="Test payment. Ignore it",
        donations_edit_str_2="What to do with the payment? Or press '🔙 Back",
        donations_edit_str_3="Yes, I'm sure.",
        donations_edit_str_4="No, cancel",
        donations_edit_str_5="🗑 Are you sure you want to delete this payment?",
        donations_edit_str_6="What exactly do you want to change? Or press '🔙 Back'",
        donations_edit_str_7="Write a new name for the payment. Or press '🔙 Back'",
        donations_edit_str_8="Do description of payment for users or write how you will utilize the money? Or press '🔙 Back'",
        donations_edit_str_9=" Choose the main currency. Or press '🔙 Back'",
        donations_edit_str_10="✅ It’s in the bag!",
        donations_edit_str_11="🗑 The payment is deleted",
        donations_edit_str_12="Enter a new token of your payment system",
        donations_edit_str_13="✅ New token updated!",
        donations_edit_str_14="Wrong token. Check it and send it again.",

        survey_str_1="Enter a name for the survey",
        survey_str_2="Write the first question",
        survey_str_3="The question with this name is already.\n" \
                     "Think of another name",
        survey_str_4="Write the next question or  press '✅ Done'",
        survey_str_5="Hi, please take the survey. It won't be long.\n" \
                     "Press '🏁 Start' to begin",
        survey_str_6="Created a survey called: {}\n" \
                     "{}" \
                     "\n Thanks, come again!",
        survey_str_7="This is a list of active surveys:",
        survey_str_8="Choose a survey to check 📊 results",
        survey_str_9=""" You haven't created a survey yet. \n
Press "Create" or '🔙 Back'""",
        survey_str_10='The name of the user: {},\nQuestion: {}\nAnswer :{} \n\n',
        survey_str_11="The data you requested: \n {}",
        survey_str_12="Wait until someone answers. =/",
        survey_str_13="Click '📤 Send' to remind users of the survey",
        survey_str_14="List of surveys:",
        survey_str_15="🗑 Choose a survey to delete ",
        survey_str_16="""You haven't created a survey yet. \n,
Press "Create" or '🔙 Back'""",
        survey_str_17="🗑 Survey called '{}' removed",
        survey_str_18="List of active surveys:",
        survey_str_19="Choose the survey you want to send to users",
        survey_str_20="Hi, please take the survey..\n" \
                      "Press '🏁 Start' to begin ",
        survey_str_21="Damn it, the survey is not sent 🤨 \n you have no users. Share the link of your bot in the social networks and  online resource or invite your friends. Somebody will come along soon 🐣",
        survey_str_22="✅ The survey is sent.",
        survey_str_23="""You haven't done the survey yet.\n
Press "Create" or '🔙 Back'""",
        survey_str_24="Survey has been deleted. You can create a new one or return to menu",

        create_donation_str_1="Test payment. Ignore it",
        create_donation_str_2="✏️ Write the name of the payment",
        create_donation_str_3="""How to get a token payment system:\n 1st Step: Go to @botfather and enter /mybots.
Choose your bot and press “Payments". Choose a provider. \nWe advise to use „Stripe“ because of low Acquiring
comisson for European card. \n2nd Step: Authorize yourself in the chatbot of the chosen provider. Just follow
instructions then you will get a token-access, that you should copy.\n3nd Step :Go back to your bot and create /newdonate.
Вставь токен: \n""",
        create_donation_str_4="✏️ Write the name of the payment",
        create_donation_str_5="Wrong token. Check it and send it again.",
        create_donation_str_6="Tell everyone about the fundraising and how you will utilize the money",
        create_donation_str_7="Choose the main currency",
        create_donation_str_8="✅Great! Now you can accept payments from bot users. ❗ ️Users only need a Bank card.\n" \
                              "Don't forget to tell about it.",

        answer_survey_str_1="Please answer the question.\n\n",
        answer_survey_str_2="Question:{}, Answer: {} \n",
        answer_survey_str_3="☺️ Thank you for answering my questions!\n",
        answer_survey_str_4="See you later!",
        survey_help_admin="""
Here you can:
❓ Create a survey\n
🗑 Delete a survey\n
📤 Send a survey to users\n
📊 The results of the survey.
""",
        survey_mode_str="Survey",

        edit_button_button="✏️ Edit",
        edit_menu_text="🤝 Change the greeting",
        add_menu_buttons_help="""
Here you can:\n
🙌🏻 Create a button to download any content. Show the users what you do.\n
🗑 Delete the button\n
✏️ Edit the button
""",
        add_menu_buttons_str_1="Write the name of the button or choose from the template.",
        add_menu_buttons_str_2='Send text, picture, document, video or music. ' \
                               '❗️ The text added to the description is not displayed in the button.',
        add_menu_buttons_str_3='A button with this name already exists. Think of another name.',
        add_menu_buttons_str_4="Great! Add something else.\n'\
'or press '✅ Done'",
        add_menu_buttons_str_5='✅Done! The button will be available in the title menu \n {}',
        add_menu_buttons_str_6="🗑 Choose the button you want to delete ",
        add_menu_buttons_str_7="""Oops. You don't have buttons yet. Click "Create""",
        add_menu_buttons_str_8='🗑 Button {} removed',
        add_menu_buttons_str_9="🛑 You canceled the creation of a button.",
        add_menu_buttons_str_10="You can crete a new button or return to menu",
        add_button="Add"),

    "RUS": dict(
        channels_str_1='Here u can manage your channels',
        channels_str_2='List of your channels',
        # Click "Add" to configure your first channel or "Back" for main menu
        no_channels='You have no channel configured yet. Click "Add channel" to configure your first channel',
        wrong_channel_link_format='Send me link or username of your channel. ' \
                                  'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"',
        bot_is_not_admin_of_channel='Bot is not admin in this({}) channel. ' \
                                    'Add bot as admin to the channel and then back to this menu ' \
                                    'and send me link or username of your channel. ' \
                                    'For Example "https://t.me/name" or "t.me/name" or "@name" or just "name"',
        bot_is_not_admin_of_channel_2="Bot is not admin in this({}) channel or can't send message to the channel" \
                                      "So channel was deleted. Add bot as admin to the channel, " \
                                      "let it send message to the channel " \
                                      "and then add channel again by Clicking 'Add channel'",
        channels_str_4="To add channel u need to add this bot as admin to your channel " \
                       "and then back to this menu and send " \
                       "link or username of your channel. " \
                       "Send me link or username of your channel",
        allow_bot_send_messages='U need to allow bot send messages to the channel. ' \
                                'And than back to this menu and send username of channel',
        no_such_channel='There are no such channel. ',
        choose_channel_to_remove='Choose channel you want to remove',
        channel_has_been_removed='Channel({}) has been deleted.',
        channel_added_success='Now you can send posts to the channel({}) using this commands.',
        choose_channel_to_post='Choose channel u want to post',
        post_message='What do u want to do?',
        send_post="What do you want to post on your channel({})?\n" \
                  "We will forward your message to channel.",
        choose_channel_to_send_poll='Choose channel u want to send poll',
        choose_channel_to_send_survey='Choose channel u want to send survey',
        try_to_add_already_exist_channel='This channel already exists',

        user_mode_help_admin="""
Нажми «Вкл», чтобы включить бота в режиме юзера.

Нажми «Выкл», чтобы вернутся в нормальный режим
""",
        user_mode_on_finish="✅ Готово, теперь посмотри на бот в режиме юзера",
        user_mode_off_finish="🔚 Режим юзера выключен",
        user_mode_str="Режим юзера",

        send_message_module_str="✉️ Сообщения",
        send_message_button_1="📤 Отправить сообщение",
        send_message_button_2="📥 Почтовый ящик",
        send_message_1="Напиши сообщение",
        send_message_2="Спасибо, голубь уже в пути 🕊!",
        send_message_3="Напиши сообщение юзерам\n" \
                       "Спасибо, голубь уже в пути 🕊!",
        send_message_4="Напиши новое сообщение или нажми '✅ Готово'",
        send_message_5="✅Сообщение отправлено",
        send_message_6="Полковнику никто не пишет 😉 ",
        send_message_admin="""
Здесь можно: 
📤 Отправить сообщение юзерам
📥 Проверить почту
🦖 Встретить динозавра

Отправь сообщение юзерам и получай обратную связь
""",
        send_message_user="""
Скажи «привет» админу!
""",
        send_donation_request_1="Расскажи всем про сбор денег и на что ты их потратишь\n" \
                                "К сообщению будет прикреплена кнопка 'Поддержать проект'",
        send_donation_request_2="Напиши новое сообщение или нажми '✅ Готово'",
        send_donation_request_3="💸 Сообщение отправлено!",

        answer_button_str="Ответить",
        cancel_button_survey="🔚 Отменить опрос",
        cancel_button="Отменить",
        remove_button="Удалить",
        send_survey_to_channel='Отправить открытый опрос',
        send_poll_to_channel='Отправить опрос',
        send_post_to_channel='Написать пост',
        donate_button="💰 Управлять платежами",
        back_button="🔙 Назад",
        done_button="✅ Готово",
        create_button="Создать",
        delete_button="🗑 Удалить",
        delete_button_str_all="Удалить все сообщения",
        delete_button_str_last_week="Удалить за послдению неделю",
        delete_button_str_last_month="Удалить за послдений месяц",
        send_button="📤 Отправить",
        results_button="📊 Результаты",
        menu_button="ℹ️ Меню",
        allow_donations_button=" 💰 Создать платёж",
        configure_button="🛠 Настройки",
        ask_donation_button="Попросить денег",
        title_button="Название",
        description_button="Описание",
        currency_button="Валюта",
        delete_donation_button="🗑 Удалить платёж",
        great_text="Отлично!",
        create_button_button="📌 Создать кнопку",
        edit_button="✏️ Редактировать",
        start_button="🏁 Старт",
        main_survey_button="Основной опрос",
        back_text="Нажми '🔙 Назад ', чтобы вернуться в меню ",
        polls_affirmations=[
            "Норм",
            "Круто",
            "Отлично",
            "Прекрасно",
            "Оки доки",
            "Изи пизи",
            "Юхуу",
            "Йоу",
            "Хорошо",
        ],
        polls_str_1='Введи название опроса',
        polls_str_2="Выбери тип опроса?",
        polls_str_3="Введи первый вариант ответа",
        polls_str_4="Отправь следующий вариант ответа",
        polls_str_5="Введи следующий ответ или нажми '✅ Готово'",
        polls_str_6="Упс, слишком много ответов. Остался ещё один вариант",
        polls_str_7="Спасибо! Нажми '📤 Отправить', чтобы юзеры прошли опрос.\n",
        polls_str_8="Ты ещё не сделал опрос. Нажми 'Создать'",
        polls_str_9="Список активных опросов",
        polls_str_10="Выбери опрос для отправки юзерам",
        polls_str_11="Блин, опрос не отправлен 🤨 \n У тебя ещё нет юзеров."
                     " Вставь ссылку на бота в соц. сетях и своих ресурсах или пригласи друзей."
                     " Скоро кто-нибудь придёт 🐣",
        polls_str_12="✅ Опрос отправлен",
        polls_str_13="Выбери опрос для просмотра 📊 результатов",
        polls_str_14="🗑 Выбери опрос для удаления",
        polls_str_15="Нажми '🔙 Назад' для отмены",
        polls_str_16=""" Ты ещё не создал опрос. \n
Нажми "Создать", или '🔙 Назад'""",
        polls_str_17="🗑 Опрос с названием {} удален из всех чатов.",
        polls_str_18=" Вот твои результаты. Можешь создать новый опрос или вернуться в гланое меню",
        polls_str_19=" Никто еще не проголосовал. Ждем результатов",

        polls_help_admin="""
Здесь можно:
🙌🏻 Создать опрос
📊 Узнать результаты
🗑 Удалить опрос
📤 Отправить опрос юзерам 
🚭 Курить запрещено

""",
        polls_module_str="Опрос",

        pay_donation_str_admin="""
Здесь можно:
💸 Отправить платёж
💰 Создать платёж для себя и оповестить об этом юзеров бота
🛠 Настроить платёж

""",
        pay_donation_mode_str="Сделать платёж",
        pay_donation_str_1="Сколько ты хочешь заплатить? Введи сумму. ❗️ Центы и копейки через запятую.",
        pay_donation_str_2="Основная валюта админа ❗️ {}",
        allow_donation_text="""Хопла, ты ещё не создал платёж \n 
                       Нажми ' Создать платёж' или нажми '🔙 Назад'""",
        pay_donation_str_4="Админ ещё не настроил платежи 🤷‍♂️ ",
        pay_donation_str_5="Упс, ты ввёл неправильное число. Попробуй ещё раз. Может через запятую?",

        manage_button_str_1="✏️Выбери кнопку, которую хочешь отредактировать или нажми '🔙 Назад'",
        manage_button_str_2="Хопла, ты ещё не сделал кнопку. Нажми '📌 Создать кнопку'",
        manage_button_str_3="✏️ Выбери контент, который хочешь заменить",
        manage_button_str_4="Отправь новый контент",
        manage_button_str_5="✅ Супер! Контент обновлён",
        manage_button_str_6="🛑 Ты отменил создание кнопки",

        edit_button_str_1="Введи новое 🤝 приветствие для юзеров",
        edit_button_str_2="✅ Дело сделано!",

        donations_edit_str_1="Тестовый платёж. Не обращай внимание",
        donations_edit_str_2="Что сделать с платежом? Или нажми '🔙 Назад'",
        donations_edit_str_3="Да, уверен",
        donations_edit_str_4="Нет, отменить",
        donations_edit_str_5="🗑 Уверен, что хочешь удалить этот платёж?",
        donations_edit_str_6="Что именно ты хочешь изменить? Или нажми '🔙 Назад'",
        donations_edit_str_7="Напиши новое название для платежа. Или нажми '🔙 Назад'",
        donations_edit_str_8="Сделай описание платежа для юзеров или напиши, "
                             "на что ты потратишь деньги?  Или нажми '🔙 Назад'",
        donations_edit_str_9=" Выбери основную валюту расчёта. Или нажми '🔙 Назад'",
        donations_edit_str_10="✅ Дело в шляпе",
        donations_edit_str_11="🗑 Платёж удалён",
        donations_edit_str_12="Введи новый токен твоей платёжной системы",
        donations_edit_str_13="✅ Новый токен обновлён!",
        donations_edit_str_14="Неправильный токен. Проверь его и отправь снова.",
        send_donation_request_button="Попросить пользователей о донате",
        survey_str_1="Введи название для опроса с открытым ответом",
        survey_str_2="Напиши первый вопрос",
        survey_str_3="Вопрос с таким названием уже есть.\n" \
                     "Придумай другое название",
        survey_str_4="Напиши следующий вопрос или нажми '✅ Готово'",
        survey_str_5="Привет, пройди, пожалуйста, опрос. Это недолго.\n" \
                     "Нажми '🏁 Старт', чтобы начать ",
        survey_str_6="Создан опрос с названием: {}\n" \
                     "{}" \
                     "\nСпасибо, приходи ещё!",
        survey_str_7="Это список активных опросов с открытым ответом:",
        survey_str_8="Выбери опрос чтобы проверить 📊 результаты",
        survey_str_9=""" Ты ещё не создал опрос. \n
Нажми "Создать", или '🔙 Назад'""",
        survey_str_10='Имя юзера: {},\nВопрос: {}\nОтвет :{} \n\n',
        survey_str_11="Данные, которые ты запрашивал: \n {}",
        survey_str_12="Подожди, пока ещё никто не ответил =/",
        survey_str_13="Нажми '📤 Отправить', чтобы напомнить юзерам об опросе",
        survey_str_14="Список активных опросов с открытым ответом:",
        survey_str_15="🗑 Выбери опрос для удаления ",
        survey_str_16="""Ты ещё не создал опрос. \n
Нажми "Создать", или '🔙 Назад'""",
        survey_str_17="🗑 Опрос с названием '{}' удалён",
        survey_str_18="Список активных опросов с открытым ответом:",
        survey_str_19="Выбери опрос, который хочешь отправить юзерам",
        survey_str_20="Привет, пройди, пожалуйста, опрос.\n" \
                      "Нажми '🏁 Старт', чтобы начать ",
        survey_str_21="Упс, опрос не отправлен 🤨 \n "
                      "У тебя ещё нет юзеров. Вставь ссылку на бота в соц. сетях "
                      "и своих ресурсах или пригласи друзей. Скоро кто-нибудь придёт 🐣",
        survey_str_22="✅ Опрос отправлен",
        survey_str_23="""Ты ещё не сделал опрос.\n
Нажми "Создать", или '🔙 Назад'""",
        survey_str_24="Твой опрос был удален. Можешь создать новый или перейти в главное меню",
        create_donation_str_1="Тестовый платёж. Не обращай внимание",
        create_donation_str_2="✏️ Напиши название платежа",
        create_donation_str_3="""Как получить токен платёжной системы:\n 1st Step: Go to @botfather and enter /mybots. 
Choose your bot and press “Payments”. Choose a provider. \nWe advise to use „Stripe“ because of low Acquiring 
comisson for European card. \n2nd Step: Authorize yourself in the chatbot of the chosen provider. Just follow 
instructions then you will get a token-access, that you should copy.\n3nd Step :Go back to your bot and create /newdonate. 
Вставь токен: \n""",
        create_donation_str_4="✏️ Напиши название платежа",
        create_donation_str_5="Неправильный токен. Проверь его и отправь снова.",
        create_donation_str_6="Сделай описание платежа для юзеров или напиши на что ты потратишь деньги?",
        create_donation_str_7="Выбери основную валюту расчёта",
        create_donation_str_8="✅Отлично! Теперь ты можешь принимать платежи от юзеров бота. ❗️Юзерам нужна лишь банковская карта.\nНе забудь рассказать об этом.",

        answer_survey_str_1="Будь добр, ответь на вопрос.\n\n",
        answer_survey_str_2="Вопрос:{}, Ответ: {} \n",
        answer_survey_str_3="☺️ Спасибо за ответы!\n",
        answer_survey_str_4="Увидимся!",
        survey_help_admin="""
Здесь можно:
❓ Создать опрос с открытым ответом \n
🗑 Удалить опрос\n
📤 Отправить опрос юзерам\n
📊 Узнать результаты опроса
""",
        survey_mode_str="Открытый опрос",
        add_menu_module_button="Редактировать меню",
        edit_button_button="✏️ Редактировать",
        edit_menu_text="🤝 Изменить приветствие",
        add_menu_buttons_help="""
Здесь можно:\n
🙌🏻 Создать кнопку для загрузки любого контента. Покажи юзерам, чем ты занимаешься.\n
🗑 Удалить кнопку\n
✏️ Редактировать кнопку
""",
        add_menu_buttons_str_1="Напиши название кнопки или выбери из шаблона.",
        add_menu_buttons_str_2='Отправь текст, картинку, документ, видео или музыку. '
                               '❗️ Текст, добавленный к описанию, не отображается в кнопке.',
        add_menu_buttons_str_3='Кнопка с этим названием уже есть. Придумай другое название',
        add_menu_buttons_str_4="Отлично! Добавь что-нибудь ещё.\n или нажми  '✅ Готово' ",
        add_menu_buttons_str_5='✅Сделано! Кнопка будет доступна в меню названием \n {}',
        add_menu_buttons_str_6="🗑 Выбери кнопку, которую хочешь удалить ",
        add_menu_buttons_str_7="""Упс. У тебя ещё нет кнопок.Нажми "Создать""",
        add_menu_buttons_str_8='🗑 Кнопка {} удалена',
        add_menu_buttons_str_9="🛑 Ты отменил создание кнопки",
        add_menu_buttons_str_10="Можешь создать нувую кнопку или вернуться в меню",

        add_button="Добавить"
    )}


def string_dict(bot):
    chatbot = chatbots_table.find_one({"bot_id": bot.id})
    return string_dict_dict[chatbot["lang"]]
