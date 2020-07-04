from datetime import datetime

import requests
from flask_restful import Resource, marshal_with

from rest_api.common import format_for_response, revoke_token
from rest_api.docs import response_doc, resp_doc, result_response
from rest_api.errors import BotNotFound, InvalidToken
from rest_api.parsers import access_parser
from database import (chatbots_table, orders_table, shop_customers_contacts_table,
                      shop_categories_table, categories_table, carts_table, products_table,
                      users_messages_to_admin_table, user_mode_table, users_table,
                      admin_passwords_table, custom_buttons_table, conflict_notifications_table)


class CrowdRobot(Resource):
    @marshal_with(response_doc)
    def get(self):
        """Get bot by bot_id"""
        parser = access_parser.copy()
        parser.add_argument("bot_id", type=int, location="json", required=True)
        args = parser.parse_args(strict=True)
        chat_bot = chatbots_table.find_one({"bot_id": args["bot_id"]})
        if chat_bot:
            return resp_doc(ok=True,
                            message="Bot Exist",
                            result=format_for_response(chat_bot)), 200
        else:
            raise BotNotFound

    @marshal_with(response_doc)
    def post(self):
        """Create and save bot"""
        parser = access_parser.copy()
        parser.add_argument("token", type=str, location="json", required=True)
        parser.add_argument("lang", type=str, location="json", required=True)
        parser.add_argument("superuser", type=int, location="json", required=True)
        args = parser.parse_args(strict=True)

        telegram_check = requests.get(f"https://api.telegram.org/bot{args['token']}/getMe").json()
        if not telegram_check["ok"]:
            raise InvalidToken

        # Find bot in database
        chat_bot = chatbots_table.find_one({"bot_id": telegram_check["result"]["id"]})

        if chat_bot:
            # Bot exist and active - need another token to create new bot
            if chat_bot["active"]:
                return resp_doc(ok=False,
                                message="Bot exist and active",
                                result=format_for_response(chat_bot)), 400
            else:
                # Bot exist but not active - revoke token and superuser
                chat_bot = revoke_token(telegram_check["result"]["id"], args)
                if chat_bot:
                    return resp_doc(ok=True,
                                    message="Token revoked successfully",
                                    result=format_for_response(chat_bot)), 200
                else:
                    raise BotNotFound
        # Token valid and bot doesn't exist in db - create and save new bot to database.
        else:
            chat_bot = {
                "token": args["token"],
                "lang": args["lang"],
                "superuser": args["superuser"],
                "bot_id": telegram_check["result"]["id"],
                "username": telegram_check["result"]["username"],
                "name": telegram_check["result"]["first_name"],
                "welcomeMessage": None,
                "active": True,
                "shop_enabled": False,
                "creation_timestamp": datetime.now()
            }
            chatbots_table.update_one({"bot_id": chat_bot["bot_id"]},
                                      {"$set": chat_bot}, upsert=True)
            return resp_doc(ok=True,
                            message="Bot created successfully",
                            result=format_for_response(chat_bot)), 201

    @marshal_with(response_doc)
    def delete(self):
        """Delete bot"""
        parser = access_parser.copy()
        parser.add_argument("bot_id", type=int, location="json", required=True)
        args = parser.parse_args(strict=True)
        # Remove Bot
        chatbots_table.delete_many({"bot_id": args["bot_id"]})
        custom_buttons_table.delete_many({"bot_id": args["bot_id"]})
        admin_passwords_table.delete_many({"bot_id": args["bot_id"]})
        users_table.delete_many({"bot_id": args["bot_id"]})
        user_mode_table.delete_many({"bot_id": args["bot_id"]})
        users_messages_to_admin_table.delete_many({"bot_id": args["bot_id"]})
        conflict_notifications_table.delete_many({"bot_id": args["bot_id"]})
        # Remove Shop
        products_table.delete_many({"bot_id": args["bot_id"]})
        carts_table.delete_many({"bot_id": args["bot_id"]})
        categories_table.delete_many({"bot_id": args["bot_id"]})
        shop_categories_table.delete_many({"bot_id": args["bot_id"]})
        shop_customers_contacts_table.delete_many({"bot_id": args["bot_id"]})
        orders_table.delete_many({"bot_id": args["bot_id"]})
        return resp_doc(ok=True, message="Bot deleted successfully"), 200


class UserBots(Resource):
    @marshal_with(result_response)
    def get(self):
        """Get bots by user_id."""
        parser = access_parser.copy()
        parser.add_argument("user_id", type=int, location="json", required=True)
        args = parser.parse_args(strict=True)
        chat_bots = chatbots_table.find({"superuser": args["user_id"]}).sort([["_id", -1]])
        return {"result": list(map(format_for_response, chat_bots))}, 200


class AllBots(Resource):
    # TODO
    #   1) need to make pagination on API side(not admin side)
    #   Works so slow and data not fresh after "pagination click" on admin side
    @marshal_with(result_response)
    def get(self):
        """Get all bots"""
        parser = access_parser.copy()
        args = parser.parse_args(strict=True)
        chat_bots = chatbots_table.find().sort([["_id", -1]])
        return {"result": list(map(format_for_response, chat_bots))}, 200


class RevokeToken(Resource):
    """Set new token for the bot"""
    @marshal_with(response_doc)
    def patch(self):
        parser = access_parser.copy()
        parser.add_argument("bot_id", type=int, location="json", required=True)
        parser.add_argument("token", type=str, location="json", required=True)
        parser.add_argument("superuser", type=int, location="json", required=True)
        args = parser.parse_args(strict=True)

        telegram_check = requests.get(f"https://api.telegram.org/bot{args['token']}/getMe").json()
        chat_bot = chatbots_table.find_one({"bot_id": args["bot_id"]})

        if not telegram_check["ok"]:
            raise InvalidToken

        if not chat_bot:
            raise BotNotFound

        if chat_bot["bot_id"] != telegram_check["result"]["id"]:
            return resp_doc(ok=False,
                            message="Given token is for another bot",
                            result={"username": telegram_check["result"]["username"],
                                    "name": telegram_check["result"]["first_name"]}), 403
        else:
            # Revoke token and superuser
            chat_bot = revoke_token(telegram_check["result"]["id"], args)
            if chat_bot:
                return resp_doc(ok=True,
                                message="Token revoked successfully",
                                result=format_for_response(chat_bot)), 200
            else:
                raise BotNotFound
