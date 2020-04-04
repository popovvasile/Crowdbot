# #!/usr/bin/env python3
# -*- coding: utf-8 -*
from datetime import datetime

from flask import Flask, request, Response, make_response
import requests
from pymongo import MongoClient

app = Flask(__name__)
client = MongoClient('localhost', 27017)

crowdbot_db = client['crowdbot_chatbots']
crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]
donations_table = crowdbot_db['donations_table']
users_table = crowdbot_db['users']


# TODO
#       /crowdbot  [GET, POST, DELETE]
#       /crowdbots -> [GET]
#       /user_bots -> [GET]


def format_for_response(chatbot):
    """
    Adds "admins" field with admin data to chatbot dict.
    """
    chatbot["admins"] = list()
    for admin in users_table.find({"is_admin": True, "superuser": False}):
        chatbot["admins"].append(convert_types(admin))
    return convert_types(chatbot)


def convert_types(obj):
    """
    Converts ObjectId and datetime fields in Mongo Document to string.
    """
    if obj.get("_id"):
        obj["_id"] = str(obj["_id"])
    if obj.get("creation_timestamp"):
        obj["creation_timestamp"] = str(obj["creation_timestamp"])
    if obj.get("timestamp"):
        obj["timestamp"] = str(obj["timestamp"])
    return obj


@app.route("/user_bots/<int:user_id>", methods=["GET"])
def user_bots(user_id):
    """
    Get bots by user_id. Only for admins.
    """
    return make_response((
        {"result": [format_for_response(chatbot) for chatbot
                    in crowdbot_bots_table.find({"superuser": user_id})]},
        200))


# todo pagination
@app.route("/crowdbots", methods=["GET"])
def get_all_bots():
    """
    Get all bots
    """
    return make_response((
        {"result": [format_for_response(chatbot)
                    for chatbot in crowdbot_bots_table.find()]},
        200))


@app.route("/crowdbot/<string:token>", methods=["GET"])
def crowdbot_on_get(token):
    """
    Get bot by token.
    """
    telegram_check = requests.get(url=f"https://api.telegram.org/"
                                      f"bot{token}/getMe").json()
    if not telegram_check.get("ok"):
        resp = make_response(({"message": "Token Error",
                               "result": telegram_check},
                              telegram_check["error_code"]))
    else:
        chatbot = crowdbot_bots_table.find_one(
            {"bot_id": telegram_check["result"]["id"]})
        resp = make_response(
            ({"message": "Bot Exist",
              "result": format_for_response(chatbot)}, 200)
            if chatbot
            else ({"message": "Bot Does Not Exist",
                   "result": telegram_check}, 404))
    return resp


@app.route('/crowdbot', methods=['POST'])
def crowdbot_on_post():
    """
    Save bot and admins data to database.

    Request json must looks like:

        {"params": {"bot": {"token": str,
                            "welcomeMessage": str,
                            "buttons": list,
                            "lang": str,
                            "superuser": int},
                    "admins": list}}
    """
    doc = request.get_json()["params"]
    telegram_check = requests.get(f"https://api.telegram.org/bot"
                                  f"{doc['bot']['token']}/getMe").json()
    if telegram_check["ok"]:
        chatbot = doc["bot"]
        chatbot["bot_id"] = telegram_check["result"]["id"]
        chatbot["username"] = telegram_check["result"]["username"]
        chatbot["name"] = telegram_check["result"]["first_name"]
        chatbot["active"] = True
        chatbot["shop_enabled"] = False
        chatbot["donations_enabled"] = False
        chatbot["creation_timestamp"] = datetime.now()
        crowdbot_bots_table.save(chatbot)  # TODO replace with update

        doc["admins"].append(dict(user_id=chatbot["superuser"]))
        for admin in doc["admins"]:
            admin["bot_id"] = chatbot["bot_id"]
            admin["registered"] = False
            admin["is_admin"] = True
            admin["superuser"] = admin.get("user_id") == chatbot["superuser"]
            if "user_id" in admin:
                users_table.update({"user_id": admin["user_id"],
                                    "bot_id": chatbot["bot_id"]},
                                   admin, upsert=True)
            else:
                users_table.save(admin)
        telegram_check["result"] = format_for_response(chatbot)
        return make_response((telegram_check, 200))
    else:
        return make_response((telegram_check, telegram_check["error_code"]))


@app.route('/crowdbot', methods=['DELETE'])
def on_delete():
    doc = request.args
    chatbot_id = requests.get(url="https://api.telegram.org/"
                                  "bot{}/getMe".format(doc["token"])).json()
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
    resp = Response({"ok": True}, status=200, mimetype='application/json')
    return resp


@app.route('/crowdbot', methods=['PUT'])
def crowdbot_on_put():  # TODO
    crowdbot_doc = request.get_json()["params"]
    chatbot = crowdbot_bots_table.find_one({"bot_id": crowdbot_doc["bot_id"]})
    chatbot.update(crowdbot_doc)
    crowdbot_bots_table.update_one(
        {"token": crowdbot_doc["token"]}, chatbot)
    resp = Response({"ok": True}, status=200, mimetype='application/json')
    return resp

# ADMIN MANAGE ENDPOINTS AND ONE PUT METHOD FOR BOTS
'''



@app.route('/crowdbot/admin', methods=['POST'])
def admin_on_post():
    # {"token": str,
    #  "admins": [{
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
'''

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
