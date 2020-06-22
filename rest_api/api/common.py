from database import users_table


def format_for_response(chatbot: dict) -> dict:
    """Adds additional fields to chatbot dict."""
    # TODO use "from bson.json_util import dumps, loads"
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
