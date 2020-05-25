# -*- coding: utf-8 -*-
import time
from multiprocessing import Process
from main_webhook import create_dispatchers
# from database import chatbots_table


def main():
    app = create_dispatchers()

    app.run(host='0.0.0.0',
            port=8443,
            ssl_context=('cert.pem', 'private.key'))


def multiple_bot_daemon():  # todo if token wrong- don't start it and notify
    while True:
        # Crowdbot
        new_process = Process(target=main)
        new_process.start()

        time.sleep(86400)  # 24h
        new_process.terminate()
        if new_process.is_alive() is False:
            new_process = Process(target=main)
            new_process.start()
            time.sleep(86400)


if __name__ == '__main__':
    multiple_bot_daemon()

