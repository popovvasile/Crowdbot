# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
from math import ceil
from pprint import pprint
from bson import ObjectId

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler, Updater)
from telegram.error import TelegramError
import logging
from bot_father.db import users_messages_to_admin_table, support_admins_table, bot_father_users_table
from bot_father.strings import get_str, report_categories
# from bot_father.bot_father import delete_messages

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: number of unread messages near 'Inbox messages' button
#       notifications and enabled notification
#       warning that admin delete unanswered report
#       notification and disable notifications setting
#       answered by:
#       different text for different category
#       join text messages in formating report and answer
# TODO: AttributeError: 'NoneType' object has no attribute 'get_file' when video message
#       user_data['page'] - fix between states


def delete_messages(bot, update, user_data):
    # print(update.effective_message.message_id)
    # if update.callback_query:
    #     print(update.callback_query.data)
    # else:
    #     print(update.message.text)
    bot.delete_message(update.effective_chat.id, update.effective_message.message_id)
    if 'to_delete' in user_data:
        for msg in user_data['to_delete']:
            try:
                if msg.message_id != update.effective_message.message_id:
                    bot.delete_message(update.effective_chat.id, msg.message_id)
            except TelegramError as e:
                print('except in delete_message---> {}, {}'.format(e, msg.message_id))
                continue
        user_data['to_delete'] = list()
    else:
        user_data['to_delete'] = list()


def keyboard(lang, kb_name):
    keyboard_dict = dict(
        user_start_keyboard=InlineKeyboardMarkup(
            list(([InlineKeyboardButton(get_str(lang, 'send_report_button'), callback_data='send_report')],
                  [InlineKeyboardButton(get_str(lang, 'contacts_button'), callback_data='contacts')],
                  [InlineKeyboardButton(get_str(lang, 'my_reports_button'), callback_data='user_inbox_messages')],
                  [InlineKeyboardButton(get_str(lang, 'BACK'), callback_data='to_main_menu')]))),

        admin_start_keyboard=InlineKeyboardMarkup(
            list(([InlineKeyboardButton(get_str(lang, 'inbox_msg_button'), callback_data='admin_inbox_messages')],
                  [InlineKeyboardButton(get_str(lang, 'manage_admins_button'), callback_data='manage_admins')],
                  [InlineKeyboardButton(get_str(lang, 'black_list_button'), callback_data='black_list')],
                  [InlineKeyboardButton(get_str(lang, 'trash_button'), callback_data='trash')],
                  [InlineKeyboardButton(get_str(lang, 'BACK'), callback_data='to_main_menu')]))),

        categories_keyboard=InlineKeyboardMarkup([
                                                     [InlineKeyboardButton(x, callback_data=f'category/{x}')]
                                                     for x in report_categories.get(lang)] +
                                                 [[InlineKeyboardButton('Back', callback_data='cancel_report')]]),

        confirm_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_str(lang, 'send_btn'), callback_data='send')],
            [InlineKeyboardButton(get_str(lang, 'BACK'), callback_data='cancel_report')]]),

        final_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=get_str(lang, 'done_button'), callback_data="confirm_send")],
            [InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'), callback_data="cancel_report")]]),

        back_to_inbox_keyboard=InlineKeyboardMarkup(
            [[InlineKeyboardButton(get_str(lang, 'BACK'), callback_data='back_to_user_inbox')]]),

        cancel_report=InlineKeyboardMarkup(
            [[InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'), callback_data='cancel_report')]]),
        confirm_delete_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_str(lang, 'yes'), callback_data='remove'),
             InlineKeyboardButton(get_str(lang, 'BACK'), callback_data='return_to_admin_inbox')]]),

        admin_final_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=get_str(lang, 'done_button'), callback_data="confirm_answer_send")],
            [InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'), callback_data="return_to_admin_inbox")]]),

        admin_confirm_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_str(lang, 'send_btn'), callback_data='send_answer')],
            [InlineKeyboardButton(get_str(lang, 'BACK'), callback_data='return_to_admin_inbox')]])
    )
    return keyboard_dict[kb_name]


