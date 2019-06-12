# import requests
# import json
#
# #
# # print(requests.post('http://localhost:8000/crowdbot',
# #                     data=json.dumps({u'params': {u'superuser': 244356086, u'name': u'DemoBot', u'finished': True,
# #                                                  u'welcomeMessage': u'vfdbgf', u'buttons': [u'Idea ', u'Business plan ',
# #                                                                                             u'Outlay  ', u'Team  '],
# #                                                  u'admins': [{u'password': u'0yb3I5vhy0r', u'email': u'po@hmail.com'}],
# #                                                  u'token': u'633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg',
# #                                                  u'requireNext': None, u'_id': u'5cf1fcfe11ff5d12f5018e43'}})))
# # requests.delete('127.0.0.1:8000/chatbot',
# #                 data={'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg'})
# #
# #
# # requests.post('127.0.0.1:8000/chatbot/admin', data={"token": "token",
# #                                                     "email": "popovvasile@gmail.com",
# #                                                     "password": "password"})
# # requests.delete('127.0.0.1:8000/chatbot/admin', data={"token": "token",
# #                                                       "email": "popovvasile@gmail.com"})



user_mode_help_admin = """
Нажми «Вкл», чтобы включить бота в режиме юзера.

Нажми «Выкл», чтобы вернутся в нормальный режим
"""
user_mode_on_finish = "✅ Готово, теперь посмотри на бот в режиме юзера"
user_mode_off_finish = "🔚 Режим юзера выключен"
user_mode_str = "Режим юзера"

send_message_module_str = "✉️ Сообщения"
send_message_button_1 = "📤 Отправить сообщение"
send_message_button_2 = "📥 Почтовый ящик"
send_message_1 = "Напиши сообщение"
send_message_2 = "Спасибо, голубь уже в пути 🕊!"
send_message_3 = "Напиши сообщение юзерам\n" \
                 "Спасибо, голубь уже в пути 🕊!"
send_message_4 = "Напиши новое сообщение или нажми '✅ Готово'"
send_message_5 = "✅Сообщение отправлено"
send_message_6 = "Полковнику никто не пишет 😉 "
send_message_admin = """
Здесь можно: 
📤 Отправить сообщение юзерам
📥 Проверить почту
🦖 Встретить динозавра

Отправь сообщение юзерам и получай обратную связь
"""
send_message_user = """
Скажи «привет» админу!
"""
send_donation_request_1 = "Расскажи всем про сбор денег и на что ты их потратишь\n" \
                          "К сообщению будет прикреплена кнопка 'Поддержать проект'"
send_donation_request_2 = "Напиши новое сообщение или нажми '✅ Готово'"
send_donation_request_3 = "💸 Сообщение отправлено!"

cancel_button_survey = "🔚 Отменить опрос"
donate_button = "💰 Управлять платежами"
back_button = "🔙 Назад"
done_button = "✅ Готово"
create_button = "Создать"
delete_button = "🗑 Удалить"
send_button = "📤 Отправить"
results_button = "📊 Результаты"
menu_button = "ℹ️ Меню"
allow_donations_button = " 💰 Создать платёж"
configure_button = "🛠 Настройки"
ask_donation_button = "Попросить денег"
title_button = "Название"
description_button = "Описание"
currency_button = "Валюта"
delete_donation_button = "🗑 Удалить платёж"
great_text = "Отлично!"
create_button_button = "📌 Создать кнопку "
edit_button = "✏️ Редактировать"
start_button = "🏁 Старт"
main_survey_button = "Основной опрос"
back_text = "Нажми '🔙 Назад ', чтобы вернуться в меню "
polls_affirmations = [
    "Норм",
    "Круто",
    "Отлично",
    "Прекрасно",
    "Оки доки",
    "Изи пизи",
    "Юхуу",
    "Йоу",
    "Хорошо",
]
polls_str_1 = 'Введи название опроса'
polls_str_2 = "Выбери тип опроса?"
polls_str_3 = "Введи первый вариант ответа"
polls_str_4 = "Отправь следующий вариант ответа"
polls_str_5 = "Введи следующий ответ или нажми '✅ Готово'"
polls_str_6 = "Упс, слишком много ответов. Остался ещё один вариант"
polls_str_7 = "Спасибо! Нажми '📤 Отправить', чтобы юзеры прошли опрос.\n"
polls_str_8 = "Ты ещё не сделал опрос. Нажми 'Создать'"
polls_str_9 = "Список активных опросов"
polls_str_10 = "Выбери опрос для отправки юзерам"
polls_str_11 = "Блин, опрос не отправлен 🤨 \n У тебя ещё нет юзеров. Вставь ссылку на бота в соц. сетях и своих ресурсах или пригласи друзей. Скоро кто-нибудь придёт 🐣"
polls_str_12 = "✅ Опрос отправлен"
polls_str_13 = "Выбери опрос для просмотра 📊 результатов"
polls_str_14 = "🗑 Выбери опрос для удаления"
polls_str_15 = "Нажми '🔙 Назад' для отмены"
polls_str_16 = """ Ты ещё не создал опрос. \n
Нажми "Создать" или '🔙 Назад'"""
polls_str_17 = "🗑 Опрос с названием {} удален из всех чатов."
polls_help_admin = """
Здесь можно:
🙌🏻 Создать опрос
📊 Узнать результаты
🗑 Удалить опрос
📤 Отправить опрос юзерам 
🚭 Курить запрещено

"""
polls_module_str = "Опрос"

