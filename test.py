import requests
import json

requests.post('127.0.0.1:8000/chatbot',
              data={'admins[]': ['{"email":"po@gmail.co"', '"password":"NThLDLf1Xqz"}'],
                    'finished': 'true',
                    'buttons[]':
                        ['Discography', 'Concerts', 'Battles', 'New Projects', 'Live photos'],

                    '_id': '"5cd835f0522bc511ad555ffe"',
                    'superuser': '244356086',
                    'name': 'Crowdbot',
                    'welcomeMessage': 'hi',
                    "language": "Russian",
                    "crowdbot_token": '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg',
                    "shop_token": "token",
                    "credit_card_token": "token",
                    "currency": "EUR"
                    })
requests.delete('127.0.0.1:8000/chatbot',
                data={'token': '633257891:AAF26-vHNNVtMV8fnaZ6dkM2SxaFjl1pLbg'})


requests.post('127.0.0.1:8000/chatbot/admin', data={"token": "token",
                                                    "email": "popovvasile@gmail.com",
                                                    "password": "password"})
requests.delete('127.0.0.1:8000/chatbot/admin', data={"token": "token",
                                                      "email": "popovvasile@gmail.com"})
