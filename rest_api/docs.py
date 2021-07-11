from flask_restful.fields import List, Raw, Integer, String, Boolean


_bot_response = {
    "_id": String,
    "active": Boolean,
    "bot_id": Integer,
    "creation_timestamp": String,  # DateTime field?
    "lang": String,
    "name": String,
    "shop": {
        "address": String,
        "currency": String,
        "description": String,
        "payment_token": String,
        "shipping": Boolean,
        "shop_type": String
    },
    "shop_enabled": Boolean,
    "superuser": Integer,
    "token": String,
    "total_active_users": Integer,
    "total_not_active_users": Integer,
    "username": String,
    "welcomeMessage": String,
    "admins": List(Raw({
        "_id": String,
        "anonim_messages_blocked": Boolean,
        "blocked": Boolean,
        "bot_id": Integer,
        "chat_id": Integer,
        "full_name": String,
        "is_admin": Boolean,
        "messages_notification": Boolean,
        "order_notification": Boolean,
        "regular_messages_blocked": Boolean,
        "superuser": Boolean,
        "timestamp": String,  # DateTime field?
        "unsubscribed": Boolean,
        "user_id": Integer,
        "username": String
    }))
}

response_doc = {
    "ok": Boolean,
    "message": String,
    "result": Raw(_bot_response)
}

result_response = {"items": List(Raw(_bot_response))}


def resp_doc(ok: bool, message: str, result: dict = None) -> dict:
    doc = {
        "ok": ok,
        "message": message,
        "result": {}
    }
    if result:
        doc["result"] = result
    return doc


_pagination_fields = {'current_page': Integer,
                      'total_pages': Integer,
                      'total_items': Integer,
                      'per_page': Integer}


paginated_response = {
    "items": List(Raw(_bot_response)),
    **_pagination_fields
}