CHOOSE_CATEGORY, MESSAGE, CONFIRM_SEND_REPORT, \
    USER_INBOX, SINGLE_REPORT, \
    ADMIN_INBOX, ANSWERING, CONFIRM_SEND_ANSWER, ADMIN_SINGLE_REPORT, \
    CONFIRM_DELETE, TRASH = range(11)

conf = {'PER_PAGE': 5}


def send_reports_layout(bot, update, user_data, page, to_admin=False, show_trash=False):
    lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

    back_button = [InlineKeyboardButton('Back', callback_data='back')]
    if to_admin:
        all_data = users_messages_to_admin_table.find({'deleted': show_trash}).sort([['_id', -1]])
    else:
        all_data = users_messages_to_admin_table.find({'user_id': update.effective_user.id}).sort([['_id', -1]])

    if all_data.count() == 0:
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'no_reports')))

    if page == 1:
        data_to_send = all_data.limit(conf['PER_PAGE'])
    else:
        last_on_prev_page = (page - 1) * conf['PER_PAGE']
        data_to_send = [i for i in all_data[last_on_prev_page: last_on_prev_page + conf['PER_PAGE']]]

    # Pagination keyboard logic
    # to do better!
    total_pages = ceil(all_data.count() / conf['PER_PAGE'])
    pages_keyboard = [[], back_button]
    if total_pages <= 1:
        pages_keyboard = [back_button]
    elif 2 <= total_pages <= 8:
        for i in range(1, total_pages + 1):
            pages_keyboard[0].append(InlineKeyboardButton('|' + str(i) + '|', callback_data=i)
                                     if i == page else
                                     InlineKeyboardButton(str(i), callback_data=i))
    else:
        arr = [i if i in range(page - 1, page + 3) else
               i if i == total_pages else
               i if i == 1 else
               # str_to_remove
               '' for i in range(1, total_pages + 1)]
        layout = list(dict.fromkeys(arr[:arr.index(page)])) + list(dict.fromkeys(arr[arr.index(page):]))
        for num, i in enumerate(layout):
            if i == '':
                pages_keyboard[0].append(InlineKeyboardButton('...',
                                                              callback_data=layout[num - 1] + 1
                                                              if num > layout.index(page) else
                                                              layout[num + 1] - 1))
            else:
                pages_keyboard[0].append(InlineKeyboardButton('|' + str(i) + '|', callback_data=i)
                                         if i == page else
                                         InlineKeyboardButton(str(i), callback_data=i))

    user_data['to_delete'].append(
        bot.send_message(update.callback_query.message.chat_id,
                         get_str(lang, 'trash_menu' if show_trash
                         else 'admin_all_reports_menu' if to_admin
                         else 'my_reports_menu'), ParseMode.MARKDOWN))

    for report in data_to_send:
        if to_admin:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'admin_report_template',
                                         report['username'],
                                         report['category'],
                                         str(report['timestamp']).split('.')[0],
                                         report['user_msg_string'],
                                         report['answer_msg_string']),
                                 reply_markup=make_report_keyboard(report, to_admin, show_trash)))
        else:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'user_report_template',
                                         report['category'],
                                         str(report['timestamp']).split('.')[0],
                                         report['user_msg_string'],
                                         report['answer_msg_string']),
                                 reply_markup=make_report_keyboard(report)))

    user_data['to_delete'].append(
        bot.send_message(update.effective_chat.id,
                         get_str(lang, 'current_page', page),
                         reply_markup=InlineKeyboardMarkup(pages_keyboard)))


def open_report(bot, update, user_data, report):
    lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
    if len(report['messages']) == 1 and report['messages'][0]['type'] == 'text':
        pass
    else:
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'message')))
        send_messages_from_report(bot, update, user_data, report['messages'])

    if report['answer']:
        if len(report['answer']) == 1 and report['answer'][0]['type'] == 'text':
            pass
        else:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'answer')))
            send_messages_from_report(bot, update, user_data, report['answer'])


