# #!/usr/bin/env python3
# -*- coding: utf-8 -*
import json

import falcon
import requests
from wsgiref import simple_server
from pymongo import MongoClient


client = MongoClient('localhost', 27017)
# TODO for the russian version, change the name of the database with sufix rus_
crowdbot_db = client['crowdbot_chatbots']
crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]
donations_table = crowdbot_db['donations_table']
users_table = crowdbot_db['users']


class CrowdbotResource(object):
    # {'admins': [{'email': 'popov@gmail.com', 'password': '4PIl4FUDCzn'}], 'requireNext': None, 'welcomeForm': [],
    #  'finished': True, 'buttons': [], '_id': '5cc25547a9a63e710b0c456a', 'superuser': 244356086,
    #  'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg', 'name': 'Crowdbot', 'welcomeMessage': 'he'}
    # language: [Russian, English], crowdbot_token: token, shop_token: token
    def on_get(self, req, resp):  # TODO
        crowdbot_doc = json.loads(req.stream.read().decode('utf-8'))["params"]
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(crowdbot_doc["token"]))
        crowdbot_doc["bot_id"] = chatbot.json()['result']['id']
        chatbot = crowdbot_bots_table.find_one({"bot_id": crowdbot_doc["bot_id"]})
        resp.body = donations_table.find_many({"bot_id": crowdbot_doc["bot_id"]})
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp):  # TODO
        crowdbot_doc = json.loads(req.stream.read().decode('utf-8'))["params"]

        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(crowdbot_doc["token"]))
        crowdbot_doc["bot_id"] = chatbot.json()['result']['id']

        crowdbot_bots_table.update_one({"bot_id": crowdbot_doc["bot_id"]}, crowdbot_doc)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        doc = json.loads(req.stream.read().decode('utf-8'))["params"]
        # Crowdbot token
        crowdbot_token = doc["token"]
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(crowdbot_token))
        doc["bot_id"] = chatbot.json()['result']['id']
        crowdbot_bots_table.save(doc)  # TODO replace with update

        if chatbot.ok:
            superadmin = dict()
            superadmin["bot_id"] = doc["bot_id"]
            superadmin["registered"] = False
            superadmin["is_admin"] = True
            superadmin["is_superuser"] = True
            superadmin["user_id"] = doc["superuser"]
            doc["admins"].append(superadmin)
            for admin in doc["admins"]:
                print(admin)
                print(doc["admins"])
                admin["bot_id"] = doc["bot_id"]
                admin["registered"] = False
                admin["is_admin"] = True
                if "user_id" in admin:
                    users_table.update({"user_id": admin["user_id"]}, admin, upsert=True)
                elif "email" in admin:
                    users_table.update({"email": admin["email"]}, admin, upsert=True)
                else:
                    users_table.save(admin)
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp):
        chatbot_id = requests.get(url="https://api.telegram.org/bot{}/getMe".format(req.params["token"])
                                  ).json()

        chatbot_id = chatbot_id["result"]["id"]
        crowdbot_db["users"].delete_many({"bot_id": chatbot_id})
        crowdbot_db["crowdbot_chatbots"].delete_many({"bot_id": chatbot_id})
        crowdbot_db['donations_table'].delete_many({"bot_id": chatbot_id})
        crowdbot_db['setpoll_instances'].delete_many({"bot_id": chatbot_id})
        crowdbot_db['setpolls'].delete_many({"bot_id": chatbot_id})
        crowdbot_db['tags'].delete_many({"bot_id": chatbot_id})
        crowdbot_db["surveys"].delete_many({"bot_id": chatbot_id})
        crowdbot_db["custom_commands"].delete_many({"bot_id": chatbot_id})
        crowdbot_db['payments_requests_table'].delete_many({"bot_id": chatbot_id})
        crowdbot_db['payments_table'].delete_many({"bot_id": chatbot_id})
        crowdbot_db["chats"].delete_many({"bot_id": chatbot_id})
        resp.status = falcon.HTTP_200


class AdminResource(object):
    def on_post(self, req, resp):
        doc = req.params  # {token: bot.token, email: chat.changeRequest.payload}
        print(req.params)
        print(req.stream)
        """Handles POST requests"""
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(doc["token"])
                               ).json()
        chatbot_id = chatbot["result"]["id"]
        users_table.insert_one({"bot_id": chatbot_id,
                                "email": doc["email"],
                                "password": doc["password"],
                                "active": doc["active"]})  # TODO update
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp):
        doc = req.params  # {token: bot.token, email: chat.changeRequest.payload}
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(doc["token"])
                               ).json()
        chatbot_id = chatbot["result"]["id"]
        users_table.delete_many({"bot_id": chatbot_id, "email": doc["email"]})
        resp.status = falcon.HTTP_200


app = falcon.API()
crowdbot_things = CrowdbotResource()
admins = AdminResource()
app.add_route('/crowdbot', crowdbot_things)
app.add_route('/crowdbot/admin', admins)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)   # todo two different ports for two languages
    httpd.serve_forever()
