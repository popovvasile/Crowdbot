from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content, To, From

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import aiosmtplib


class MessageText(object):
    def __init__(self):
        self.subject = 'ChatNetwork Bot one-time password'

        self.html_content = "<p>Hello and welcome to the ChatBotNetwork!<br/>" \
                            "You've been added as an admin to a newly created bot {}. " \
                            "To get the access, open the bot's dialog and send it " \
                            "the following one-time pass: {}<br/>" \
                            "You won't need this password afterwards<br/>" \
                            "<br/>" \
                            "Kind regards, <br/>" \
                            "CBN Team</p>"

        self.plain_text_content = "Hello and welcome to the ChatBotNetwork!\n" \
                                  "You've been added as an admin to a newly created bot {}. " \
                                  "To get the access, open the bot's dialog and send it the " \
                                  "following one-time pass: {}\n " \
                                  "You won't need this password afterwards\n" \
                                  "\n" \
                                  "Kind regards, \n" \
                                  "CBN Team"


# Send Messages To Spam
# https://github.com/sendgrid/sendgrid-python
class SendGridMailer(MessageText):
    def __init__(self):
        super(SendGridMailer, self).__init__()
        self.sg = SendGridAPIClient('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')
        self.from_email = 'keikoobro@gmail.com'

    def regular_send(self, admins, bot_name):
        for admin in admins:
            message = Mail(
                from_email=self.from_email,
                to_emails=admin['email'],
                subject=self.subject,
                html_content=self.html_content.format(bot_name, admin['password']),
                plain_text_content=self.plain_text_content.format(bot_name, admin['password']))
            try:
                response = self.sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)

    # Asynchronous Mail Send
    #  https://github.com/sendgrid/sendgrid-python/blob/master/use_cases/asynchronous_mail_send.md
    async def send_email(self, n, email):
        try:
            resp = self.sg.send(email)
            if resp.status_code < 300:
                print(f'Email #{n} processed ', resp.body, resp.status_code)
        except Exception as e:
            print(e)

    @asyncio.coroutine
    def send_many(self, admins, bot_name):
        emails = [Mail(From(self.from_email),
                       To(admin['email']),
                       self.subject,
                       Content('text/html',
                               self.html_content.format(bot_name, admin['password'])),
                       Content('text/plain',
                               self.plain_text_content.format(bot_name, admin['password'])))
                  for admin in admins]

        print('START - sending emails ...')
        for n, em in enumerate(emails):
            asyncio.ensure_future(self.send_email(n, em))
        print('END - returning control...')

    def send(self, admins, bot_name):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = asyncio.ensure_future(self.send_many(admins, bot_name))
        loop.run_until_complete(task)
        loop.close()
        return 'HERE IS RETURN'


# https://realpython.com/python-send-email/#loop-over-rows-to-send-multiple-emails
class SMTPMailer(MessageText):
    def __init__(self):
        super(SMTPMailer, self).__init__()
        self.port = 465  # 1025  # 587
        self.smtp_server = 'smtp.gmail.com'
        self.password = 'zlxpmffqskodrsca'
        self.sender = 'keikoobro@gmail.com'

    def send(self, admins, bot_name):
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(self.sender, self.password)
            for admin in admins:
                try:
                    message = MIMEMultipart('alternative')
                    message['Subject'] = self.subject
                    message['From'] = self.sender
                    message['To'] = admin['email']
                    message.attach(
                        MIMEText(self.plain_text_content.format(
                            bot_name, admin['password']), 'plain'))
                    message.attach(
                        MIMEText(self.html_content.format(
                            bot_name, admin['password']), 'html'))
                    server.sendmail(self.sender, admin['email'], message.as_string())
                    print(f"Message sent: {admin['email']}")
                except Exception as e:
                    print('Mailer Exception', e)

    # Asynchronous Mail Send
    # https://howto.lintel.in/sending-asynchronous-emails-using-twisted-part-2/
    # https: // aiosmtplib.readthedocs.io / en / stable / overview.html
    async def async_sending(self, admins, bot_name, loop):
        for admin in admins:
            message = MIMEMultipart('alternative')
            message['Subject'] = self.subject
            message['From'] = self.sender
            message['To'] = admin['email']
            message.attach(
                MIMEText(self.plain_text_content.format(
                    bot_name, admin['password']), 'plain'))
            message.attach(
                MIMEText(self.html_content.format(
                    bot_name, admin['password']), 'html'))
            async with aiosmtplib.SMTP(hostname=self.smtp_server,
                                       port=self.port,
                                       loop=loop,
                                       use_tls=True) as server:
                await server.login(self.sender, self.password)
                await server.send_message(message)
                print(f"Message sent: {admin['email']}")

    def send_async(self, admins, bot_name):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.async_sending(admins, bot_name, loop))

    """
    async def async_sending(self, admins, bot_name, loop):
        async with aiosmtplib.SMTP(hostname=self.smtp_server,
                                   port=self.port,
                                   loop=loop,
                                   use_tls=True) as server:
            await server.login(self.sender, self.password)
            for admin in admins:
                message = MIMEMultipart('alternative')
                message['Subject'] = self.subject
                message['From'] = self.sender
                message['To'] = admin['email']
                message.attach(
                    MIMEText(self.plain_text_content.format(
                        bot_name, admin['password']), 'plain'))
                message.attach(
                    MIMEText(self.html_content.format(
                        bot_name, admin['password']), 'html'))

                await server.send_message(message)
                print(f"Message sent: {admin['email']}")

    def send_async(self, admins, bot_name):
        loop = asyncio.new_event_loop()
        smtp = aiosmtplib.SMTP(hostname="smtp.gmail.com", port=465, loop=loop, use_tls=True)
        smtp.login(self.sender, self.password)
        asyncio.set_event_loop(loop)
        loop.run_until_complete(smtp.connect())
        for admin in admins:
            message = MIMEMultipart('alternative')
            message['Subject'] = self.subject
            message['From'] = self.sender
            message['To'] = admin['email']
            message.attach(
                MIMEText(self.plain_text_content.format(
                    bot_name, admin['password']), 'plain'))
            message.attach(
                MIMEText(self.html_content.format(
                    bot_name, admin['password']), 'html'))

            loop.run_until_complete(smtp.send_message(message))
    """

