# #!/usr/bin/env python3
# -*- coding: utf-8 -*
import falcon
import requests
from wsgiref import simple_server
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
# TODO for the russian version, change the name of the database with sufix rus_
shop_db = client['shop_chatbots']
shop_bots_table = shop_db["shop_chatbots"]

crowdbot_db = client['crowdbot_chatbots']
crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]

users_table = crowdbot_db['users']


class CrowdbotResource(object):
    # {'admins': [{'email': 'popov@gmail.com', 'password': '4PIl4FUDCzn'}], 'requireNext': None, 'welcomeForm': [],
    #  'finished': True, 'buttons': [], '_id': '5cc25547a9a63e710b0c456a', 'superuser': 244356086,
    #  'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg', 'name': 'Crowdbot', 'welcomeMessage': 'he'}
    # language: [Russian, English], crowdbot_token: token, shop_token: token
    def on_get(self, req, resp):  # TODO
        crowdbot_doc = {}
        if req.content_length:
            crowdbot_doc = falcon.json.load(req.stream)
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(crowdbot_doc["token"]))
        crowdbot_doc["bot_id"] = chatbot.json()['result']['id']
        chatbot = shop_bots_table.find_one({"bot_id": crowdbot_doc["bot_id"]})
        resp.body = {"active": chatbot["active"],
                     "total_amount": chatbot["total_amount"],
                     "last_update": chatbot["last_update"]
                     }
        resp.status = falcon.HTTP_200

    def on_put(self, req, resp):  # TODO
        crowdbot_doc = {}
        if req.content_length:
            crowdbot_doc = falcon.json.load(req.stream)
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(crowdbot_doc["token"]))
        crowdbot_doc["bot_id"] = chatbot.json()['result']['id']

        crowdbot_bots_table.update_one({"bot_id": crowdbot_doc["bot_id"]}, crowdbot_doc)
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        doc = {}
        if req.content_length:
            doc = falcon.json.load(req.stream)
        # Crowdbot token
        print(doc)
        doc.pop("token", None)
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
        crowdbot_bots_table["users"].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table["chatbots"].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table['donations_table'].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table['setpoll_instances'].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table['setpolls'].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table['tags'].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table["surveys"].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table["custom_commands"].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table['payments_requests_table'].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table['payments_table'].delete_many({"bot_id": chatbot_id})
        crowdbot_bots_table["chats"].delete_many({"bot_id": chatbot_id})
        resp.status = falcon.HTTP_200


class ShopResource(object):
    def on_get(self, req, resp):  # TODO
        shop_doc = {}
        if req.content_length:
            shop_doc = falcon.json.load(req.stream)
        chatbot = shop_bots_table.find({"bot_id": shop_doc["bot_id"]})
        resp.body = {"active": chatbot["active"],
                     "total_amount": chatbot["total_amount"],
                     "last_update": chatbot["last_update"]
                     }
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        # Shop token
        shop_doc = {}
        if req.content_length:
            shop_doc = falcon.json.load(req.stream)
        print(shop_doc)
        shop_doc.pop("token", None)
        shop_token = shop_doc["token"]
        shop_chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(shop_token))
        shop_doc["bot_id"] = shop_chatbot.json()['result']['id']
        shop_bots_table.save(shop_doc)
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp):
        print(req.params)
        chatbot_id = requests.get(url="https://api.telegram.org/bot{}/getMe".format(req.params["token"])
                                  ).json()
        chatbot_id = chatbot_id["result"]["id"]
        shop_bots_table.delete_many({"bot_id": chatbot_id})
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
shop_things = ShopResource()
admins = AdminResource()
app.add_route('/crowdbot', crowdbot_things)

app.add_route('/crowdbot/admin', admins)
app.add_route('/shopbot', shop_things)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)   # todo two different ports for two languages
    httpd.serve_forever()
