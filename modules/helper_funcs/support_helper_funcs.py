from datetime import datetime
from telegram import ParseMode
from telegram.error import TelegramError
from bot_father.db import support_admins_table, users_messages_to_admin_table
from bot_father.helper.strings import get_str, report_categories


def delete_messages(bot, update, user_data):
    try:
        bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
    except TelegramError:
        pass
    if 'to_delete' in user_data:
        for msg in user_data['to_delete']:
            try:
                if msg.message_id != update.effective_message.message_id:
                    bot.delete_message(update.effective_chat.id, msg.message_id)
            except TelegramError:
                # print('except in delete_message---> {}, {}'.format(e, msg.message_id))
                continue
        user_data['to_delete'] = list()
    else:
        user_data['to_delete'] = list()


# Create text to append in report template
def create_template_part(update, user_data, messages):
    # string = 'contains - '
    string = ""
    if messages is None:
        return get_str(user_data, update, "not_yet")
    if len(messages) == 1:
        if messages[0]['type'] == 'text':
            string = messages[0]['file_id']
        else:
            string += get_str(user_data, update, "report_file",
                              messages[0]['type'])
    else:
        messages_types = dict()
        for message in messages:
            if messages_types.get(message['type']):
                messages_types[message['type']] += 1
            else:
                messages_types[message['type']] = 1

        for msg_type, count in messages_types.items():
            if count == 1:
                string += get_str(user_data, update, "report_file_2",
                                  count, msg_type)
            else:
                string += get_str(user_data, update, "report_files",
                                  count, msg_type)
    return string


def admins_in_text(admins):
    return '\n'.join([i['email'] for i in admins])


def category_as_text(user_data, report):
    result = report_categories.get(user_data["lang"]).get(report["category"])
    return result if result else report['category']


def admin_report_template(update, user_data, report):
    return get_str(user_data, update, "admin_report_template",
                   report['username'],
                   category_as_text(user_data, report),
                   str(report['timestamp']).split('.')[0],
                   create_template_part(update, user_data, report["messages"]),
                   create_template_part(update, user_data, report['answer']))


def user_report_template(update, user_data, report):
    return get_str(user_data, update, "user_report_template",
                   category_as_text(user_data, report),
                   str(report['timestamp']).split('.')[0],
                   create_template_part(update, user_data, report["messages"]),
                   create_template_part(update, user_data, report["answer"]))


# class for sending notifications about completed actions
class Notification(object):
    # BOT FATHER
    @staticmethod
    def bot_created(bot, update, user_data):
        bot.send_message(update.effective_chat.id,
                         get_str(user_data, update, 'finish_creating',
                                 # bot_data['bot_name'],
                                 "[{}](https://t.me/{})".format(
                                     user_data['to_save']["bot_name"],
                                     user_data['to_save']["bot_username"][1:]),
                                 admins_in_text(user_data['to_save']['all_admins']),
                                 str(user_data['to_save']['timestamp']).split('.')[0]),
                         parse_mode=ParseMode.MARKDOWN)

    @staticmethod
    def bot_deleted(bot, update, user_data):
        bot.send_message(update.effective_chat.id,
                         get_str(user_data, update, 'finish_deleting',
                                 # bot_data['bot_name'],
                                 "[{}](https://t.me/{})".format(
                                     user_data['processed_bot']["bot_name"],
                                     user_data['processed_bot']["bot_username"][1:]),
                                 admins_in_text(user_data['processed_bot']['all_admins']),
                                 str(user_data['processed_bot']['timestamp']).split('.')[0],
                                 str(datetime.now()).split('.')[0]),
                         parse_mode=ParseMode.MARKDOWN)

    @staticmethod
    def admins_added(bot, update, user_data):
        bot.send_message(update.effective_chat.id,
                         get_str(user_data, update, 'finish_admin_add',
                                 # bot_name,
                                 "[{}](https://t.me/{})".format(
                                     user_data['processed_bot']["bot_name"],
                                     user_data['processed_bot']["bot_username"][1:]),
                                 admins_in_text(user_data['request']['admins']),
                                 str(datetime.now()).split('.')[0]),
                         parse_mode=ParseMode.MARKDOWN)

    @staticmethod
    def admin_deleted(bot, update, user_data, bot_data, admin):
        bot.send_message(update.effective_chat.id,
                         get_str(user_data, update, 'finish_admins_deleting',
                                 # bot_name,
                                 "[{}](https://t.me/{})".format(
                                     bot_data["bot_name"],
                                     bot_data["bot_username"][1:]),
                                 admin,
                                 str(datetime.now()).split('.')[0]),
                         parse_mode=ParseMode.MARKDOWN)

    # Support Bot
    # Mb add buttons near notification
    @staticmethod
    def new_report(bot, user_data, update, _id):
        report = users_messages_to_admin_table.find_one({'_id': _id})
        for admin in support_admins_table.find():
            bot.send_message(admin['chat_id'],
                             get_str(user_data, update, 'admin_notification') +
                             admin_report_template(update, user_data, report),
                             parse_mode=ParseMode.HTML)

    @staticmethod
    def report_answered(bot, user_data, update, _id):
        report = users_messages_to_admin_table.find_one({'_id': _id})
        bot.send_message(report['chat_id'],
                         get_str(user_data, update, 'user_notification') +
                         user_report_template(update, user_data, report),
                         parse_mode=ParseMode.HTML)
