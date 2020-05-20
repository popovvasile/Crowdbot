from pymongo import MongoClient


def migrate():
    client = MongoClient('localhost', 27017)
    db = client['crowdbot_chatbots']
    chatbots_table = db["crowdbot_chatbots"]
    users_table = db["users"]

    chatbots_table.update_many({}, {"$unset": {"donations_enabled": ""}})
    users_table.update_many({}, {"$unset": {"registered": "", "tags": ""}})


if __name__ == "__main__":
    migrate()
