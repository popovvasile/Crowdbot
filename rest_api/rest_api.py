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
    def on_post(self, req, resp):
        """Handles POST requests"""
        doc = {}
        if req.content_length:
            doc = falcon.json.load(req.stream)
        print(doc)
        token = doc["token"]
        chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(token))
        if chatbot.ok:
            if chatbots_table.find_one({"token": doc["token"]}):
                pass
            else:

                doc["bot_id"] = chatbot.json()['result']['id']
                db["chatbots"].save(doc)
                superadmin = dict()
                superadmin["bot_id"] = doc["bot_id"]
                superadmin["registered"] = False
                superadmin["is_admin"] = True
                superadmin["is_superuser"] = True
                superadmin["user_id"] = doc["superuser"]
                db["users"].save(superadmin)
                for admin in doc["admins"]:  # TODO check for the fullname and for email
                    admin["bot_id"] = doc["bot_id"]
                    admin["registered"] = False
                    admin["is_admin"] = True

                    db["users"].save(admin)
                resp.status = falcon.HTTP_200

    def on_delete(self, req, resp):
        """Handles POST requests"""
        chatbot_id = requests.get(url="https://api.telegram.org/bot{}/getMe".format(req.data["token"])
                                  ).json()["results"]["id"]
        db["users"].delete_all({"bot_id": chatbot_id})
        db["chatbots"].delete_all({"bot_id": chatbot_id})
        db['donations_table'].delete_all({"bot_id": chatbot_id})
        db['setpoll_instances'].delete_all({"bot_id": chatbot_id})
        db['setpolls'].delete_all({"bot_id": chatbot_id})
        db['tags'].delete_all({"bot_id": chatbot_id})
        db["surveys"].delete_all({"bot_id": chatbot_id})
        db["custom_commands"].delete_all({"bot_id": chatbot_id})
        db['payments_requests_table'].delete_all({"bot_id": chatbot_id})
        db['payments_table'].delete_all({"bot_id": chatbot_id})
        db["chats"].delete_all({"bot_id": chatbot_id})
        resp.status = falcon.HTTP_200


app = falcon.API()
things = ThingsResource()
app.add_route('/chatbot', things)


if __name__ == '__main__':
    httpd = simple_server.make_server('127.0.0.1', 8000, app)
    httpd.serve_forever()
