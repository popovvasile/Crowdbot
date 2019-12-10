from bson.objectid import ObjectId
from helper_funcs.misc import get_obj
from database import purchases_table


class Purchase(object):
    def __init__(self, obj: (ObjectId, dict, str)):
        # self.context = context
        product_obj = get_obj(purchases_table, obj)

        # self._id = product_obj["_id"]
        self.title = product_obj["title"]
        self.price = product_obj["price"]
        self.currency = product_obj["currency"]
        self.shipping = product_obj["shipping"]
