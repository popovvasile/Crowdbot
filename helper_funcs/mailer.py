"""
**********************************************
WITH NEW REGISTRATION THIS FILE CAN BE REMOVED

"""
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pprint import pprint
from database import chatbots_table


button_style = "background-color: #4CAF50; "\
               "font-size: 12px; "\
               "border-radius: 8px; "\
               "text-align: center;"\
               "display: inline-block;"

email_text = {
    "ENG": dict(
        subject='ChatNetwork Bot one-time password',
        html_content="<b>Hello,</b>"
                     "<p>You have been added by the admin to the bot <b>{bot_name}.</b></p>"
                     "To get rights:"
                     "<ul style='list-style-type:disc;'>"
                     "<li><b>Start a conversation with the bot or click button: </b>"
                     "<a href='https://t.me/{bot_username}?start=registration'>"
                     f"<button style='{button_style}'>Log in</button></a></li>"
                     "<li><b>Send to the bot your email address</b></li>"
                     "<li><b>Insert the one-time password: {password}</b></li>"
                     "</ul>" 
                     "<br>"
                     "If you encounter any difficulties, feel free to contact our <b>support team: t.me/CrowdRobot</b>"
                     "<p><i>Ignore this letter if it is not addressed to you.</i></p>"
                     "<p>Best regards,</p>"
                     "<p><b>CrowdRobot Team</b></p>",
        plain_text_content="Hello,"
                           "\nYou have been added by the admin to the bot {bot_name}."
                           "\nTo get rights:"
                           "\n• Start a conversation with the bot or follow the link:"
                           "\nhttps://t.me/{bot_username}?start=registration"
                           "\n• Send to the bot your email address"
                           "\n• Insert the one-time password: {password}"
                           "\n\nIf you encounter any difficulties, feel free to "
                           "contact our support team: t.me/CrowdRobot"
                           "\nIgnore this letter if it is not addressed to you."
                           "\nBest regards,"
                           "\nCrowdRobot Team"
    ),

    "RUS": dict(
        subject='ChatNetwork Одноразовый пароль бота',
        html_content="<b>Привет,</b>"
                     "<p>Тебя добавили админом в бот <b>{bot_name}.</b></p>"
                     "Чтобы получить права:"
                     "<ul style='list-style-type:disc;'>"
                     "<li><b>Открой диалог с ботом или нажми кнопку: </b>"
                     "<a href='https://t.me/{bot_username}?start=registration'>"
                     f"<button style='{button_style}'>Войти</button></a></li>"
                     "<li><b>Напиши боту адрес своей почты</b></li>"
                     "<li><b>Вставь одноразовый пароль: {password}</b></li>"
                     "</ul>" 
                     "<br>"
                     "Если возникнут проблемы, то пиши в <b>Саппорт: t.me/CrowdRobot</b>"
                     "<p><i>Проигнорируй это письмо, если оно адресовано не тебе.</i></p>"
                     "<p>С Уважением,</p>" 
                     "<p><b>Команда CrowdRobot</b></p>",
        plain_text_content="Привет,"
                           "\nТебя добавили админом в бот {bot_name}. "
                           "\nЧтобы получить права:"
                           "\n• Открой диалог с ботом"
                           "\n• Напиши боту адрес своей почты или перейди по ссылке:"
                           "\nhttps://t.me/{bot_username}?start=registration"
                           "\n• Вставь одноразовый пароль: {password}"
                           "\n\nЕсли возникнут проблемы, то пиши в Саппорт: t.me/CrowdRobot"
                           "\nПроигнорируй это письмо, если оно адресовано не тебе."
                           "\nС Уважением,"
                           "\nКоманда CrowdRobot"
    )}


# https://realpython.com/python-send-email/#loop-over-rows-to-send-multiple-emails
class SMTPMailer:
    def __init__(self):
        self.port = 465  # 1025  # 587
        self.smtp_server = 'smtp.gmail.com'

        # self.password = "cgbyjpfcgbyjpsx"
        # self.sender = "cbnetwo@gmail.com"

        # self.password = "swsuzlfmtbukmnti"
        self.password = "cmlafwciqyfhwpvo"
        self.sender = "crowdrobot.telegram@gmail.com"

    def send_registration_msgs(self, context, admins_data: list):
        chat_bot = chatbots_table.find_one({"bot_id": context.bot.id})
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender, self.password)
            for admin in admins_data:
                try:
                    message = MIMEMultipart("alternative")
                    message["Subject"] = email_text[chat_bot["lang"]]["subject"]
                    message["From"] = self.sender
                    message["To"] = admin["email"]
                    message.attach(
                        MIMEText(email_text[chat_bot["lang"]]["plain_text_content"].format(
                            bot_name=chat_bot["name"],
                            bot_username=chat_bot["username"],
                            password=admin["password"]), "plain"))
                    message.attach(
                        MIMEText(email_text[chat_bot["lang"]]["html_content"].format(
                            bot_name=chat_bot["name"],
                            bot_username=chat_bot["username"],
                            password=admin["password"]), "html"))
                    server.sendmail(self.sender, admin["email"], message.as_string())
                    print(f"Message sent: {admin['email']}")
                except Exception as e:
                    print('Mailer Exception', e)