pay_donation_str_admin = """
Здесь можно:
💸 Отправить платёж
💰 Создать платёж для себя и оповестить об этом юзеров бота
🛠 Настроить платёж

"""
pay_donation_mode_str = "Сделать платёж"
pay_donation_str_1 = "Сколько ты хочешь заплатить? Введи сумму. ❗️ Центы и копейки через запятую."
pay_donation_str_2 = "Основная валюта админа ❗️ {}"
allow_donation_text = """Хопла, ты ещё не создал платёж \n" \
                      'Нажми '💰 Создать
платёж
'\n' \
'или нажми '🔙 Назад
'"""
pay_donation_str_4 = "Админ ещё не настроил платежи 🤷‍♂️ "
pay_donation_str_5 = "Упс, ты ввёл неправильное число. Попробуй ещё раз. Может через запятую?"

manage_button_str_1 = "✏️Выбери кнопку, которую хочешь отредактировать или нажми '🔙 Назад'"
manage_button_str_2 = "Хопла, ты ещё не сделал кнопку. Нажми '📌 Создать кнопку'"
manage_button_str_3 = "✏️ Выбери контент, который хочешь заменить"
manage_button_str_4 = "Отправь новый контент"
manage_button_str_5 = "✅ Супер! Контент обновлён"
manage_button_str_6 = "🛑 Ты отменил создание кнопки"

edit_button_str_1 = "Введи новое 🤝 приветствие для юзеров"
edit_button_str_2 = "✅ Дело сделано!"

donations_edit_str_1 = "Тестовый платёж. Не обращай внимание"
donations_edit_str_2 = "Что сделать с платежом? Или нажми '🔙 Назад'"
donations_edit_str_3 = "Да, уверен"
donations_edit_str_4 = "Нет, отменить"
donations_edit_str_5 = "🗑 Уверен, что хочешь удалить этот платёж?"
donations_edit_str_6 = "Что именно ты хочешь изменить? Или нажми '🔙 Назад'"
donations_edit_str_7 = "Напиши новое название для платежа. Или нажми '🔙 Назад'"
donations_edit_str_8 = "Сделай описание платежа для юзеров или напиши, на что ты потратишь деньги?  Или нажми '🔙 Назад'"
donations_edit_str_9 = " Выбери основную валюту расчёта. Или нажми '🔙 Назад'"
donations_edit_str_10 = "✅ Дело в шляпе"
donations_edit_str_11 = "🗑 Платёж удалён"
donations_edit_str_12 = "Введи новый токен твоей платёжной системы"
donations_edit_str_13 = "✅ Новый токен обновлён!"
donations_edit_str_14 = "Неправильный токен. Проверь его и отправь снова."

survey_str_1 = "Введи название для опроса с открытым ответом"
survey_str_2 = "Напиши первый вопрос"
survey_str_3 = "Вопрос с таким названием уже есть.\n" \
               "Придумай другое название"
survey_str_4 = "Напиши следующий вопрос или нажми '✅ Готово'"
survey_str_5 = "Привет, пройди, пожалуйста, опрос. Это недолго.\n" \
               "Нажми '🏁 Старт', чтобы начать "
survey_str_6 = "Создан опрос с названием: {}\n" \
               "{}" \
               "\nСпасибо, приходи ещё!"
