from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['crowdbot_chatbots']
groups_table = db["groups_table"]
donations_table = db['donations_table']
poll_instances_table = db['setpoll_instances']
polls_table = db['setpolls']
surveys_table = db["surveys"]
users_table = db["users"]
custom_buttons_table = db["custom_buttons"]
payments_requests_table = db['payments_requests_table']
chatbots_table = db["crowdbot_chatbots"]
admin_passwords_table = db["admin_passwords"]
answers_table = db['answers']
products_table = db["products"]
scam_reports_table = db["scam_reports"]
user_mode_table = db["user_mode"]
channels_table = db["channels"]
categories_table = db["categories"]
user_categories_table = db["user_categories"]
orders_quantity_table = db["orders_quantity"]
shop_categories_table = db["shop_categories"]
DROPBOX_TOKEN = "xPAGp5mkaqgAAAAAAAABwK7yiygvq9ITgQj7j4KlBU8SYQ3WEmHCQnUxCIZUD-mR"

# in bot_father.db

users_messages_to_admin_table = db["users_messages_to_admin_bot"]
# support_admins_table = db['support_admins']
# bot_father_bots_table = db['bot_father_bots']
# bot_father_users_table = db['bot_father_users']

# Api Shop To Mongo Shop
orders_table = db["orders"]
