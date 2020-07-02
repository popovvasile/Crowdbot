"""June 27 2020"""
from pprint import pprint
from uuid import uuid4

from pymongo import MongoClient


def migrate():
    client = MongoClient('localhost', 27017)
    db = client['crowdbot_chatbots']
    products_table = db["products"]
    orders_table = db["orders"]

    # Add "article" field to each document in products_table.
    for prod in products_table.find():
        products_table.update_one({"_id": prod["_id"]},
                                  {"$set": {"article": str(uuid4())[:6].upper()}})

    # Add "article" field to all documents in orders_table.
    for order in orders_table.find():
        orders_table.update_one({"_id": order["_id"]},
                                {"$set": {"article": str(uuid4())[:6].upper()}})

    print("Migration Done!")


if __name__ == "__main__":
    migrate()
