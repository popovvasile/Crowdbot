# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from multiprocessing import Process
from pymongo import MongoClient
import time
from main_runner import main
import gc

client = MongoClient('localhost', 27017)
crowdbot_db = client['crowdbot_chatbots']
crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]


def multiple_bot_daemon():
    my_process = {}
    print(crowdbot_bots_table.find().count())
    while True:
        # Crowdbot
        for doc in crowdbot_bots_table.find():  # run all tokens when the script is running
            if doc["token"] not in list(my_process.keys()):
                if doc["lang"] == "ENG":
                    print(doc["token"])
                    new_env = os.environ
                    new_env["LANG"] = "ENG"
                    new_process = Process(target=main, args=(doc["token"], 8001+len(my_process)+1), name=doc["token"])
                    new_process.start()
                    my_process[doc["token"]] = new_process
                elif doc["lang"] == "RUS":
                    print("TEST")
                    new_env = os.environ
                    new_env["LANG"] = "RUS"
                    new_process = Process(target=main, args=(doc["token"], 8001+len(my_process)+1), name=doc["token"])
                    new_process.start()
                    my_process[doc["token"]] = new_process

        for process_key in list(my_process):  # stop the unused tokens
            list_of_tokens = [d['token'] for d in crowdbot_bots_table.find() if 'token' in d]
            if process_key not in list_of_tokens:
                my_process[process_key].terminate()
                my_process.pop(process_key, None)
        gc.collect()
        time.sleep(10)


if __name__ == '__main__':
    multiple_bot_daemon()
