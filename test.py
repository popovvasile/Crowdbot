import requests
import json

#
print(requests.post('http://localhost:8000/crowdbot',
                    data=json.dumps({u'params': {u'superuser': 244356086, u'name': u'DemoBot', u'finished': True,
                                                 u'welcomeMessage': u'vfdbgf', u'buttons': [u'Idea ', u'Business plan ',
                                                                                            u'Outlay  ', u'Team  '],
                                                 u'admins': [{u'password': u'0yb3I5vhy0r', u'email': u'po@hmail.com'}],
                                                 u'token': u'633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg',
                                                 u'requireNext': None, u'_id': u'5cf1fcfe11ff5d12f5018e43'}})))
# requests.delete('127.0.0.1:8000/chatbot',
#                 data={'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg'})
#
#
# requests.post('127.0.0.1:8000/chatbot/admin', data={"token": "token",
#                                                     "email": "popovvasile@gmail.com",
#                                                     "password": "password"})
# requests.delete('127.0.0.1:8000/chatbot/admin', data={"token": "token",
#                                                       "email": "popovvasile@gmail.com"})
