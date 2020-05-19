import time
from queue import Queue
from threading import Thread
from flask import Flask, request

import logging

from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def start_handler(update, context):
    # Creating a handler-function for /start command
    logger.info("User {} started bot".format(update.effective_user["id"]))
    update.message.reply_text("Hello from Python!\nPress /random to get random number")


tokens = ["502301506:AAGIuV3XCZuOrIhiCPhRdWXNK5ehWMueizI",
          "364462454:AAHcEYiM95KGzHMt-6agNmB2uoZFGxa-m2Q"]

megadict = {}


def setup():
    app = Flask(__name__)
    for token in tokens:
        bot = Bot(token=token)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue, use_context=True)
        # Commands for admin
        dp.add_handler(CommandHandler('start', start_handler))
        megadict.update({token: {
            "queue": update_queue,
            "dispatcher": dp,
            "bot": bot
        }})
        s = bot.set_webhook(url='https://64.227.14.144:8443/' + token,
                            certificate=open('cert.pem', 'rb'))
        if s:
            print(s)
            logger.info('webhook setup ok')
        else:
            print(s)
            logger.info('webhook setup failed')

        def webhook():
            if request.headers.get('content-type') == 'application/json':
                dp_dict = megadict[request.path[1:]]
                update = Update.de_json(request.get_json(force=True), dp_dict["bot"])
                logger.info('Update received! ' + str(update))
                dp_dict["queue"].put(update)
            return 'OK'
        app.add_url_rule(rule='/{}'.format(token),
                         endpoint=token,
                         view_func=webhook,
                         methods=['POST'])
        # thread = Thread(target=dp.start, name=token)
        # thread.start()
        # @app.route('/hook/' + token, methods=['POST'])
        #time.sleep(1)
    return app


webhook = setup()
for token in megadict.values():
    dp = token["dispatcher"]
    thread = Thread(target=dp.start, name=dp.bot.username)
    thread.start()

webhook.run(host='0.0.0.0',
            port=8443,
            ssl_context=('cert.pem', 'private.key'))
