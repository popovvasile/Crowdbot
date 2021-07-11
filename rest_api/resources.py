from math import ceil

from datetime import datetime

import requests
from flask_restful import Resource, marshal_with

from rest_api.common import format_for_response, revoke_token
from rest_api.docs import response_doc, resp_doc, result_response, paginated_response
from rest_api.errors import BotNotFound, InvalidToken
from rest_api.parsers import access_parser, paginated_parser
from database import (chatbots_table, orders_table, shop_customers_contacts_table,
                      shop_categories_table, categories_table, carts_table, products_table,
                      users_messages_to_admin_table, user_mode_table, users_table,
                      admin_passwords_table, custom_buttons_table, conflict_notifications_table)


class CrowdRobot(Resource):

    @marshal_with(response_doc)
    def get(self):  # todo bug with admins - superuser is not there somehow
        """Get bot by bot_id"""
        parser = access_parser.copy()
        parser.add_argument("bot_id", type=int, location="json", required=True)
        args = parser.parse_args(strict=True)
        chat_bot = chatbots_table.find_one({"bot_id": args["bot_id"]})
        chatbot = format_for_response(chat_bot)
        # chatbot["admins"] = [{
        #     "bot_id": chat_bot["bot_id"],
        #     "user_id": chat_bot["superuser"],
        #     "full_name": "Vasi",
        #     "username": "vasile_python"
        # }]

        if chatbot:
            return resp_doc(ok=True,
                            message="Bot Exist",
                            result=chatbot), 200
        else:
            raise BotNotFound

    @marshal_with(response_doc)
    def post(self):
        """Create and save bot"""
        parser = access_parser.copy()
        parser.add_argument("token", type=str, location="json", required=True)
        parser.add_argument("lang", type=str, location="json", required=True)
        parser.add_argument("superuser", type=int, location="json", required=True)
        parser.add_argument("premium", type=bool, location="json", required=True)
        args = parser.parse_args(strict=True)

        telegram_check = requests.get(f"https://api.telegram.org/bot{args['token']}/getMe").json()
        if not telegram_check["ok"]:
            raise InvalidToken

        # Find bot in database
        chatbot = chatbots_table.find_one({"bot_id": telegram_check["result"]["id"]})

        if chatbot:
            # Bot exist and active - need another token to create new bot.
            if chatbot["active"]:
                return resp_doc(ok=False,
                                message="Bot exist and active",
                                result=format_for_response(chatbot)), 400
            else:
                # Bot exist but not active - revoke token and superuser.
                chatbot = revoke_token(telegram_check["result"]["id"], args)
                if chatbot:
                    return resp_doc(ok=True,
                                    message="Token revoked successfully",
                                    result=format_for_response(chatbot)), 200
                else:
                    raise BotNotFound

        # Token valid and bot doesn't exist in db - create and save new bot to database.
        else:
            fields = {
                "token": args["token"],
                "lang": args["lang"],
                "premium": args["premium"],
                "superuser": args["superuser"],
                "bot_id": telegram_check["result"]["id"],
                "username": telegram_check["result"]["username"],
                "name": telegram_check["result"]["first_name"],
                "welcomeMessage": None,
                "active": True,
                "shop_enabled": False,
                "creation_timestamp": datetime.now()
            }
            chatbot = chatbots_table.find_and_modify(
                {"bot_id": telegram_check["result"]["id"]},
                {"$set": fields}, upsert=True, new=True
            )
            return resp_doc(ok=True,
                            message="Bot created successfully",
                            result=format_for_response(chatbot)), 201

    # @marshal_with(response_doc)
    # def put(self):
    #     """Update the bot"""
    #     parser = access_parser.copy()
    #     parser.add_argument("bot_id", type=int, location="json", required=True)
    #     args = parser.parse_args()
    #     # Find bot in database
    #     chat_bot = chatbots_table.find_one({"bot_id": args["bot_id"]})
    #     args.pop("API_KEY", None)
    #     chat_bot.update(args)
    #     chatbots_table.replace_one(dict(bot_id=args["bot_id"]), chat_bot)
    #     if chat_bot["active"]:
    #         return resp_doc(ok=False,
    #                         message="Bot exist and active",
    #                         result=format_for_response(chat_bot)), 201

    # @marshal_with(response_doc)
    # def patch(self):
    #     parser = access_parser.copy()
    #     parser.add_argument('bot_id', type=int, location='json', required=True)
    #     parser.add_argument('premium', type=bool, location='json')
    #     parser.add_argument('shop_enabled', type=bool, location='json')
    #     args = parser.parse_args()
    #
    #     new_fields = {}
    #     if 'premium' in args:
    #         new_fields['premium'] = args['premium']
    #     if 'shop_enabled' in args:
    #         new_fields['shop_enabled'] = args['shop_enabled']
    #
    #     chatbot = chatbots_table.find_and_modify({'bot_id': args['bot_id']},
    #                                              {'$set': new_fields}, new=True)
    #     if not chatbot:
    #         raise BotNotFound
    #     return resp_doc(ok=True,
    #                     message="Chatbot updated successfully",
    #                     result=format_for_response(chatbot)), 200

    @marshal_with(response_doc)
    def delete(self):
        """ Delete bot."""
        parser = access_parser.copy()
        parser.add_argument("bot_id", type=int, location="json", required=True)
        args = parser.parse_args(strict=True)
        # Remove Bot.
        chatbots_table.delete_many({"bot_id": args["bot_id"]})
        custom_buttons_table.delete_many({"bot_id": args["bot_id"]})
        admin_passwords_table.delete_many({"bot_id": args["bot_id"]})
        users_table.delete_many({"bot_id": args["bot_id"]})
        user_mode_table.delete_many({"bot_id": args["bot_id"]})
        users_messages_to_admin_table.delete_many({"bot_id": args["bot_id"]})
        conflict_notifications_table.delete_many({"bot_id": args["bot_id"]})
        # Remove Shop.
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
        return {"items": list(map(format_for_response, chat_bots))}, 200