def send_messages_from_report(bot, update, user_data, reports):
    for msg in reports:
        if msg['type'] == 'text':
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, msg['file_id']))

        elif msg['type'] == 'photo':
            user_data['to_delete'].append(
                bot.send_photo(update.effective_chat.id, photo=msg['file_id']))

        elif msg['type'] == 'audio':
            user_data['to_delete'].append(
                bot.send_audio(update.effective_chat.id, msg['file_id']))

        elif msg['type'] == 'voice':
            user_data['to_delete'].append(
                bot.send_voice(update.effective_chat.id, msg['file_id']))

        elif msg['type'] == 'document':
            user_data['to_delete'].append(
                bot.send_document(update.effective_chat.id, msg['file_id']))

        elif msg['type'] == 'sticker':
            user_data['to_delete'].append(
                bot.send_sticker(update.effective_chat.id, msg['file_id']))

        elif msg['type'] == 'game':
            user_data['to_delete'].append(
                bot.send_game(update.effective_chat.id, msg['file_id']))

        elif msg['type'] == 'animation':
            user_data['to_delete'].append(
                bot.send_animation(update.effective_chat.id, msg['file_id']))

        elif msg['type'] == 'video':
            user_data['to_delete'].append(
                bot.send_video(update.effective_chat.id, msg['file_id']))

        elif msg['type'] == 'video_note':
            user_data['to_delete'].append(
                bot.send_video_note(update.effective_chat.id, msg['file_id']))


def make_report_keyboard(report, to_admin=False, show_trash=False):
    if to_admin:
        """
                1) нет ответа, вопрос - 1 текст
                       [Удалить, Ответить]
                2) нет ответа, вопрос - есть файл
                        [Удалить, Ответить]

                3) ответ - текст, вопрос - текст
                            [Удалить]

                4) ответ - текст, вопрос - файл
                       [Просмотр, Удалить]
                5) ответ - файл, вопрос - текст
                       [Просмотр, Удалить]
                6) ответ - файл, вопрос - файл
                       [Просмотр, Удалить]
            """
        if report.get('have_file'):
            if report['answer']:
                keyboard = [[InlineKeyboardButton('Delete', callback_data=f"delete_report/{report['_id']}"),
                             InlineKeyboardButton('Open', callback_data=f"open_report/{report['_id']}")]]
            else:
                keyboard = [[InlineKeyboardButton('Delete', callback_data=f"delete_report/{report['_id']}"),
                            InlineKeyboardButton('Reply', callback_data=f"reply_on_report/{report['_id']}")]]
        else:
            if report.get('answer'):
                keyboard = [[InlineKeyboardButton('Delete', callback_data=f"delete_report/{report['_id']}")]]
            else:
                keyboard = [[InlineKeyboardButton('Delete', callback_data=f"delete_report/{report['_id']}"),
                             InlineKeyboardButton('Reply', callback_data=f"reply_on_report/{report['_id']}")]]
        if show_trash:
            keyboard = [[InlineKeyboardButton('Restore', callback_data=f"restore/{report['_id']}")]]
    else:
        if report.get('have_file'):
            keyboard = [[InlineKeyboardButton('Open', callback_data=f"open_report/{report['_id']}")]]
        else:
            keyboard = None
    return InlineKeyboardMarkup(keyboard) if keyboard else keyboard


def create_template_part(messages, have_file=False):
    string = 'contains - '
    if len(messages) == 1:
        if messages[0]['type'] == 'text':
            string = messages[0]['file_id']
        else:
            have_file = True
            string += 'one {} file'.format(messages[0]['type'])
    else:
        messages_types = dict()
        for message in messages:
            if messages_types.get(message['type']):
                messages_types[message['type']] += 1
            else:
                if message['type'] != 'text':
                    have_file = True
                messages_types[message['type']] = 1

        for msg_type, count in messages_types.items():
            if count == 1:
                string += '{} {} file. '.format(count, msg_type)
            else:
                string += '{} {} files. '.format(count, msg_type)
    return string, have_file


