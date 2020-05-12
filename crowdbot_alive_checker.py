# -*- coding: utf-8 -*-
from __future__ import absolute_import
from multiprocessing import Process
import time

from database import chatbots_table
from main_runner import main


def multiple_bot_daemon():  # todo if token wrong- don't start it and notify
    my_process = {}
    print(chatbots_table.count_documents({"active": True}))
    while True:
        # Crowdbot
        for doc in chatbots_table.find({"active": True}):
            # run all active tokens when the script is running
            # "active" means that a bot did not experience an "Unauthorized" error (token not valid)
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

        for process_key in list(my_process):  # stop the unused tokens
            list_of_tokens = [d['token'] for d in chatbots_table.find({"active": True})
                              if 'token' in d]
            if process_key not in list_of_tokens:
                my_process[process_key].terminate()
                my_process.pop(process_key, None)

        time.sleep(10)


if __name__ == '__main__':
    multiple_bot_daemon()