class AllBots(Resource):

    @marshal_with(paginated_response)
    def get(self):
        """ Get all bots."""
        parser = paginated_parser.copy()
        args = parser.parse_args(strict=True)

        queryset = chatbots_table.find().sort("_id", -1)
        offset = (args['page'] - 1) * args['per_page']
        items = queryset.skip(offset).limit(args['per_page'])
        total_items = queryset.count()
        total_pages = ceil(total_items / args['per_page'])

        return {"items": list(map(format_for_response, items)),
                'current_page': args['page'],
                'total_pages': total_pages,
                'total_items': total_items,
                'per_page': args['per_page']}, 200


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


class Subscription(Resource):

    @marshal_with(response_doc)
    def patch(self):
        """ Turn shop off after subscription ends and turn on after subscription payed."""
        parser = access_parser.copy()
        parser.add_argument('bot_id', type=int, location='json', required=True)
        parser.add_argument('premium', type=bool, location='json', required=True)
        args = parser.parse_args()

        # Find bot in database.
        chatbot = chatbots_table.find_one({"bot_id": args['bot_id']})
        if not chatbot:
            raise BotNotFound

        new_fields = {}

        # Turn shop on.
        if args['premium']:
            new_fields['premium'] = True
            if chatbot.get('shop'):
                new_fields["shop_enabled"] = True
            else:
                new_fields["shop_enabled"] = False
        # Turn shop off.
        else:
            new_fields["premium"] = False
            new_fields["shop_enabled"] = False

        chatbot = chatbots_table.find_and_modify({'bot_id': args['bot_id']},
                                                 {'$set': new_fields}, new=True)
        if not chatbot:
            raise BotNotFound

        return resp_doc(ok=True,
                        message="Chatbot updated successfully",
                        result=format_for_response(chatbot)), 200
