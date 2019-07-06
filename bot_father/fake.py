from bot_father.db import users_messages_to_admin_table
from datetime import datetime


def gen_fake(count=100):
    for i in range(count):
        users_messages_to_admin_table.insert_one(
            {
                "user_full_name": 'Loc Loc',
                "username": '@keikoobro',
                "chat_id": 321858998,
                "user_id": 321858998,
                "timestamp": datetime.now(),
                "category": 'Complaint',
                "messages": [
                    {'file_id': 'AgADAgADWqsxG6tJoUiRssQLalwiBFvUtw8ABHYF4V0hpXNM9FUAAgI', 'type': 'photo'},
                    {'file_id': 'text', 'type': 'text'}],
                'user_msg_string': 'contains - 1 photo file. 1 text file. ',
                'answer': None,
                'answer_msg_string': 'Not yet...',
                'deleted': False,
                'have_file': True
            })
