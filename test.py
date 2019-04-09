import requests  # TODO
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
print(type(data.content))
print(json.loads(data.content))

b'{"ok":true,"result":{"message_id":5806,"from":{"id":633257891,"is_bot":true,"first_name":"Crowdbot","username":"DEMObyballbot"},"chat":{"id":244356086,"first_name":"Vasile","last_name":"P","username":"vasile_python","type":"private"},"date":1554676574,"invoice":{"title":"test","description":"test","start_parameter":"test","currency":"USD","total_amount":10000}}}'

b'{"ok":false,"error_code":400,"description":"Bad Request: PAYMENT_PROVIDER_INVALID"}'
