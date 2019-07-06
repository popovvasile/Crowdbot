from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['bot_father']

users_messages_to_admin_table = db["users_messages_to_admin"]
support_admins_table = db['support_admins']
bot_father_bots_table = db['bot_father_bots']
bot_father_users_table = db['bot_father_users']
