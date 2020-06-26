"""June 11 2020"""
import json
from pprint import pprint

from pymongo import MongoClient


def convert_id(doc):
    pprint(doc)
    doc["_id"] = str(doc["_id"])
    return doc


def migrate():
    client = MongoClient('localhost', 27017)
    db = client['crowdbot_chatbots']
    chatbots_table = db["crowdbot_chatbots"]
    users_table = db["users"]

    # Remove "donations_enabled" field from all bots in chatbots_table.
    chatbots_table.update_many({}, {"$unset": {"donations_enabled": ""}})

    # Remove "registered" and "tags" fields from all documents in users_table.
    users_table.update_many({}, {"$unset": {"registered": "", "tags": ""}})

    # Remove all superusers documents created by old API registration.
    # Old API was added admins to users_table but now register_chat function done all work.
    # Old superusers documents that we need to delete looks like this:
    """
    {'_id': ObjectId('5edf6a7f42c26315996c1d88'),
     'bot_id': 1084083334,
     'is_admin': True,
     'registered': False,
     'superuser': True,
     'user_id': 321858998}
     """
    broken_users_filter = {
        "username": {"$exists": False},
        "full_name": {"$exists": False},
        "timestamp": {"$exists": False},
        "regular_messages_blocked": {"$exists": False},
        "anonim_messages_blocked": {"$exists": False},
        "order_notification": {"$exists": False},
        "messages_notification": {"$exists": False},
        "blocked": {"$exists": False},
        "unsubscribed": {"$exists": False}
    }

    all_broken_super_users = users_table.find(broken_users_filter)
    print(all_broken_super_users.count())

    # Write all removed superusers to the json file.
    with open("migrations/migration1/migration1_result.json", "w") as migration_json:
        json.dump(list(map(convert_id, all_broken_super_users)), migration_json)

    # Remove all broken superusers
    users_table.delete_many(broken_users_filter)

    print("Migration Done!")


if __name__ == "__main__":
    migrate()
