# #!/usr/bin/env python3
# -*- coding: utf-8 -*
from flask import Flask, request, Response
import requests
from pymongo import MongoClient
from pprint import pprint

app = Flask(__name__)
client = MongoClient('localhost', 27017)
# TODO for the russian version, change the name of the database with sufix rus_
crowdbot_db = client['crowdbot_chatbots']
crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]
donations_table = crowdbot_db['donations_table']
users_table = crowdbot_db['users']
# 104.248.82.166

# {'admins': [{'email': 'popov@gmail.com', 'password': '4PIl4FUDCzn'}], 'requireNext': None, 'welcomeForm': [],
#  'finished': True, 'buttons': [], '_id': '5cc25547a9a63e710b0c456a', 'superuser': 244356086,
#  'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg', 'name': 'Crowdbot', 'welcomeMessage': 'he'}
# language: [Russian, English], crowdbot_token: token, shop_token: token


@app.route('/crowdbot', methods=['GET'])
def crowdbot_on_get():  # TODO
    crowdbot_doc = request.get_json()["params"]
    chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(crowdbot_doc["token"]))
    crowdbot_doc["bot_id"] = chatbot.json()['result']['id']
    resp = Response(donations_table.find_many({"bot_id": crowdbot_doc["bot_id"]}),
                    status=200, mimetype='application/json')
    return resp


@app.route('/crowdbot', methods=['PUT'])
def crowdbot_on_put():  # TODO
    crowdbot_doc = request.get_json()["params"]

    chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(crowdbot_doc["token"]))
    crowdbot_doc["bot_id"] = chatbot.json()['result']['id']

    crowdbot_bots_table.update_one({"bot_id": crowdbot_doc["bot_id"]}, crowdbot_doc)
    resp = Response({"ok": True}, status=200, mimetype='application/json')
    return resp


@app.route('/crowdbot', methods=['POST'])
def crowdbot_on_post():

    doc = request.get_json()["params"]
    print(doc)
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
    resp = Response({"ok": True}, status=200, mimetype='application/json')
    return resp


@app.route('/crowdbot', methods=['DELETE'])
def on_delete():
    doc = request.args
    print(doc)
    chatbot_id = requests.get(url="https://api.telegram.org/bot{}/getMe".format(doc["token"])).json()
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
    resp = Response({"ready": True}, status=200, mimetype='application/json')
    return resp


@app.route('/crowdbot/admin', methods=['POST'])
def admin_on_post():
    # {"token": str,
    #  "admins": [{"email": doc["email"],
    #              "password": doc["password"],
    #              "active": doc["active"]}]
    #   }
    doc = request.get_json()  # {token: bot.token, email: chat.changeRequest.payload}
    """Handles POST requests"""
    chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(doc["token"])
                           ).json()
    chatbot_id = chatbot["result"]["id"]

    for admin in doc['admins']:
        users_table.insert_one({"bot_id": chatbot_id,
                                "email": admin["email"],
                                "password": admin["password"],
                                "registered": False,
                                "is_admin": True,
        })

    resp = Response({}, status=200, mimetype='application/json')
    return resp


@app.route('/crowdbot/admin', methods=['DELETE'])
def admin_on_delete():
    doc = request.get_json()["params"]  # {token: bot.token, email: chat.changeRequest.payload}
    chatbot = requests.get(url="https://api.telegram.org/bot{}/getMe".format(doc["token"])
                           ).json()
    chatbot_id = chatbot["result"]["id"]
    users_table.delete_many({"bot_id": chatbot_id, "email": doc["email"]})
    # resp.status = falcon.HTTP_200
    resp = Response({}, status=200, mimetype='application/json')
    return resp


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
