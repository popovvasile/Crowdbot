# -*- coding: utf-8 -*-
from __future__ import absolute_import
from multiprocessing import Process
from pymongo import MongoClient
import time
from main_runner import main

client = MongoClient('localhost', 27017)
crowdbot_db = client['crowdbot_chatbots']
crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]


def multiple_bot_daemon():  # todo if token wrong- don't start it and notify
    my_process = {}
    print(crowdbot_bots_table.find().count())
    while True:
        # Crowdbot
        for doc in crowdbot_bots_table.find():  # run all tokens when the script is running
            if doc["token"] not in list(my_process.keys()):
                if doc["lang"] == "ENG":
                    print(doc["token"])
                    new_process = Process(target=main, args=(doc["token"],
                                                             doc["lang"]), name=doc["token"])
                    new_process.start()
                    my_process[doc["token"]] = new_process
                elif doc["lang"] == "RUS":
                    print(doc["token"])
                    new_process = Process(target=main, args=(doc["token"],
                                                             doc["lang"]), name=doc["token"])
                    new_process.start()
                    my_process[doc["token"]] = new_process

        time.sleep(10)


if __name__ == '__main__':
    multiple_bot_daemon()
