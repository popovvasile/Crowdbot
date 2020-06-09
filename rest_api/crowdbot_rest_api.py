# #!/usr/bin/env python3
# -*- coding: utf-8 -*
import os
from datetime import datetime
from pprint import pprint

from flask import Flask, request, Response, make_response
import requests
from pymongo import MongoClient


app = Flask(__name__)
client = MongoClient('localhost', 27017)

if os.environ['SHOP_PRODUCTION'] == "1":
    crowdbot_db = client['crowdbot_chatbots']
else:
    crowdbot_db = client['crowdbot_chatbots_test']

crowdbot_bots_table = crowdbot_db["crowdbot_chatbots"]
donations_table = crowdbot_db['donations_table']
users_table = crowdbot_db['users']


def format_for_response(chatbot: dict) -> dict:
    """Adds additional fields to chatbot dict."""
    active_users = users_table.find({"bot_id": chatbot["bot_id"],
                                     "is_admin": False,
                                     "blocked": False,
                                     "unsubscribed": False})

    not_active_users = users_table.find(
        {"$or": [{"bot_id": chatbot["bot_id"], "is_admin": False, "blocked": True},
                 {"bot_id": chatbot["bot_id"], "is_admin": False, "unsubscribed": True}]
         })

    admins = users_table.find({"bot_id": chatbot["bot_id"],
                               "is_admin": True,
                               "superuser": False})

    chatbot["total_active_users"] = active_users.count()
    chatbot["total_not_active_users"] = not_active_users.count()
    chatbot["admins"] = list(map(convert_types, admins))
    return convert_types(chatbot)


def convert_types(obj: dict) -> dict:
    """Converts ObjectId and datetime fields in Mongo Document to string."""
    if obj.get("_id"):
        obj["_id"] = str(obj["_id"])
    if obj.get("creation_timestamp"):
        obj["creation_timestamp"] = str(obj["creation_timestamp"])
    if obj.get("timestamp"):
        obj["timestamp"] = str(obj["timestamp"])
    return obj


@app.route("/user_bots/<int:user_id>", methods=["GET"])
def user_bots(user_id):
    """Get bots by user_id. Only for admins."""
    result = list(map(format_for_response, crowdbot_bots_table.find({"superuser": user_id})))
    return make_response(({"result": result}, 200))


# todo pagination
@app.route("/crowdbots", methods=["GET"])
def get_all_bots():
    """Get all bots"""
    # TODO Very bad - make pagination. So slow
    result = list(map(format_for_response, crowdbot_bots_table.find()))
    # pprint(result)
    return make_response(({"result": result}, 200))


@app.route("/crowdbot/<int:bot_id>", methods=["GET"])
def crowdbot_on_get(bot_id):
    """Get bot by bot_id"""
    chatbot = crowdbot_bots_table.find_one({"bot_id": bot_id})
    if chatbot:
        resp = ({"message": "Bot Exist", "result": format_for_response(chatbot)}, 200)
    else:
        resp = ({"message": "Bot Does Not Exist"}, 404)
    return make_response(resp)


@app.route('/crowdbot', methods=['POST'])
def crowdbot_on_post():
    """
    Save bot and admins data to database.

    Request json must looks like:

        {"params": {"bot": {"token": str,
                            "lang": str,
                            "superuser": int}}}
    """
    # todo check for not active tokens
    doc = request.get_json()["params"]
    telegram_check = requests.get(
        f"https://api.telegram.org/bot{doc['bot']['token']}/getMe").json()
    if telegram_check["ok"]:
        chatbot = doc["bot"]
        chatbot["bot_id"] = telegram_check["result"]["id"]
        chatbot["username"] = telegram_check["result"]["username"]
        chatbot["name"] = telegram_check["result"]["first_name"]
        chatbot["welcomeMessage"] = None
        chatbot["active"] = True
        chatbot["shop_enabled"] = False
        # chatbot["donations_enabled"] = False
        chatbot["creation_timestamp"] = datetime.now()
        # todo "update_one" with "upsert"? mb check for the bot_id in db and delete if it exist
        crowdbot_bots_table.update_one({"bot_id": chatbot["bot_id"]},
                                       {"$set": chatbot}, upsert=True)

        # doc["admins"].append(dict(user_id=chatbot["superuser"]))
        # for admin in doc["admins"]:
        #     admin["bot_id"] = chatbot["bot_id"]
        #     admin["registered"] = False
        #     admin["is_admin"] = True
        #     admin["superuser"] = admin.get("user_id") == chatbot["superuser"]
        #     if "user_id" in admin:
        #         users_table.update({"user_id": admin["user_id"],
        #                             "bot_id": chatbot["bot_id"]},
        #                            admin, upsert=True)
        #     else:
        #         users_table.save(admin)

        telegram_check["result"] = format_for_response(chatbot)
        return make_response((telegram_check, 201))
    else:
        return make_response((telegram_check, telegram_check["error_code"]))


@app.route('/crowdbot', methods=['DELETE'])
def on_delete():
    doc = request.args
    chatbot_id = int(doc["bot_id"])
    # todo don't delete data to control processes - and maybe remove from prod. db
    crowdbot_db["crowdbot_chatbots"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["custom_buttons"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["admin_passwords"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["users"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["user_mode"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["users_messages_to_admin_bot"].delete_many({"bot_id": chatbot_id})

    crowdbot_db["products"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["carts"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["categories"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["shop_categories"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["customers_contacts"].delete_many({"bot_id": chatbot_id})
    crowdbot_db["orders"].delete_many({"bot_id": chatbot_id})

    resp = Response({"ok": True}, status=200, mimetype='application/json')
    return resp


@app.route("/check_token/<string:token>", methods=["GET"])
def check_token(token):
    """Check token before bot creation"""
    telegram_resp = requests.get(url=f"https://api.telegram.org/bot{token}/getMe").json()
    if not telegram_resp.get("ok"):
        resp = ({"message": "Token Error", "result": telegram_resp}, telegram_resp["error_code"])
    else:
        chatbot = crowdbot_bots_table.find_one({"bot_id": telegram_resp["result"]["id"],
                                                "active": True})
        if chatbot:
            resp = ({"message": "Bot Exist", "result": format_for_response(chatbot)}, 403)
        else:
            resp = ({"message": "Token Valid", "result": telegram_resp}, 200)
    return make_response(resp)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
