from random import randint

from database import (products_table, orders_table,
                      categories_table, brands_table)
from modules.shop.helper.data import categories, brands


class FakeDb(object):
    def make_db(self):
        categories_table.delete_many({})
        self.insert_all_categories()

        brands_table.delete_many({})
        self.insert_all_brands()

    @staticmethod
    def insert_all_categories():
        for category in categories:
            categories_table.insert_one({"name": category["name"]})
        print("Categories added")

    @staticmethod
    def insert_all_brands():
        for brand in brands:
            logo_file_id = \
                'AgADAgADGa0xG2qBmEtQQJsjU6Npx69XzQ8ABAEAAwIAA3kAA5UZAAIWBA'
            prices = [899, 990, 1090, 1190, 1290]
            brands_table.insert_one({"name": brand["name"],
                                     "price": prices[randint(0, len(prices)-1)],
                                     "logo_file_id": logo_file_id})
        print("Brands added")


class Faker(object):
    @staticmethod
    def fake_order(count=1):
        products = products_table.find()
        for i in range(count):
            orders_table.insert_one()


if __name__ == "__main__":
    FakeDb().make_db()