# from user input
def get_message(message):
    # TODO: remember captions?
    #       join text messages
    #       switch case as a dict ?

    if message.text:
        # bot.send_message(user_data['channel'], update.message.text)
        message = dict(file_id=message.text, type='text')

    elif message.photo:
        photo_file = message.photo[0].get_file().file_id
        # bot.send_photo(chat_id=user_data['channel'], photo=photo_file)
        # if update.message.caption:
        #     print(update.message.caption)
        message = dict(file_id=photo_file, type='photo')

        # pprint(update.to_dict())

    elif message.audio:  # or update.message.video_note:
        audio_file = message.audio.get_file().file_id
        # bot.send_audio(user_data['channel'], audio_file)
        message = dict(file_id=audio_file, type='audio')

    elif message.voice:
        voice_file = message.voice.get_file().file_id
        # bot.send_voice(user_data['channel'], voice_file)
        message = dict(file_id=voice_file, type='voice')

    elif message.document:
        document_file = message.document.get_file().file_id
        # bot.send_document(user_data['channel'], document_file)
        message = dict(file_id=document_file, type='document')

    elif message.sticker:
        sticker_file = message.sticker.get_file().file_id
        # bot.send_sticker(user_data['channel'], sticker_file)
        message = dict(file_id=sticker_file, type='sticker')

    elif message.game:
        sticker_file = message.game.get_file().file_id
        # bot.send_game(user_data['channel'], sticker_file)
        message = dict(file_id=sticker_file, type='game')

    elif message.animation:
        animation_file = message.animation.get_file().file_id
        # bot.send_animation(user_data['channel'], animation_file)
        message = dict(file_id=animation_file, type='animation')

    elif message.video:
        video_file = message.video.get_file().file_id
        # bot.send_video(user_data['channel'], video_file)
        message = dict(file_id=video_file, type='video')

    elif message.video_note:
        video_note_file = message.audio.get_file().file_id
        # bot.send_video_note(user_data['channel'], video_note_file)
        message = dict(file_id=video_note_file, type='video_note')

    else:
        message = dict(file_id=None, type=None)
    return message


"""
    если только только текст в вопросе и в ответе-> 
        вставляем текст в шаблон
            [без клавиатуры]

    если в вопросе или в ответе не текст ->
        вставляем в шаблон количество и тип сообщений
            [open]
    если вопрос текст, а ответ не текст или наоборот ->
        вставляем в шаблон что текст -> 
            вставляем в шаблон количество и тип сообщений там где не текст ->
                [open]


    Все возможные выводы:
    1) когда пишешь сообщения:
        
        user - Your report contains:
               {messages_from_report}
               Send a new message if u want to add more 
               [[Send], [Cancel]]
        admin -
    
    2) Потдверждение на отправку
        
        # user - Your report contains:
        #        {messages_from report}
        #        Are you sure u want to send your report?
        #        [[Send], [back_to_main]]
        
        # admin - 
    
    3) Список сообщений:
        
        user - Here is the list of your reports
               {user_report_template}
                [[Open] or None] -> Open 
               Current page
               [[back] or + [pages_keyboard]]
        
        admin - 
    
    4) Open -> если в вопросе или в ответе есть файлы. меню для просмотра этих файлов из репорта 
        
        user - {user_report_template}
                     [Back]
                Here is your Messages:
                {user_files_from_report}
                
                
        
"""


# TODO: better, and how to delete it without user_data
def send_notification_to_admins(bot, user_data, report, lang):
    for admin in support_admins_table.find():
        # user_data['to_delete'].append(
            bot.send_message(admin['chat_id'],
                             get_str(lang, 'admin_notification') +
                             get_str(lang, 'admin_report_template',
                                     report['username'],
                                     report['category'],
                                     str(report['timestamp']).split('.')[0],
                                     report['user_msg_string'],
                                     report['answer_msg_string'])
                             # reply_markup=make_report_keyboard(report, to_admin=True)
                             # ))
                             )


