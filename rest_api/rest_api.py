# #!/usr/bin/env python3
# -*- coding: utf-8 -*
import falcon
import requests
from wsgiref import simple_server
from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['chatbots']
chatbots_table = db["chatbots"]
users_table = db['users']


class ThingsResource(object):
    # {'admins': [{'email': 'popov@gmail.com', 'password': '4PIl4FUDCzn'}], 'requireNext': None, 'welcomeForm': [],
    #  'finished': True, 'buttons': [], '_id': '5cc25547a9a63e710b0c456a', 'superuser': 244356086,
    #  'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg', 'name': 'Crowdbot', 'welcomeMessage': 'he'}

    def on_post(self, req, resp):

        """Handles POST requests"""
        doc = {}
        if req.content_length:
            doc = falcon.json.load(req.stream)
        token = doc["token"]
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(token))
        doc["bot_id"] = chatbot.json()['result']['id']
        db["chatbots"].save(doc)

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
                    db["users"].update({"user_id": admin["user_id"]}, admin, upsert=True)
                elif "email" in admin:
                    db["users"].update({"email": admin["email"]}, admin, upsert=True)
                else:
                    db["users"].save(admin)
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
        db["users"].delete_many({"bot_id": chatbot_id})
        db["chatbots"].delete_many({"bot_id": chatbot_id})
        db['donations_table'].delete_many({"bot_id": chatbot_id})
        db['setpoll_instances'].delete_many({"bot_id": chatbot_id})
        db['setpolls'].delete_many({"bot_id": chatbot_id})
        db['tags'].delete_many({"bot_id": chatbot_id})
        db["surveys"].delete_many({"bot_id": chatbot_id})
        db["custom_commands"].delete_many({"bot_id": chatbot_id})
        db['payments_requests_table'].delete_many({"bot_id": chatbot_id})
        db['payments_table'].delete_many({"bot_id": chatbot_id})
        db["chats"].delete_many({"bot_id": chatbot_id})
        resp.status = falcon.HTTP_200


class AdminResource(object):
    def on_delete(self, req, resp):
        # doc = {}
        # if req.content_length:
        #
        doc = req.params  #  {token: bot.token, email: chat.changeRequest.payload}
        print(req.params)
        print(req.stream)
        """Handles DELETE requests"""
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(doc["token"])
                                  ).json()
        chatbot_id = chatbot["result"]["id"]
        db["users"].delete_many({"bot_id": chatbot_id, "email": doc["email"]})
        resp.status = falcon.HTTP_200


app = falcon.API()
things = ThingsResource()
admins = AdminResource()
app.add_route('/chatbot', things)
app.add_route('/chatbot/admin', admins)


if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
