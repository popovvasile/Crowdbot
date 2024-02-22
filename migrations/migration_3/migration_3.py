"""11 February 2021"""
from pymongo import MongoClient


def migrate():
    client = MongoClient('localhost', 27017)
    db = client['crowdbot_chatbots']
    chatbots_table = db["crowdbot_chatbots"]

    for bot in chatbots_table.find():
        shop = bot.get("shop")
        if shop:
            if shop.get("shipping"):
                shop["delivery"] = True
                shop["pick_up"] = False
                shop["delivery_fee"] = 0
            else:
                shop["delivery"] = False
                shop["pick_up"] = True
                shop["delivery_fee"] = 0
            shop.pop("shipping", None)
        bot["shop"] = shop
        if bot["lang"] == "RUS":
            bot["lang"] = "ru"
        elif bot["lang"] == "ENG":
            bot["lang"] = "en"
        else:
            bot["lang"] = "de"
        chatbots_table.replace_one(filter={"bot_id": bot["bot_id"]},
                                   replacement=bot)
    print("Migration Done!")


if __name__ == "__main__":
    migrate()