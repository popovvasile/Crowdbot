from database import users_table, client
from datetime import datetime
from faker import Faker


class FakeUsers(object):
    def __init__(self):
        self.bot_id = 771382519
        self.fake = Faker()

    def registered_admins(self):
        for i in range(20):
            profile = self.fake.simple_profile(sex=None)
            users_table.insert_one({
                "bot_id": self.bot_id,
                "chat_id": 321858998,
                "user_id": 321858998,
                "email": profile["mail"],
                "username": profile["username"],
                "full_name": profile["name"],
                "mention_markdown": f"[{profile['name']}](tg://user?id=321858998)",
                "mention_html": f'<a href="tg://user?id=321858998">{profile["name"]}</a>',
                "timestamp": datetime.now(),
                "registered": True,
                "is_admin": True,
                "superuser": False,
                "tags": ["#all", "#user", "#admin"],
                "fake": True})

    def not_registered_admins(self):
        for i in range(20):
            users_table.insert_one({"bot_id": self.bot_id,
                                    "email": self.fake.email(),
                                    "is_admin": True,
                                    "password": "2b8c3ff7-4",
                                    "registered": False,
                                    "superuser": False,
                                    "fake": True})

    def users(self):
        for i in range(20):
            profile = self.fake.simple_profile(sex=None)
            users_table.insert_one(
                {"bot_id": self.bot_id,
                 "chat_id": 321858998,
                 "user_id": 321858998,
                 "username": profile["username"],
                 "full_name": profile["name"],
                 "mention_markdown": f"[{profile['name']}](tg://user?id=321858998)",
                 "mention_html": f'<a href="tg://user?id=321858998">{profile["name"]}</a>',
                 "timestamp": datetime.now(),
                 'registered': False,
                 "is_admin": False,
                 "tags": ["#all", "#user"],
                 "fake": True})

    def users_and_admins(self):
        self.registered_admins()
        self.not_registered_admins()
        self.users()


if __name__ == "__main__":
    FakeUsers().users_and_admins()
    # client.drop_database("crowdbot_chatbots")