# TODO: better, and how to delete it without user_data
def send_notification_to_user(bot, user_data, report, lang):
    # user_data['to_delete'].append(
        bot.send_message(report['chat_id'],
                         get_str(lang, 'user_notification') +
                         get_str(lang, 'user_report_template',
                                 report['category'],
                                 str(report['timestamp']).split('.')[0],
                                 report['user_msg_string'],
                                 report['answer_msg_string'])
                         # reply_markup=make_report_keyboard(report)
                         # )
                         )


class Welcome(object):
    def start(self, bot, update, user_data):
        user_data['report'] = list()
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        if support_admins_table.find().count() == 0:
            support_admins_table.insert_one({'user_id': update.effective_user.id,
                                             'chat_id': update.effective_chat.id,
                                             'username': update.effective_user.name})
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'start_message'),
                             reply_markup=keyboard(lang, 'user_start_keyboard')))
        return ConversationHandler.END

    def test_admin(self, bot, update, user_data):
        user_data['answer_to_report'] = list()
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'admin_menu'),
                             reply_markup=keyboard(lang, 'admin_start_keyboard')))
        return ConversationHandler.END


# USER SIDE
class UserSupportBot(object):
    # 'Contacts' button
    def contacts(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(lang, 'contacts')
                             # reply_markup=user_start_keyboard
                             ))
        return ConversationHandler.END

    # 'Send report' button
    def choose_category(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(lang, 'choose_category'),
                             reply_markup=keyboard(lang, 'categories_keyboard')))
        return CHOOSE_CATEGORY

    @run_async
    def start_answering(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        if update.callback_query:
            user_data['category'] = update.callback_query.data.split('/')[1]
        else:
            # if len(update.message.text) > 200:
            #     user_data['to_delete'].append(
            #         bot.send_message())
            user_data['category'] = update.message.text

        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'enter_message'),
                             reply_markup=keyboard(lang, 'cancel_report')))
        return MESSAGE

    @run_async
    def received_message(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        # TODO: AttributeError: 'NoneType' object has no attribute 'get_file' when video message
        message = get_message(update.message)
        user_data['report'].append(message)
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'report_contains')))
        send_messages_from_report(bot, update, user_data, user_data['report'])
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'enter_message_2'),
                             reply_markup=keyboard(lang, 'final_keyboard')))
        return MESSAGE

    def confirm_send(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'report_contains')))
        send_messages_from_report(bot, update, user_data, user_data['report'])
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(lang, 'confirm_message'),
                             reply_markup=keyboard(lang, 'confirm_keyboard')))
        return CONFIRM_SEND_REPORT

    def finish_send_report(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        user_msg_string, have_file = create_template_part(user_data['report'])
        _id = users_messages_to_admin_table.insert_one({"user_full_name": update.effective_user.full_name,
                                                        "username": update.effective_user.name,
                                                        "chat_id": update.effective_chat.id,
                                                        "user_id": update.effective_user.id,
                                                        "timestamp": datetime.datetime.now(),
                                                        "category": user_data['category'],
                                                        "messages": user_data["report"],
                                                        'user_msg_string': user_msg_string,
                                                        'answer': None,
                                                        'answer_msg_string': get_str(lang, 'not_yet'),
                                                        'deleted': False,
                                                        'have_file': have_file
                                                        }).inserted_id
        update.callback_query.answer(text=get_str(lang, 'blink_success_send_report'))
        send_notification_to_admins(bot, user_data,
                                    users_messages_to_admin_table.find_one({'_id': _id}), lang)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(lang, 'finish_send_report'),
                             reply_markup=keyboard(lang, 'user_start_keyboard')))
        user_data['report'] = list()
        return ConversationHandler.END

    # 'My reports' button
    def my_reports(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        """
        1) кнопка страницы -> query_data
        2) back -> user_data
        3) start -> 1
        """
        try:
            user_data['page'] = int(update.callback_query.data)
        except ValueError:
            if update.callback_query.data == 'user_inbox_messages':
                user_data['page'] = 1

        send_reports_layout(bot, update, user_data, user_data['page'])
        return USER_INBOX

    def single_report(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        report = users_messages_to_admin_table.find_one({'_id': ObjectId(update.callback_query.data.split('/')[1])})
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'user_report_template',
                                     report['category'],
                                     str(report['timestamp']).split('.')[0],
                                     report['user_msg_string'],
                                     report['answer_msg_string']),
                             reply_markup=keyboard(lang, 'back_to_inbox_keyboard')))
        open_report(bot, update, user_data, report)
        return SINGLE_REPORT

    @run_async
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        bot.send_message(update.message.chat_id,
                         "Command canceled")

        logger.warning('Update "%s" caused error "%s"', update, error)
        return ConversationHandler.END

    def back(self, bot, update, user_data):
        pass


