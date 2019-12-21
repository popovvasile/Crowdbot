from database import (products_table, orders_table,
                      categories_table)
from modules.shop.helper.data import categories


class FakeDb(object):
    def make_db(self):
        categories_table.delete_many({})
        self.insert_all_categories()

    @staticmethod
    def insert_all_categories():
        for category in categories:
            categories_table.insert_one({"name": category["name"]})
        print("Categories added")


class Faker(object):
    @staticmethod
    def fake_order(count=1):
        products = products_table.find()
        for i in range(count):
            orders_table.insert_one()


if __name__ == "__main__":
    FakeDb().make_db()
