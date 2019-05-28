# -*- coding: utf-8 -*-
from __future__ import absolute_import
from multiprocessing import Process
from pymongo import MongoClient
import time
from main_runner import main
from shop.core import shop_main

client = MongoClient('localhost', 27017)
shop_db = client['shop_chatbots']
shop_bots_table = shop_db["shop_chatbots"]

crowdbot_db = client['crowdbot_chatbots']
crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]


def multiple_bot_daemon():
    my_process = {}
    print(crowdbot_db["chatbots"].find().count())
    while True:
        # Crowdbot
        for doc in crowdbot_bots_table.find({"active": True}):  # run all tokens when the script is running
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
        for process_key in list(my_process):  # stop the unused tokens
            list_of_tokens = [d['token'] for d in crowdbot_bots_table.find({"active": True}) if 'token' in d]
            if process_key not in list_of_tokens:
                my_process[process_key].terminate()
                my_process.pop(process_key, None)

        # Shop
        for doc in shop_bots_table.find({"active": True}):  # run all tokens when the script is running
            if doc["token"] not in list(my_process):
                new_process = Process(target=shop_main, args=(doc["token"],), name=doc["token"])
                new_process.start()
                my_process[doc["token"]] = new_process

        for key, process in my_process.items():
            if not process.is_alive():
                doc = dict()
                doc["token"] = key
                new_process = Process(target=shop_main, args=(doc,), name=doc["token"])
                new_process.start()
                my_process[doc["token"]] = new_process
                print("restarted process " + doc["token"])
        for process_key in list(my_process):  # stop the unused tokens
            list_of_tokens = [d['token'] for d in shop_bots_table.find({"active": True}) if 'token' in d]
            if process_key not in list_of_tokens:
                my_process[process_key].terminate()
                my_process.pop(process_key, None)
        time.sleep(2)


if __name__ == '__main__':
    multiple_bot_daemon()