# ADMIN SIDE
class AdminSupportBot(object):
    def inbox_reports(self, bot, update, user_data):
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        # !!!!!!!!!!
        user_data['answer_to_report'] = list()
        # !!!!!!!!!!
        try:
            user_data['page'] = int(update.callback_query.data)
        except ValueError:
            if update.callback_query.data == 'admin_inbox_messages':
                user_data['page'] = 1
        delete_messages(bot, update, user_data)
        send_reports_layout(bot, update, user_data, user_data['page'], to_admin=True)
        return ADMIN_INBOX

    def single_report(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        report = users_messages_to_admin_table.find_one({'_id': ObjectId(update.callback_query.data.split('/')[1])})
        single_report_keyboard = [[InlineKeyboardButton(get_str(lang, 'BACK'), callback_data='return_to_admin_inbox')]] + \
                                 [[InlineKeyboardButton(get_str(lang, 'delete_btn'), callback_data=f"delete_report/{report['_id']}")]] \
            if report['answer'] else \
            [[InlineKeyboardButton(get_str(lang, 'delete_btn'), callback_data=f"delete_report/{report['_id']}"),
              InlineKeyboardButton(get_str(lang, 'reply_btn'), callback_data=f"reply_on_report/{report['_id']}")]]

        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'admin_report_template',
                                     report['username'],
                                     report['category'],
                                     str(report['timestamp']).split('.')[0],
                                     report['user_msg_string'],
                                     report['answer_msg_string']),
                             reply_markup=InlineKeyboardMarkup(single_report_keyboard)))
        open_report(bot, update, user_data, report)
        return ADMIN_SINGLE_REPORT

    def confirm_move_to_trash(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        report = users_messages_to_admin_table.find_one({'_id': ObjectId(update.callback_query.data.split('/')[1])})
        user_data['move_to_trash'] = report
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'admin_report_template',
                                     report['username'],
                                     report['category'],
                                     str(report['timestamp']).split('.')[0],
                                     report['user_msg_string'],
                                     report['answer_msg_string'])))
        open_report(bot, update, user_data, report)
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'confirm_delete'),
                             reply_markup=keyboard(lang, 'confirm_delete_keyboard')))
        return CONFIRM_DELETE

    def finish_move_to_trash(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        users_messages_to_admin_table.update_one({'_id': user_data['move_to_trash']['_id']},
                                                 {'$set': {'deleted': True}})
        send_reports_layout(bot, update, user_data, 1, to_admin=True)
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'finish_move_to_trash')))
        return ADMIN_INBOX

    def start_answering(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        report = users_messages_to_admin_table.find_one({'_id': ObjectId(update.callback_query.data.split('/')[1])})
        user_data['processed_report'] = report
        user_data['processed_report_template'] = \
            get_str(lang, 'admin_report_template',
                    report['username'],
                    report['category'],
                    str(report['timestamp']).split('.')[0],
                    report['user_msg_string'],
                    report['answer_msg_string'])
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             user_data['processed_report_template']))
        open_report(bot, update, user_data, report)
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'admin_give_answer'),
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'),
                                                        callback_data='return_to_admin_inbox')]])))
        return ANSWERING

    def received_message(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        message = get_message(update.message)
        user_data['answer_to_report'].append(message)
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             user_data['processed_report_template']))
        open_report(bot, update, user_data, user_data['processed_report'])
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'admin_give_answer_3')))
        send_messages_from_report(bot, update, user_data, user_data['answer_to_report'])
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'admin_give_answer_2'),
                             reply_markup=keyboard(lang, 'admin_final_keyboard')))
        return ANSWERING

    def confirm_send_answer(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             user_data['processed_report_template']))
        open_report(bot, update, user_data, user_data['processed_report'])
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'admin_give_answer_3')))
        send_messages_from_report(bot, update, user_data, user_data['answer_to_report'])
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(lang, 'confirm_answer'),
                             reply_markup=keyboard(lang, 'admin_confirm_keyboard')))
        return CONFIRM_SEND_ANSWER

    def finish_send_answer(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        answer_msg_string, have_file = \
            create_template_part(user_data['answer_to_report'], user_data['processed_report']['have_file'])
        users_messages_to_admin_table.update_one({'_id': user_data['processed_report']['_id']},
                                                 {'$set': {'answer': user_data['answer_to_report'],
                                                           # 'answer_messages_types': admin_answer_messages_types,
                                                           'answer_msg_string': answer_msg_string,
                                                           'have_file': have_file}})
        update.callback_query.answer(text=get_str(lang, 'blink_success_send_answer'))
        # TODO: user_data['processed_report'] contains Not yet... but need to contain answer_msg_string
        send_notification_to_user(bot, user_data,
                                  users_messages_to_admin_table.find_one(
                                      {'_id': user_data['processed_report']['_id']}), lang)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(lang, 'finish_send_answer'),
                             reply_markup=keyboard(lang, 'admin_start_keyboard')))
        user_data['answer_to_report'] = list()
        return ConversationHandler.END

    def trash(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        send_reports_layout(bot, update, user_data, 1, to_admin=True, show_trash=True)
        return TRASH

    def restore_from_trash(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

        report = users_messages_to_admin_table.find_one({'_id': ObjectId(update.callback_query.data.split('/')[1])})

    def manage_admins(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']

    def black_list(self, bot, update, user_data):
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']


# START_HANDLER = CommandHandler('start', Welcome().start, pass_user_data=True)
START_SUPPORT_HANDLER = CallbackQueryHandler(Welcome().start,
                                             pattern=r"contact", pass_user_data=True)

# USER SIDE
CONTACTS_HANDLER = CallbackQueryHandler(UserSupportBot().contacts, pattern=r"contacts", pass_user_data=True)

SEND_REPORT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(UserSupportBot().choose_category,
                                       pattern=r"send_report", pass_user_data=True)],

    states={
        CHOOSE_CATEGORY: [MessageHandler(Filters.text, UserSupportBot().start_answering, pass_user_data=True),
                          CallbackQueryHandler(UserSupportBot().start_answering,
                                               pattern=r"category", pass_user_data=True),
                          # CallbackQueryHandler(Welcome().start, pattern=r"cancel_report", pass_user_data=True)
                          ],

        MESSAGE: [MessageHandler(Filters.all, UserSupportBot().received_message, pass_user_data=True),
                  CallbackQueryHandler(UserSupportBot().confirm_send,
                                       pattern=r"confirm_send", pass_user_data=True)
                  # CallbackQueryHandler(Welcome().start, pattern=r"cancel_report", pass_user_data=True)
                  ],

        CONFIRM_SEND_REPORT: [CallbackQueryHandler(UserSupportBot().finish_send_report,
                                                   pattern=r"send", pass_user_data=True)]
    },

    fallbacks=[CallbackQueryHandler(Welcome().start, pattern=r"cancel_report", pass_user_data=True)
               # CallbackQueryHandler(callback=UserSupportBot().back, pattern=r"cancel_report"),
               # CommandHandler('cancel', UserSupportBot().back, pass_user_data=True),
               # MessageHandler(filters=Filters.command, callback=UserSupportBot().error)
               ]
)

USER_REPORTS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(UserSupportBot().my_reports,
                                       pattern=r"user_inbox_messages", pass_user_data=True)],

    states={
        USER_INBOX: [CallbackQueryHandler(UserSupportBot().single_report,
                                          pattern=r"open_report", pass_user_data=True),
                     CallbackQueryHandler(UserSupportBot().my_reports,
                                          pattern='^[0-9]+$', pass_user_data=True)],

        SINGLE_REPORT: [CallbackQueryHandler(UserSupportBot().my_reports,
                                             pattern=r"back_to_user_inbox", pass_user_data=True)]

    },

    fallbacks=[CallbackQueryHandler(Welcome().start, pattern=r"back", pass_user_data=True)]
)


