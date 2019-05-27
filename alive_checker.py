# -*- coding: utf-8 -*-
from __future__ import absolute_import
from multiprocessing import Process
from pymongo import MongoClient
# import main_bot.main_interface.bot_runner
import time

from main_runner import main
# from tg_bot.__main__ import main
# from testi import main
client = MongoClient('localhost', 27017)
db = client['chatbots']  # TODO make two different clients or not


def multiple_bot_daemon():  # TODO adjust to webhook
    my_process = {}
    print(db["chatbots"].find().count())
    while True:
        for doc in db["chatbots"].find():  # run all tokens when the script is running
            if doc["token"] not in list(my_process):
                new_process = Process(target=main, args=(doc["token"],), name=doc["token"])
                new_process.start()
                my_process[doc["token"]] = new_process

        for key, process in my_process.items():
            if not process.is_alive():
                doc = dict()
                doc["token"] = key
                new_process = Process(target=main, args=(doc,), name=doc["token"])
                new_process.start()
                my_process[doc["token"]] = new_process
                print("restarted process " + doc["token"])
        for process_key in list(my_process):  # run all tokens when the script is running
            list_of_tokens = [d['token'] for d in db["chatbots"].find() if 'token' in d]
            if process_key not in list_of_tokens:
                my_process[process_key].terminate()
                my_process.pop(process_key, None)
        time.sleep(2)


if __name__ == '__main__':
    multiple_bot_daemon()
