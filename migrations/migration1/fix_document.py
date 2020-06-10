"""June 11 2020"""
import json
from pprint import pprint

from pymongo import MongoClient
from bson.json_util import dumps, loads


def broken_document_fix():
    client = MongoClient('localhost', 27017)
    db = client['crowdbot_chatbots']
    chatbots_table = db["crowdbot_chatbots"]

    broken_document_filter = {"bot_id": 1191051963}

    # Write broken document to json file
    with open("migrations/migration1/broken_document_before.json", "w") as json_file:
        broken_document = chatbots_table.find_one(broken_document_filter)
        pprint(broken_document)
        json.dump(json.loads(dumps(broken_document)), json_file)

    # Remove "button" field from broken bot document
    chatbots_table.update_one(broken_document_filter, {"$unset": {"shop.button": ""}})

    # Write correct document to json file
    with open("migrations/migration1/broken_document_after.json", "w") as json_file:
        correct_document = chatbots_table.find_one(broken_document_filter)
        pprint(correct_document)
        json.dump(json.loads(dumps(correct_document)), json_file)

    print("Broken document fix Done!")


if __name__ == "__main__":
    broken_document_fix()
