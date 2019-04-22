from queue import Queue
from threading import Thread
from flask import Flask, request

import logging
import os
from datetime import time
from telegram import Bot, Update
from telegram.ext import Dispatcher, CommandHandler, Filters

from nasa_api_bot.config import conf

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def get_info(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text=str(bot.get_webhook_info()))


def setup():
    bot = Bot(token=conf['BOT_TOKEN'])
    update_queue = Queue()
    dp = Dispatcher(bot, update_queue)

    s = bot.set_webhook(url='https://142.93.109.14:5000/hook/' + conf['BOT_TOKEN'])
    if s:
        print(s)
        logger.info('webhook setup ok')
    else:
        print(s)
        logger.info('webhook setup failed')

    thread = Thread(target=dp.start, name='dispatcher')
    thread.start()

    return update_queue, bot


update_queue, bot = setup()

app = Flask(__name__)


@app.route('/hook/' + conf['BOT_TOKEN'], methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = Update.de_json(request.get_json(force=True), bot)
        logger.info('Update received! ' + str(update))
        update_queue.put(update)
    return 'OK'


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=conf['PORT'])
