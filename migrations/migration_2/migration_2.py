"""June 27 2020"""
from pprint import pprint

from pymongo import MongoClient


def migrate():
    client = MongoClient('localhost', 27017)
    db = client['crowdbot_chatbots']
    products_table = db["products"]
    orders_table = db["orders"]

    # Add "article" field to all documents in products_table.
    products_table.update_many({}, {"$set": {"article": str(uuid4())[:6].upper()}})

    # Add "article" field to all documents in orders_table.
    orders_table.update_many({}, {"$set": {"article": str(uuid4())[:6].upper()}})

    print("Migration Done!")


if __name__ == "__main__":
    migrate()
