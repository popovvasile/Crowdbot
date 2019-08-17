# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
import logging
from math import ceil
from bson import ObjectId
from pprint import pprint

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)

from bot_father.config import conf
from bot_father.db import users_messages_to_admin_table, support_admins_table, bot_father_users_table
from bot_father.helper.strings import get_str, report_categories
from bot_father.helper.helper_funcs import delete_messages, Notification, admin_report_template, user_report_template

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def keyboard(user_data, update, kb_name):
    keyboard_dict = dict(
        user_start_keyboard=InlineKeyboardMarkup(
            list(([InlineKeyboardButton(get_str(user_data, update, 'send_report_button'), callback_data='send_report')],
                  [InlineKeyboardButton(get_str(user_data, update, 'my_reports_button'), callback_data='inbox')],
                  [InlineKeyboardButton(get_str(user_data, update, 'BACK'), callback_data='to_main_menu')]))),

        admin_start_keyboard=InlineKeyboardMarkup(
            list(([InlineKeyboardButton(get_str(user_data, update, 'trash_button'), callback_data='trash'),
                   InlineKeyboardButton(get_str(user_data, update, 'inbox_msg_button'), callback_data='inbox')],
                  [InlineKeyboardButton(get_str(user_data, update, 'manage_admins_button'),
                                        callback_data='manage_admins'),
                  InlineKeyboardButton(get_str(user_data, update, 'black_list_button'), callback_data='black_list')],
                  [InlineKeyboardButton("Bots Information", callback_data="bots_info")],
                  [InlineKeyboardButton(get_str(user_data, update, 'BACK'), callback_data='to_main_menu')]))),

        categories_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(v, callback_data=f'category/{k}')]
            for k, v in report_categories.get(user_data["lang"]).items()] +
            [[InlineKeyboardButton(get_str(user_data, update, 'BACK'),
                                   callback_data='cancel_report')]]),

        final_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=get_str(user_data, update, 'send_btn'), callback_data="confirm_send")],
            [InlineKeyboardButton(get_str(user_data, update, 'CANCEL_CREATION'), callback_data="cancel_report")]]),

        back_to_inbox_keyboard=InlineKeyboardMarkup(
            [[InlineKeyboardButton(get_str(user_data, update, 'BACK'), callback_data='back_to_inbox')]]),

        cancel_report=InlineKeyboardMarkup(
            [[InlineKeyboardButton(get_str(user_data, update, 'CANCEL_CREATION'), callback_data='cancel_report')]]),
        confirm_delete_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_str(user_data, update, 'yes'), callback_data='remove'),
             InlineKeyboardButton(get_str(user_data, update, 'BACK'), callback_data='back_to_inbox')]]),

        admin_final_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=get_str(user_data, update, 'send_btn'), callback_data="confirm_answer_send")],
            [InlineKeyboardButton(get_str(user_data, update, 'CANCEL_CREATION'), callback_data="back_to_inbox")]]),
    )
    return keyboard_dict[kb_name]


CHOOSE_CATEGORY, MESSAGE, CONFIRM_SEND_REPORT, \
    INBOX, SINGLE_REPORT, \
    ANSWERING, CONFIRM_SEND_ANSWER, \
    CONFIRM_DELETE, TRASH = range(9)


