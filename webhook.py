from queue import Queue  # in python 2 it should be "from Queue"
from threading import Thread

from telegram import Bot
from telegram.ext import Dispatcher


def setup(token):  # TODO Task for Yuria - create a webhook for Telegram
    # Create bot, update queue and dispatcher instances
    bot = Bot(token)
    update_queue = Queue()

    dispatcher = Dispatcher(bot, update_queue)
    ##### Register handlers here #####

    # Start the thread
    thread = Thread(target=dispatcher.start, name='dispatcher')
    thread.start()

    return update_queue
    # you might want to return dispatcher as well,
    # to stop it at server shutdown, or to register more handlers:
    # return (update_queue, dispatcher)