survey_str_7 = "Это список активных опросов с открытым ответом:"
survey_str_8 = "Выбери опрос чтобы проверить 📊 результаты"
survey_str_9 = """ Ты ещё не создал опрос. \n
Нажми "Создать" или '🔙 Назад'"""
survey_str_10 = 'Имя юзера: {},\nВопрос: {}\nОтвет :{} \n\n'
survey_str_11 = "Данные, которые ты запрашивал: \n {}"
survey_str_12 = "Подожди, пока ещё никто не ответил =/"
survey_str_13 = "Нажми '📤 Отправить', чтобы напомнить юзерам об опросе"
survey_str_14 = "Список активных опросов с открытым ответом:"
survey_str_15 = "🗑 Выбери опрос для удаления "
survey_str_16 = """Ты ещё не создал опрос. \n
Нажми "Создать" или '🔙 Назад'"""
survey_str_17 = "🗑 Опрос с названием '{}' удалён"
survey_str_18 = "Список активных опросов с открытым ответом:"
survey_str_19 = "Выбери опрос, который хочешь отправить юзерам"
survey_str_20 = "Привет, пройди, пожалуйста, опрос.\n" \
                "Нажми '🏁 Старт', чтобы начать "
survey_str_21 = "Упс, опрос не отправлен 🤨 \n У тебя ещё нет юзеров. Вставь ссылку на бота в соц. сетях и своих ресурсах или пригласи друзей. Скоро кто-нибудь придёт 🐣"
survey_str_22 = "✅ Опрос отправлен"
survey_str_23 = """Ты ещё не сделал опрос.\n
Нажми "Создать" или '🔙 Назад'"""

create_donation_str_1 = "Тестовый платёж. Не обращай внимание"
create_donation_str_2 = "✏️ Напиши название платежа"
create_donation_str_3 = """Как получить токен платёжной системы:\n 1st Step: Go to @botfather and enter /mybots. 
Choose your bot and press “Payments”. Choose a provider. \nWe advise to use „Stripe“ because of low Acquiring 
comisson for European card. \n2nd Step: Authorize yourself in the chatbot of the chosen provider. Just follow 
instructions then you will get a token-access, that you should copy.\n3nd Step :Go back to your bot and create /newdonate. 
Вставь токен: \n"""
create_donation_str_4 = "✏️ Напиши название платежа"
create_donation_str_5 = "Неправильный токен. Проверь его и отправь снова."
create_donation_str_6 = "Сделай описание платежа для юзеров или напиши на что ты потратишь деньги?"
create_donation_str_7 = "Выбери основную валюту расчёта"
create_donation_str_8 = "✅Отлично! Теперь ты можешь принимать платежи от юзеров бота. ❗️Юзерам нужна лишь банковская карта.\n" \
                        "Не забудь рассказать об этом."

answer_survey_str_1 = "Будь добр, ответь на вопрос.\n\n"
answer_survey_str_2 = "Вопрос:{}, Ответ: {} \n"
answer_survey_str_3 = "☺️ Спасибо за ответы!\n"
answer_survey_str_4 = "Увидимся!"
survey_help_admin = """
Здесь можно:
❓ Создать опрос с открытым ответом \n
🗑 Удалить опрос\n
📤 Отправить опрос юзерам\n
📊 Узнать результаты опроса
"""
survey_mode_str = "Открытый опрос"

edit_button_button = "✏️ Редактировать"
edit_menu_text = "🤝 Изменить приветствие"
add_menu_buttons_help = """
Здесь можно:\n
🙌🏻 Создать кнопку для загрузки любого контента. Покажи юзерам, чем ты занимаешься.\n
🗑 Удалить кнопку\n
✏️ Редактировать кнопку
"""
add_menu_buttons_str_1 = "Напиши название кнопки или выбери из шаблона."
add_menu_buttons_str_2 = 'Отправь текст, картинку, документ, видео или музыку. ' \
                         '❗️ Текст, добавленный к описанию, не отображается в кнопке.'
add_menu_buttons_str_3 = 'Кнопка с этим названием уже есть. Придумай другое название'
add_menu_buttons_str_4 = "Отлично! Добавь что-нибудь ещё.\n'\
                                  'или нажми '✅ Готово'"
add_menu_buttons_str_5 = '✅Сделано! Кнопка будет доступна в меню названием \n {}'
add_menu_buttons_str_6 = "🗑 Выбери кнопку, которую хочешь удалить "
add_menu_buttons_str_7 = """Упс. У тебя ещё нет кнопок.Нажми "Создать"""
add_menu_buttons_str_8 = '🗑 Кнопка {} удалена'
add_menu_buttons_str_9 = "🛑 Ты отменил создание кнопки"
add_menu_buttons_str_10 = "Можешь создать нувую кнопку или вернуться в меню"
