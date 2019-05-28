# #!/usr/bin/env python3
# -*- coding: utf-8 -*
import falcon
import requests
from wsgiref import simple_server
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
shop_db = client['shop_chatbots']
shop_bots_table = shop_db["shop_chatbots"]

crowdbot_db = client['crowdbot_chatbots']
crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]

users_table = crowdbot_db['users']


class ChatbotResource(object):
    # TODO create a POST endpoint to pause the chatbot if not paid "active" + in the botfather- add the option "pause the bot"
    # TODO make different enpoints for shop and crowdbot
    # TODO credit card token for shop
    # {'admins': [{'email': 'popov@gmail.com', 'password': '4PIl4FUDCzn'}], 'requireNext': None, 'welcomeForm': [],
    #  'finished': True, 'buttons': [], '_id': '5cc25547a9a63e710b0c456a', 'superuser': 244356086,
    #  'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg', 'name': 'Crowdbot', 'welcomeMessage': 'he'}
    # language: [Russian, English], crowdbot_token: token, shop_token: token
    def on_post(self, req, resp):

        """Handles POST requests"""
        doc = {}
        if req.content_length:
            doc = falcon.json.load(req.stream)
        # Crowdbot token
        doc.pop("token", None)
        crowdbot_token = doc["token"]
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(crowdbot_token))
        doc["bot_id"] = chatbot.json()['result']['id']
        crowdbot_bots_table.save(doc)

        # Shop token
        shop_doc = {}
        if req.content_length:
            shop_doc = falcon.json.load(req.stream)
        shop_doc.pop("token", None)
        shop_token = shop_doc["token"]
        shop_chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(shop_token))
        shop_doc["bot_id"] = shop_chatbot.json()['result']['id']
        shop_bots_table.save(shop_doc)

        if chatbot.ok:
            superadmin = dict()
            superadmin["bot_id"] = doc["bot_id"]
            superadmin["registered"] = False
            superadmin["is_admin"] = True
            superadmin["is_superuser"] = True
            superadmin["user_id"] = doc["superuser"]
            doc["admins"].append(superadmin)
            for admin in doc["admins"]:  # TODO check for the fullname and for email
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
        # {'admins[]': ['{"email":"po@gmail.co"', '"password":"NThLDLf1Xqz"}'], 'finished': 'true',
        #  'buttons[]': ['Discography', 'Concerts', 'Battles', 'New Projects', 'Live photos'],
        #  '_id': '"5cd835f0522bc511ad555ffe"', 'superuser': '244356086',
        #  'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg', 'name': 'Crowdbot', 'welcomeMessage': 'hi'}

        """Handles DELETE requests"""
        chatbot_id = requests.get(url="https://api.telegram.org/bot{}/getMe".format(req.params["token"])
                                  ).json()
        chatbot_id = chatbot_id["result"]["id"]
        if crowdbot_bots_table.find({"bot_id": chatbot_id}).count() != 0:
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
        else:
            shop_bots_table.delete_many({"bot_id": chatbot_id})
            resp.status = falcon.HTTP_200


class AdminResource(object):
    def on_post(self, req, resp):
        doc = req.params  # {token: bot.token, email: chat.changeRequest.payload}
        print(req.params)
        print(req.stream)
        """Handles DELETE requests"""
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(doc["token"])
                               ).json()
        chatbot_id = chatbot["result"]["id"]
        users_table.insert_one({"bot_id": chatbot_id, "email": doc["email"], "password": doc["password"]})
        resp.status = falcon.HTTP_200

    def on_delete(self, req, resp):
        doc = req.params  # {token: bot.token, email: chat.changeRequest.payload}
        """Handles DELETE requests"""
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(doc["token"])
                               ).json()
        chatbot_id = chatbot["result"]["id"]
        users_table.delete_many({"bot_id": chatbot_id, "email": doc["email"]})
        resp.status = falcon.HTTP_200


app = falcon.API()
things = ChatbotResource()
admins = AdminResource()
app.add_route('/chatbot', things)
app.add_route('/chatbot/admin', admins)

if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
