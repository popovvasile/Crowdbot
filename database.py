from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['crowdbot_chatbots']
donations_table = db['donations_table']
poll_instances_table = db['setpoll_instances']
polls_table = db['setpolls']
surveys_table = db["surveys"]
users_table = db["users"]
custom_buttons_table = db["custom_buttons"]
payments_requests_table = db['payments_requests_table']
chats_table = db["chats"]
chatbots_table = db["crowdbot_chatbots"]
answers_table = db['answers']
products_table = db["products"]
orders_table = db["orders"]
scam_reports_table = db["scam_reports"]
users_messages_to_admin_table = db["users_messages_to_admin"]
user_mode_table = db["user_mode"]
channels_table = db["channels"]
categories_table = db["categories"]
user_categories_table = db["user_categories"]
DROPBOX_TOKEN = "xPAGp5mkaqgAAAAAAAABwK7yiygvq9ITgQj7j4KlBU8SYQ3WEmHCQnUxCIZUD-mR"
