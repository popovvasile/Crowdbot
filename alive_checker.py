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
db = client['chatbots']
# doc = db["admin_chats"].find_one({"token": "511539263:AAFT8Bpu-yoP0qaWXXJouzLT4QPcof_8hqI"})
#
#
# def multiple_bot_daemon():
#     my_process = {}
#
#     while True:
#         for doc in db["chatbots"].find():  # run all tokens when the script is running
#             if doc["token"] not in my_process.keys():
#                 new_process = Process(target=main, args=(doc["token"],), name=doc["token"])
#                 new_process.start()
#                 my_process[doc["token"]] = new_process
#                 # print(my_process)
#                 # print(doc["token"])
#
#         for key, process in my_process.items():
#             if not process.is_alive():
#                 doc = dict()
#                 doc["token"] = key
#                 new_process = Process(target=main, args=(doc,), name=doc["token"])
#                 new_process.start()
#                 my_process[doc["token"]] = new_process
#                 # print "restarted process " + doc["token"]
#         time.sleep(2)


if __name__ == '__main__':
    # multiple_bot_daemon()
    main("633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg")