# ADMIN SIDE
ADMIN_REPORTS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(AdminSupportBot().inbox_reports,
                                       pattern=r"admin_inbox_messages", pass_user_data=True)],
    states={
        ADMIN_INBOX: [CallbackQueryHandler(AdminSupportBot().single_report,
                                           pattern=r"open_report", pass_user_data=True),
                      CallbackQueryHandler(AdminSupportBot().confirm_move_to_trash,
                                           pattern=r"delete_report", pass_user_data=True),
                      CallbackQueryHandler(AdminSupportBot().start_answering,
                                           pattern=r"reply_on_report", pass_user_data=True),
                      CallbackQueryHandler(AdminSupportBot().inbox_reports,
                                           pattern='^[0-9]+$', pass_user_data=True)],

        ANSWERING: [MessageHandler(Filters.all, AdminSupportBot().received_message, pass_user_data=True),
                    CallbackQueryHandler(AdminSupportBot().confirm_send_answer,
                                         pattern=r"confirm_answer_send", pass_user_data=True),

                    CallbackQueryHandler(AdminSupportBot().inbox_reports,
                                         pattern=r"return_to_admin_inbox", pass_user_data=True)],

        CONFIRM_SEND_ANSWER: [CallbackQueryHandler(AdminSupportBot().finish_send_answer,
                                                   pattern=r"send_answer", pass_user_data=True),

                              CallbackQueryHandler(AdminSupportBot().inbox_reports,
                                                   pattern=r"return_to_admin_inbox", pass_user_data=True)],

        ADMIN_SINGLE_REPORT: [CallbackQueryHandler(AdminSupportBot().confirm_move_to_trash,
                                                   pattern=r"delete_report", pass_user_data=True),
                              CallbackQueryHandler(AdminSupportBot().start_answering,
                                                   pattern=r"reply_on_report", pass_user_data=True),
                              CallbackQueryHandler(AdminSupportBot().inbox_reports,
                                                   pattern=r"return_to_admin_inbox", pass_user_data=True)],
        CONFIRM_DELETE: [CallbackQueryHandler(AdminSupportBot().finish_move_to_trash,
                                              pattern=r"remove", pass_user_data=True),
                         CallbackQueryHandler(AdminSupportBot().inbox_reports,
                                              pattern=r"return_to_admin_inbox", pass_user_data=True)]

    },

    fallbacks=[CallbackQueryHandler(Welcome().test_admin, pattern=r"back", pass_user_data=True)]
)

TRASH_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(AdminSupportBot().trash,
                                       pattern=r"trash", pass_user_data=True)],
    states={
        TRASH: [CallbackQueryHandler(AdminSupportBot().restore_from_trash,
                                     pattern=r"restore", pass_user_data=True)]
    },

    fallbacks=[]
)

MANAGE_ADMINS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(AdminSupportBot().manage_admins,
                                       pattern=r"manage_admins", pass_user_data=True)],
    states={
        TRASH: []
    },

    fallbacks=[]
)

BLACK_LIST_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(AdminSupportBot().black_list,
                                       pattern=r"black_list", pass_user_data=True)],
    states={
        TRASH: []
    },

    fallbacks=[]
)

