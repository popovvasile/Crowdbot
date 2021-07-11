# -*- coding: utf-8 -*-
from __future__ import annotations
from pymongo import MongoClient


def upgrade():

    # Prod DB conf.
    client = MongoClient('localhost', 27017)
    database = client['crowdbot_chatbots']
    bots_table = database['crowdbot_chatbots']

    # Update lang field with the correct iso_639_1 language code.
    bots_table.update_many({"lang": "ENG"}, {"$set": {"lang": "en"}})
    bots_table.update_many({"lang": "RUS"}, {"$set": {"lang": "ru"}})
    bots_table.update_many({"lang": "DE"}, {"$set": {"lang": "de"}})

    print("Migration Done! Successfully upgraded.")


def downgrade():
    # Prod DB conf.
    client = MongoClient('localhost', 27017)
    database = client['crowdbot_chatbots']
    bots_table = database['crowdbot_chatbots']

    # Downgrade lang field with the old language code.
    bots_table.update_many({"lang": "en"}, {"$set": {"lang": "ENG"}})
    bots_table.update_many({"lang": "ru"}, {"$set": {"lang": "RUS"}})
    bots_table.update_many({"lang": "de"}, {"$set": {"lang": "DE"}})

    print("Migration Done! Successfully downgraded.")


if __name__ == "__main__":
    upgrade()