class SupportMain(object):
    """HELP METHODS"""
    def send_reports_layout(self, bot, update, user_data, show_trash=False):
        self.is_admin = user_data['is_admin']
        self.show_trash = show_trash
        self.user_data = user_data
        self.update = update

        # Create data
        if user_data.get('is_admin'):
            all_data = users_messages_to_admin_table.find(
                {'deleted': show_trash}).sort([['_id', -1]])
        else:
            all_data = users_messages_to_admin_table.find(
                {'user_id': update.effective_user.id}).sort([['_id', -1]])

        if all_data.count() == 0:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(user_data, update, 'no_reports')))

        if user_data['page'] == 1:
            data_to_send = all_data.limit(conf['PER_PAGE'])
        else:
            last_on_prev_page = (user_data['page'] - 1) * conf['PER_PAGE']
            data_to_send = [i for i in all_data[last_on_prev_page:
                                                last_on_prev_page + conf['PER_PAGE']]]
        # Pagination keyboard logic
        # to do better!
        back_button = [InlineKeyboardButton(get_str(user_data, update, "BACK"),
                                            callback_data='back')]
        total_pages = ceil(all_data.count() / conf['PER_PAGE'])
        pages_keyboard = [[], back_button]
        if total_pages <= 1:
            pages_keyboard = [back_button]
        elif 2 <= total_pages <= 8:
            for i in range(1, total_pages + 1):
                pages_keyboard[0].append(
                    InlineKeyboardButton('|' + str(i) + '|', callback_data=i)
                    if i == user_data['page'] else
                    InlineKeyboardButton(str(i), callback_data=i))
        else:
            arr = [i if i in range(user_data['page'] - 1, user_data['page'] + 3) else
                   i if i == total_pages else
                   i if i == 1 else
                   # str_to_remove
                   '' for i in range(1, total_pages + 1)]
            p_index = arr.index(user_data['page'])
            layout = list(dict.fromkeys(arr[:p_index])) + \
                     list(dict.fromkeys(arr[p_index:]))
            for num, i in enumerate(layout):
                if i == '':
                    pages_keyboard[0].append(InlineKeyboardButton('...',
                                                                  callback_data=layout[num - 1] + 1
                                                                  if num > layout.index(user_data['page']) else
                                                                  layout[num + 1] - 1))
                else:
                    pages_keyboard[0].append(InlineKeyboardButton('|' + str(i) + '|', callback_data=i)
                                             if i == user_data['page'] else
                                             InlineKeyboardButton(str(i), callback_data=i))
        # SENDING
        # Title
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(user_data, update,
                                     'trash_menu'
                                     if show_trash else
                                     'admin_all_reports_menu'
                                     if user_data.get('is_admin') else
                                     'my_reports_menu'),
                             ParseMode.MARKDOWN))
        # Reports
        for report in data_to_send:
            if user_data.get('is_admin'):
                user_data['to_delete'].append(
                    bot.send_message(update.effective_chat.id,
                                     admin_report_template(update, user_data, report),
                                     reply_markup=self.make_report_keyboard(report),
                                     parse_mode=ParseMode.HTML))
            else:
                user_data['to_delete'].append(
                    bot.send_message(update.effective_chat.id,
                                     user_report_template(update, user_data, report),
                                     reply_markup=self.make_report_keyboard(report),
                                     parse_mode=ParseMode.HTML))
        # Pages navigation
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(user_data, update,
                                     'current_page',
                                     user_data['page']),
                             reply_markup=InlineKeyboardMarkup(pages_keyboard),
                             parse_mode=ParseMode.MARKDOWN))

    # TODO: Better!
    def make_report_keyboard(self, report):
        if self.is_admin:
            if report.get('have_file'):
                if report['answer']:
                    kb = [[InlineKeyboardButton(get_str(self.user_data, self.update, 'delete_btn'),
                                                callback_data=f"delete_report/{report['_id']}"),
                           InlineKeyboardButton(get_str(self.user_data, self.update, 'open_btn'),
                                                callback_data=f"open_report/{report['_id']}")]]
                else:
                    kb = [[InlineKeyboardButton(get_str(self.user_data, self.update, 'delete_btn'),
                                                callback_data=f"delete_report/{report['_id']}"),
                           InlineKeyboardButton(get_str(self.user_data, self.update, "reply_btn"),
                                                callback_data=f"reply_on_report/{report['_id']}")]]
            else:
                if report.get('answer'):
                    kb = [[InlineKeyboardButton(get_str(self.user_data, self.update, 'delete_btn'),
                                                callback_data=f"delete_report/{report['_id']}")]]
                else:
                    kb = [[InlineKeyboardButton(get_str(self.user_data, self.update, 'delete_btn'),
                                                callback_data=f"delete_report/{report['_id']}"),
                           InlineKeyboardButton(get_str(self.user_data, self.update, "reply_btn"),
                                                callback_data=f"reply_on_report/{report['_id']}")]]
            if self.show_trash:
                kb = [[InlineKeyboardButton(get_str(self.user_data, self.update, "restore_btn"),
                                            callback_data=f"restore/{report['_id']}")]]
        else:
            if report.get('have_file'):
                kb = [[InlineKeyboardButton(get_str(self.user_data, self.update, 'open_btn'),
                                            callback_data=f"open_report/{report['_id']}")]]
            else:
                kb = None
        return InlineKeyboardMarkup(kb) if kb else kb

    def open_report(self, bot, update, user_data, report, kb=None):
        if len(report['messages']) == 1 and report['messages'][0]['type'] == 'text':
            pass
        else:
            if user_data.get('is_admin'):
                user_data['to_delete'].append(
                    bot.send_message(update.effective_chat.id,
                                     get_str(user_data, update, 'enter_message_4'),
                                     parse_mode=ParseMode.MARKDOWN))
            else:
                user_data['to_delete'].append(
                    bot.send_message(update.effective_chat.id,
                                     get_str(user_data, update, 'message'),
                                     parse_mode=ParseMode.MARKDOWN))
            self.send_messages_from_report(bot, update, user_data, report['messages'])

        if report['answer']:
            if len(report['answer']) == 1 and report['answer'][0]['type'] == 'text':
                pass
            else:
                user_data['to_delete'].append(
                    bot.send_message(update.effective_chat.id,
                                     get_str(user_data, update, 'answer'),
                                     parse_mode=ParseMode.MARKDOWN))
                self.send_messages_from_report(bot, update, user_data, report['answer'])

        if user_data['is_admin']:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 admin_report_template(update, user_data, report),
                                 reply_markup=kb,
                                 parse_mode=ParseMode.HTML))

        else:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 user_report_template(update, user_data, report),
                                 reply_markup=keyboard(user_data, update,
                                                       'back_to_inbox_keyboard'),
                                 parse_mode=ParseMode.HTML))

    def send_messages_from_report(self, bot, update, user_data, reports):
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

    def have_file(self, messages, have_file=False):
        for m in messages:
            if m["type"] != "text":
                have_file = True
                break
        return have_file

    def add_message(self, bot, update, user_data):
        # TODO: remember captions?
        # pprint(update.to_dict())

        if 'messages' not in user_data:
            user_data['messages'] = list()
        message = update.message

        if message.text:
            if len(user_data['messages']) > 0:
                if user_data['messages'][-1]['type'] == 'text':
                    user_data['messages'][-1]['file_id'] += f'\n{message.text}'
                    user_data['prev_text_msg'] = \
                        user_data['prev_text_msg'].edit_text(
                        user_data['prev_text_msg'].text + f'\n{message.text}')
                    return True
            msg = dict(file_id=message.text, type='text')
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id, msg['file_id']))
            user_data['prev_text_msg'] = user_data['to_delete'][-1]

        elif message.photo:
            photo_file = message.photo[0].get_file().file_id
            msg = dict(file_id=photo_file, type='photo')
            user_data['to_delete'].append(
                bot.send_photo(update.effective_chat.id,
                               photo=msg['file_id']))

        elif message.audio:  # or update.message.video_note:
            audio_file = message.audio.get_file().file_id
            msg = dict(file_id=audio_file, type='audio')
            user_data['to_delete'].append(
                bot.send_audio(update.effective_chat.id,
                               msg['file_id']))

        elif message.voice:
            voice_file = message.voice.get_file().file_id
            msg = dict(file_id=voice_file, type='voice')
            user_data['to_delete'].append(
                bot.send_voice(update.effective_chat.id,
                               msg['file_id']))

        elif message.document:
            document_file = message.document.get_file().file_id
            msg = dict(file_id=document_file, type='document')
            user_data['to_delete'].append(
                bot.send_document(update.effective_chat.id,
                                  msg['file_id']))

        elif message.sticker:
            sticker_file = message.sticker.get_file().file_id
            msg = dict(file_id=sticker_file, type='sticker')
            user_data['to_delete'].append(
                bot.send_sticker(update.effective_chat.id,
                                 msg['file_id']))

        elif message.game:
            sticker_file = message.game.get_file().file_id
            msg = dict(file_id=sticker_file, type='game')
            user_data['to_delete'].append(
                bot.send_game(update.effective_chat.id,
                              msg['file_id']))

        elif message.animation:
            animation_file = message.animation.get_file().file_id
            msg = dict(file_id=animation_file, type='animation')
            user_data['to_delete'].append(
                bot.send_animation(update.effective_chat.id,
                                   msg['file_id']))

        elif message.video:
            video_file = message.video.get_file().file_id
            msg = dict(file_id=video_file, type='video')
            user_data['to_delete'].append(
                bot.send_video(update.effective_chat.id,
                               msg['file_id']))

        elif message.video_note:
            pprint(update.to_dict())
            video_note_file = message.video_note.get_file().file_id
            msg = dict(file_id=video_note_file, type='video_note')
            user_data['to_delete'].append(
                bot.send_video_note(update.effective_chat.id,
                                    msg['file_id']))
        # !!! Can this function return False?
        else:
            return False
        user_data['messages'].append(msg)
        return True

    """START Support bot"""
    def start(self, bot, update, user_data):
        # to_del = user_data.get('to_delete', list())
        # is_admin = user_data.get('is_admin')
        # user_data.clear()
        # user_data['to_delete'] = to_del
        # user_data['is_admin'] = is_admin
        delete_messages(bot, update, user_data)
        if user_data.get("msg_to_send"):
            user_data["to_delete"].append(
                bot.send_message(update.effective_chat.id,
                                 user_data["msg_to_send"]))

        admins = ["@vasile_python", "@keikoobro", "@Mykyto", "@dvk88"]
        if not support_admins_table.find_one({"username": update.effective_user.name}) \
                and update.effective_user.name in admins:
            support_admins_table.insert_one({'user_id': update.effective_user.id,
                                             'chat_id': update.effective_chat.id,
                                             'username': update.effective_user.name})

        # if not user_data.get('lang'):
        #     user_data['lang'] = bot_father_users_table.find_one(
        #         {'user_id': update.effective_user.id})['lang']
        if not user_data.get('is_admin'):
            user_data['is_admin'] = False
        if support_admins_table.find_one(
                {'user_id': update.effective_user.id}):
            if update.effective_message.text == '/a':
                user_data['is_admin'] = True

        if user_data.get('is_admin'):
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(user_data, update, 'admin_menu'),
                                 reply_markup=keyboard(user_data, update, 'admin_start_keyboard')))
        else:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(user_data, update, 'start_message') +
                                 get_str(user_data, update, 'contacts'),
                                 reply_markup=keyboard(user_data, update, 'user_start_keyboard'),
                                 parse_mode=ParseMode.HTML))
        return ConversationHandler.END

    def inbox(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        try:
            user_data['page'] = int(update.callback_query.data)
        except ValueError:
            if update.callback_query.data == 'inbox':
                user_data['page'] = 1
        self.send_reports_layout(bot, update, user_data)
        return INBOX

    def single_report(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        report = users_messages_to_admin_table.find_one(
            {'_id': ObjectId(update.callback_query.data.split('/')[1])})
        if user_data.get('is_admin'):
            report_keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton(get_str(user_data, update, 'BACK'),
                                       callback_data='back_to_inbox')]] +
                [[InlineKeyboardButton(get_str(user_data, update, 'delete_btn'),
                                       callback_data=f"delete_report/{report['_id']}")]]
                if report['answer'] else
                [[InlineKeyboardButton(get_str(user_data, update, 'delete_btn'),
                                       callback_data=f"delete_report/{report['_id']}"),
                  InlineKeyboardButton(get_str(user_data, update, 'reply_btn'),
                                       callback_data=f"reply_on_report/{report['_id']}")]])
        else:
            report_keyboard = None
        self.open_report(bot, update, user_data,
                         report, report_keyboard)
        return SINGLE_REPORT

    def back_to_support_main(self, bot, update, user_data, msg_to_send=None):
        to_del = user_data.get('to_delete', list())
        is_admin = user_data.get('is_admin')
        user_data.clear()
        user_data['to_delete'] = to_del
        user_data['is_admin'] = is_admin
        # user_data['lang'] = bot_father_users_table.find_one(
        #     {'user_id': update.effective_user.id})['lang']
        if msg_to_send:
            user_data["msg_to_send"] = msg_to_send
        return self.start(bot, update, user_data)


