import requests
import json

from telegram import LabeledPrice
prices = [LabeledPrice("test", 10000)]
data = requests.get("https://api.telegram.org/bot633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg/sendInvoice",

        params=dict(title="test",
                    description="test",
                    payload="test",
                    provider_token="284685063:TEST:OWRiZGIxYWFhYzk4",
                    currency="USD",
                    start_parameter="test",
                    prices=json.dumps([p.to_dict() for p in prices]),
                    chat_id=244356086))  # send to the user in order to test it
print([p.to_dict() for p in prices])
print(data)
print(data.content)
b'{"ok":false,"error_code":400,"description":"Bad Request: PAYMENT_PROVIDER_INVALID"}'
