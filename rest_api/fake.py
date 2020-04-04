from datetime import datetime, timedelta
from random import randint

from faker import Faker
from bson import ObjectId

from database import users_table, users_messages_to_admin_table


class FakeUsers:
    # def __init__(self):
    bot_id = 771382519  # @test_user_crowd_bot
    fake = Faker()
    user_ids = [305465575, 378826409, 573858793,
                244356086, 620501777, 479438338]

    def registered_admins(self):
        for i in range(20):
            profile = self.fake.simple_profile(sex=None)
            users_table.insert_one({
                "bot_id": self.bot_id,
                "chat_id": 321858998,
                "user_id": 321858998,
                "username": profile["username"],
                "full_name": profile["name"],
                # "mention_markdown": f"[{profile['name']}](tg://user?id=321858998)",
                # "mention_html": f'<a href="tg://user?id=321858998">{profile["name"]}</a>',
                "timestamp": datetime.now(),
                "registered": True,
                "is_admin": True,
                "superuser": False,
                "regular_messages_blocked": False,
                "anonim_messages_blocked": False,
                "tags": ["#all", "#user", "#admin"],
                "fake": True})

    def not_registered_admins(self):
        for i in range(20):
            users_table.insert_one({"bot_id": self.bot_id,
                                    "is_admin": True,
                                    "password": "2b8c3ff7-4",
                                    "registered": False,
                                    "superuser": False,
                                    "fake": True})

    def users(self, count=20):
        for user_id in self.user_ids:
            profile = self.fake.simple_profile(sex=None)
            users_table.insert_one(
                {"bot_id": self.bot_id,
                 "chat_id": user_id,
                 "user_id": user_id,
                 "username": profile["username"],
                 "full_name": profile["name"],
                 # "mention_markdown": f"[{profile['name']}](tg://user?id={user_id})",
                 # "mention_html": f'<a href="tg://user?id={user_id}">{profile["name"]}</a>',
                 "timestamp": datetime.now(),
                 'registered': False,
                 "is_admin": False,
                 "superuser": False,
                 "regular_messages_blocked": False,
                 "anonim_messages_blocked": False,
                 "blocked": False,
                 "tags": ["#all", "#user"],
                 "fake": True})


class FakeMessages:
    bot_id = 771382519
    fake = Faker()

    def fake_vasi_messages(self, count=20):

        messsage = {
            'anonim': False,
            'answer_content': [
                # {'name': '🤢',
                #  'sticker_file':
                #      'CAACAgIAAxkBAAKx-V5dekGET3yk4MRzEsGfvbQJTZedAAKwAAO_ZtAXiyPzJWW1vkEYBA'},
                # {'name': '😅',
                #  'sticker_file':
                #      'CAACAgIAAxkBAAKx-15dekufHcCYTi7B_F4kGDViV1esAALIAQAC-eRsAAGSghyFw1_y4RgE'}
            ],
            'bot_id': self.bot_id,
            'chat_id': 244356086,
            'content': [{'text': self.fake.text()}],
            'deleted': False,
            'is_new': True,
            'timestamp': datetime.now() - timedelta(seconds=randint(1, 50000)),
            'user_full_name': 'Vasi',
            'user_id': 244356086}
        for x in range(count):
            users_messages_to_admin_table.insert_one(messsage)
        # users_messages_to_admin_table.insert_many([messsage for x in range(count)])

    def messages(self, count=20):
        count = 0
        for user in users_table.find():
            users_messages_to_admin_table.insert_one({
                'anonim': False,
                'bot_id': self.bot_id,
                'chat_id': user["user_id"],
                "user_id": user["user_id"],
                'content': [{'text': 'this is my regular message'}],
                'is_new': True,
                # 'message_id': 12666,
                'timestamp': datetime.now(),
                'user_full_name': 'User Userevich',
            })
            if count == 3:
                break
            count += 1

    """def messages(self, count=20):
        count = 0
        for user_id in FakeUsers.user_ids:
            users_messages_to_admin_table.insert_one({
                'anonim': False,
                'bot_id': self.bot_id,
                'chat_id': user_id,
                "user_id": user_id,
                'content': [{'text': 'this is my regular message'}],
                'is_new': True,
                # 'mention_html': '<a href="tg://user?id={user_id}">Loc Loc</a>',
                # 'mention_markdown': '[Loc Loc](tg://user?id=321858998)',
                'message_id': 12666,
                'timestamp': datetime.now(),
                'user_full_name': 'User Userevich',
            })
            if count == 3:
                break
            count += 1"""


if __name__ == "__main__":
    # FakeUsers().users()
    # FakeMessages().messages()
    FakeMessages().fake_vasi_messages()
