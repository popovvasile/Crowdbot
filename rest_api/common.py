from database import users_table, chatbots_table, conflict_notifications_table

from flask_restful.fields import Integer, String, Raw
from flask_restful import reqparse


# TODO use "from bson.json_util import dumps, loads"
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
                               "is_admin": True})

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


# pagination_fields = {"items_total": Integer,
#                      "total_pages": Integer,
#                      "current_page": Integer}
#
#
# def pagination_json():
#     return {"items_total": pagination.total,
#             "total_pages": pagination.pages,
#             "current_page": pagination.page}
#
#
# def paginate(query, args):
#     return query.paginate(args["page"],  # If None -> return 1
#                           per_page=args["per_page"],  # If None -> return 20
#                           max_per_page=100, error_out=False)


def revoke_token(bot_id, args):
    # remove all conflict notifications to send new if error occurred
    conflict_notifications_table.delete_many({"bot_id": bot_id})
    # Set new token and superuser for the bot
    return chatbots_table.find_and_modify({"bot_id": bot_id},
                                          {"$set": {"token": args["token"],
                                                    "superuser": args["superuser"],
                                                    "active": True}}, new=True)