# USER SIDE
class UserSupportBot(SupportMain):
    # 'Send report' button
    def choose_category(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(user_data, update, 'choose_category'),
                             reply_markup=keyboard(user_data, update, 'categories_keyboard')))
        return CHOOSE_CATEGORY

    # @run_async
    def start_answering(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        if update.callback_query:
            user_data['category'] = update.callback_query.data.split('/')[1]
        else:
            # if len(update.message.text) > 200:
            #     user_data['to_delete'].append(
            #         bot.send_message())
            user_data['category'] = update.message.text

        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(user_data, update, 'enter_message'),
                             reply_markup=keyboard(user_data, update, 'cancel_report')))
        return MESSAGE

    # @run_async
    def received_message(self, bot, update, user_data):
        bot.delete_message(update.effective_chat.id,
                           update.effective_message.message_id)
        if not user_data.get('messages'):
            delete_messages(bot, update, user_data)
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(user_data, update, 'report_contains'),
                                 parse_mode=ParseMode.MARKDOWN))
        if user_data.get("dynamic_menu"):
            bot.delete_message(update.effective_chat.id,
                               user_data['dynamic_menu'].message_id)
        self.add_message(bot, update, user_data)
        user_data['dynamic_menu'] = \
            bot.send_message(update.effective_chat.id,
                             get_str(user_data, update, 'enter_message_2'),
                             reply_markup=keyboard(user_data, update, 'final_keyboard'))
        return MESSAGE

    def finish_send_report(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        have_file = self.have_file(user_data["messages"])
        _id = users_messages_to_admin_table.insert_one(
            {
                "user_full_name": update.effective_user.full_name,
                "username": update.effective_user.name,
                "chat_id": update.effective_chat.id,
                "user_id": update.effective_user.id,
                "timestamp": datetime.datetime.now(),
                "messages": user_data["messages"],
                'answer': None,
                'deleted': False,
                'have_file': have_file,
                "category": user_data['category'],
             }).inserted_id
        update.callback_query.answer(text=get_str(user_data, update, 'blink_success_send_report'))
        Notification.new_report(bot, user_data, update, _id)
        # user_data['to_delete'].append(
        #     bot.send_message(update.callback_query.message.chat_id,
        #                      get_str(user_data['lang'], 'finish_send_report'),
        #                      reply_markup=keyboard(user_data['lang'], 'user_start_keyboard')
        #                      ))
        # user_data['messages'] = list()
        # user_data.clear()
        # user_data["lang"] = bot_father_users_table.find_one(
        #     {'user_id': update.effective_user.id})['lang']
        # user_data["is_admin"] = False
        # return ConversationHandler.END
        msg = get_str(user_data, update, 'finish_send_report')
        return self.back_to_support_main(bot, update, user_data, msg_to_send=msg)


# ADMIN SIDE
class AdminSupportBot(SupportMain):
    def confirm_move_to_trash(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        report = users_messages_to_admin_table.find_one(
            {'_id': ObjectId(update.callback_query.data.split('/')[1])})
        user_data['move_to_trash'] = report
        self.open_report(bot, update, user_data, report)
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(user_data, update, 'confirm_delete'),
                             reply_markup=keyboard(user_data, update, 'confirm_delete_keyboard')))
        return CONFIRM_DELETE

    def finish_move_to_trash(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        users_messages_to_admin_table.update_one({'_id': user_data['move_to_trash']['_id']},
                                                 {'$set': {'deleted': True}})
        self.send_reports_layout(bot, update, user_data)
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(user_data, update, 'finish_move_to_trash')))
        return INBOX

    def start_answering(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        report = users_messages_to_admin_table.find_one(
            {'_id': ObjectId(update.callback_query.data.split('/')[1])})
        user_data['processed_report'] = report
        self.open_report(bot, update, user_data, report)
        user_data['dynamic_menu'] = \
            bot.send_message(update.effective_chat.id,
                             get_str(user_data, update, 'admin_give_answer'),
                             reply_markup=InlineKeyboardMarkup(
                                 [[InlineKeyboardButton(get_str(user_data, update, 'CANCEL_CREATION'),
                                                        callback_data='back_to_inbox')]]),
                             parse_mode=ParseMode.MARKDOWN)
        return ANSWERING

    def received_message(self, bot, update, user_data):
        bot.delete_message(update.effective_chat.id,
                           update.effective_message.message_id)
        if not user_data.get('messages'):
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(user_data, update, 'admin_give_answer_3'),
                                 parse_mode=ParseMode.MARKDOWN))
        bot.delete_message(update.effective_chat.id,
                           user_data['dynamic_menu'].message_id)
        self.add_message(bot, update, user_data)
        user_data['dynamic_menu'] = \
            bot.send_message(update.effective_chat.id,
                             get_str(user_data, update, 'admin_give_answer_2'),
                             reply_markup=keyboard(user_data, update, 'admin_final_keyboard'))
        return ANSWERING

    def finish_send_answer(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        have_file = self.have_file(user_data['messages'], user_data['processed_report']['have_file'])
        users_messages_to_admin_table.update_one({'_id': user_data['processed_report']['_id']},
                                                 {'$set': {'answer': user_data['messages'],
                                                           'have_file': have_file}})
        update.callback_query.answer(text=get_str(user_data, update, 'blink_success_send_answer'))
        Notification.report_answered(bot, user_data, update, user_data['processed_report']['_id'])
        user_data['to_delete'].append(
            bot.send_message(update.callback_query.message.chat_id,
                             get_str(user_data, update, 'finish_send_answer'),
                             # reply_markup=keyboard(user_data['lang'], 'admin_start_keyboard')
                             ))
        user_data['messages'] = list()
        self.send_reports_layout(bot, update, user_data)
        return INBOX

    def trash(self, bot, update, user_data):
        self.send_reports_layout(bot, update, user_data, show_trash=True)
        return TRASH

    def restore_from_trash(self, bot, update, user_data):
        report = users_messages_to_admin_table.find_one({'_id': ObjectId(update.callback_query.data.split('/')[1])})

    def manage_admins(self, bot, update, user_data):
        pass

    def black_list(self, bot, update, user_data):
        pass


START_SUPPORT_HANDLER = CallbackQueryHandler(SupportMain().start,
                                             pattern=r"contact", pass_user_data=True)

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
                  CallbackQueryHandler(UserSupportBot().finish_send_report,
                                       pattern=r"confirm_send", pass_user_data=True)
                  # CallbackQueryHandler(Welcome().start, pattern=r"cancel_report", pass_user_data=True)
                  ],

        # CONFIRM_SEND_REPORT: [CallbackQueryHandler(UserSupportBot().finish_send_report,
        #                                            pattern=r"send", pass_user_data=True)]
    },

    fallbacks=[CallbackQueryHandler(SupportMain().back_to_support_main, pattern=r"cancel_report", pass_user_data=True)
               ]
)

INBOX_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SupportMain().inbox,
                                       pattern=r"inbox", pass_user_data=True)],
    states={
        INBOX: [CallbackQueryHandler(SupportMain().single_report,
                                     pattern=r"open_report", pass_user_data=True),
                CallbackQueryHandler(SupportMain().inbox,
                                     pattern='^[0-9]+$', pass_user_data=True),
                CallbackQueryHandler(AdminSupportBot().confirm_move_to_trash,
                                     pattern=r"delete_report", pass_user_data=True),
                CallbackQueryHandler(AdminSupportBot().start_answering,
                                     pattern=r"reply_on_report", pass_user_data=True)],

        SINGLE_REPORT: [CallbackQueryHandler(SupportMain().inbox,
                                             pattern=r"back_to_inbox", pass_user_data=True),
                        CallbackQueryHandler(AdminSupportBot().confirm_move_to_trash,
                                             pattern=r"delete_report", pass_user_data=True)],

        ANSWERING: [CallbackQueryHandler(SupportMain().inbox,
                                         pattern="^back_to_inbox$", pass_user_data=True),
                    MessageHandler(Filters.all, AdminSupportBot().received_message, pass_user_data=True),
                    CallbackQueryHandler(AdminSupportBot().finish_send_answer,
                                         pattern=r"confirm_answer_send", pass_user_data=True)
                    ],

        CONFIRM_DELETE: [CallbackQueryHandler(AdminSupportBot().finish_move_to_trash,
                                              pattern=r"remove", pass_user_data=True),
                         CallbackQueryHandler(SupportMain().inbox,
                                              pattern=r"back_to_inbox", pass_user_data=True)]
    },

    fallbacks=[CallbackQueryHandler(SupportMain().back_to_support_main, pattern=r"back", pass_user_data=True)]
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

