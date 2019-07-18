# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import datetime
from math import ceil
from pprint import pprint
from bson import ObjectId
import requests
from validate_email import validate_email
from uuid import uuid4
from pprint import pprint
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler, Updater)
from telegram.error import TelegramError
import logging
from bot_father.db import bot_father_bots_table, bot_father_users_table
from bot_father import strings
from bot_father.support_bot import \
    START_SUPPORT_HANDLER, CONTACTS_HANDLER, SEND_REPORT_HANDLER, \
    USER_REPORTS_HANDLER, ADMIN_REPORTS_HANDLER, Welcome
from bot_father.strings import get_str, categories

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: 1) realy need third step in guide?
#       3) how to know that bot token not in use
#       4) unknown commands
#       5) restriction on bot count
#       6) changing bot_name and bot_username loop
#       7) lang remember using user_data
#       8) adding already added or exist emails ! !


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


def map_email(email):
    return {
        'email': email,
        'password': str(uuid4())[:8]
    }


def create_keyboard(buttons, extra_buttons):
    pairs = list(zip(buttons[::2], buttons[1::2]))
    if len(buttons) % 2 == 1:
        pairs.append((buttons[-1],))
    pairs.extend([extra_buttons])
    return InlineKeyboardMarkup(pairs)


def emails_layout(user_data, text):
    result = text + '\n'
    if len(user_data['request']['admins']) > 0:
        result += 'Admins:'
        for i in user_data['request']['admins']:
            result += f"\n{i['email']}"
    return result


TERMS_OF_USE, TOKEN_REQUEST, ADMIN_EMAILS_REQUEST, ADD_EMAIL, WELCOME_MESSAGE, CHOOSE_CATEGORY, \
    CHOOSE_BOT_FOR_MANAGE, BOT_MANAGE, CONFIRM_DELETE_BOT, ADD_ADMINS, DELETE_ADMIN, CONFIRM_DELETE_ADMIN = range(12)


def keyboard(lang, kb_name):
    keyboard_dict = dict(
        cancel_button=InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'),
                                           callback_data='cancel'),
        continue_button=InlineKeyboardButton(get_str(lang, 'continue_button_text'),
                                             callback_data='continue'),
        back_button=InlineKeyboardButton(get_str(lang, 'BACK'),
                                         callback_data='back'),

        cancel_keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'),
                                                                    callback_data='cancel')]]),
        continue_cancel_keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'),
                                                                             callback_data='cancel'),
                                                        InlineKeyboardButton(get_str(lang, 'continue_button_text'),
                                                                             callback_data='continue')]]),
        delete_back_keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(get_str(lang, 'DELETE'),
                                                                         callback_data='delete_bot'),
                                                    InlineKeyboardButton(get_str(lang, 'BACK'),
                                                                         callback_data='back')]]),
        add_cancel_keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'),
                                                                        callback_data='cancel'),
                                                   InlineKeyboardButton(get_str(lang, 'add_button'),
                                                                        callback_data='add_admins')]]),
        delete_cancel_keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(get_str(lang, 'DELETE_ADMIN'),
                                                                           callback_data='delete_admin'),
                                                      InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'),
                                                                           callback_data='cancel')]]),
        lang_keyboard=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_str(lang, 'en'), callback_data='language/ENG')],
            [InlineKeyboardButton(get_str(lang, 'ru'), callback_data='language/RUS')]]),

        main_keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(text=get_str(lang, 'CREATE_NEW_BOT'),
                                                                  callback_data='create_new_bot'),
                                             InlineKeyboardButton(text=get_str(lang, 'manage_bots_button'),
                                                                  callback_data='manage_bots')],
                                            [InlineKeyboardButton(text=get_str(lang, 'contact_button'),
                                                                  callback_data='contact')],
                                            [InlineKeyboardButton(get_str(lang, 'lang_button'),
                                                                  callback_data='lang_menu')]]),
        terms_of_use_keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(get_str(lang, 'terms_as_text_button'),
                                                                          callback_data='as_text_terms'),
                                                     InlineKeyboardButton(get_str(lang, 'terms_as_doc_button'),
                                                                          callback_data='as_doc_terms')],
                                                    [InlineKeyboardButton(get_str(lang, 'agree_with_terms_button'),
                                                                          callback_data='agree_with_terms')],
                                                    [InlineKeyboardButton(get_str(lang, 'CANCEL_CREATION'),
                                                                          callback_data='cancel')]]),

        bot_manage_keyboard=InlineKeyboardMarkup([[InlineKeyboardButton(get_str(lang, 'DELETE'),
                                                                        callback_data='confirm_delete'),
                                                   InlineKeyboardButton(get_str(lang, 'ADD_ADMINS'),
                                                                        callback_data='add_admins'),
                                                   InlineKeyboardButton(get_str(lang, 'DELETE_ADMIN'),
                                                                        callback_data='delete_admins')],
                                                  [InlineKeyboardButton(get_str(lang, 'BACK'),
                                                                        callback_data='back')]])
    )
    return keyboard_dict[kb_name]


class BotFather(object):
    # Start conversation /start
    def start(self, bot, update, user_data):
        user_data.clear()
        delete_messages(bot, update, user_data)
        user = bot_father_users_table.find_one({'user_id': update.effective_user.id})
        if user:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(user['lang'], 'NO_CONTEXT'),
                                 reply_markup=keyboard(user['lang'], 'main_keyboard')))
        else:
            bot_father_users_table.insert_one({'user_id': update.effective_user.id,
                                               'lang': 'ENG',
                                               'username': update.effective_user.username})
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str('ENG', 'language_menu'),
                                 reply_markup=keyboard('ENG', 'lang_keyboard')))
        return ConversationHandler.END

    def lang_menu(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'language_menu'),
                             reply_markup=keyboard(lang, 'lang_keyboard')))
        return ConversationHandler.END

    def set_lang(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        new_lang = update.callback_query.data.split('/')[1]
        bot_father_users_table.update_one({'user_id': update.effective_user.id},
                                          {'$set': {'lang': new_lang}})
        user_data['to_delete'].append(
            bot.send_message(update.effective_user.id,
                             get_str(new_lang, 'NO_CONTEXT'),
                             reply_markup=keyboard(new_lang, 'main_keyboard')))
        return ConversationHandler.END

    # 'Create bot' button
    def terms_of_use(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        if update.message:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'terms_of_use_menu'),
                                 reply_markup=keyboard(lang, 'terms_of_use_keyboard')))

        elif update.callback_query.data == 'as_text_terms':
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'terms_of_use_in_text') +
                                 get_str(lang, 'terms_of_use_menu'),
                                 reply_markup=keyboard(lang, 'terms_of_use_keyboard')))

        elif update.callback_query.data == 'as_doc_terms':
            user_data['to_delete'].append(
                bot.send_document(update.effective_chat.id,
                                  open('bot_father/terms_of_use.docx', 'rb'),
                                  caption=get_str(lang, 'terms_of_use_menu'),
                                  reply_markup=keyboard(lang, 'terms_of_use_keyboard')))

        else:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'terms_of_use_menu'),
                                 reply_markup=keyboard(lang, 'terms_of_use_keyboard')))
        return TERMS_OF_USE

    def request_token(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'TOKEN_REQUEST'),
                             reply_markup=keyboard(lang, 'cancel_keyboard')))
        return TOKEN_REQUEST

    def request_email(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        resp = requests.get(f'https://api.telegram.org/bot{update.message.text}/getMe').json()
        print(resp)
        if resp.get('ok'):
            if not bot_father_bots_table.find_one({'token': update.message.text}):
                user_data['request'] = dict()
                user_data['request']['admins'] = list()
                user_data['request']['token'] = update.message.text
                # email request
                user_data['to_delete'].append(
                    bot.send_message(update.effective_chat.id,
                                     get_str(lang, 'ADMIN_EMAILS_REQUEST'),
                                     reply_markup=keyboard(lang, 'cancel_keyboard')))
                return ADMIN_EMAILS_REQUEST
            else:
                # bot exist in db
                user_data['to_delete'].append(
                    bot.send_message(update.effective_chat.id,
                                     get_str(lang, 'token_already_exist',
                                             f"@{resp['result']['username']}"),
                                     reply_markup=keyboard(lang, 'cancel_keyboard')))
                return TOKEN_REQUEST
        else:
            # wrong token
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'WRONG_TOKEN'),
                                 reply_markup=keyboard(lang, 'cancel_keyboard')))
            return TOKEN_REQUEST

    def add_email(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        # https://pypi.org/project/validate_email/
        is_valid = validate_email(update.message.text)
        if is_valid:
            user_data['request']['admins'].append(map_email(update.message.text))
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 emails_layout(user_data, get_str(lang, 'NEXT_EMAIL_REQUEST')),
                                 reply_markup=keyboard(lang, 'continue_cancel_keyboard')))
        else:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 emails_layout(user_data, get_str(lang, 'WRONG_EMAIL')),
                                 reply_markup=keyboard(lang, 'continue_cancel_keyboard')
                                 if user_data['request']['admins'] else
                                 keyboard(lang, 'cancel_keyboard')))
        return ADD_EMAIL

    def enter_welcome_message(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'WELCOME_MESSAGE_REQUEST'),
                             reply_markup=keyboard(lang, 'cancel_keyboard')))
        return WELCOME_MESSAGE

    def category_choose(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['request']['welcomeMessage'] = update.message.text
        kb = create_keyboard([InlineKeyboardButton(i, callback_data=i)
                              for i in categories.get(lang)],
                             [keyboard(lang, 'cancel_button')])
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'OCCUPATION_REQUEST'),
                             reply_markup=kb))
        return CHOOSE_CATEGORY

    def finish_creating(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        # request to get bot username for finish message and bot name for api request
        resp = requests.get(f"https://api.telegram.org/bot{user_data['request']['token']}/getMe").json()
        # get name before sending coz user can change it between state
        user_data['request']['name'] = resp['result']['first_name']
        user_data['request']['buttons'] = categories.get(update.callback_query.data)
        user_data['request']['lang'] = lang
        user_data['request']['superuser'] = update.effective_user.id

        user_data['to_save'] = dict()
        # user_data['to_save']['request'] = user_data['request']
        # first entered email is superuser email
        user_data['to_save']['super_user'] = user_data['request']['admins'][0]
        user_data['to_save']['super_user']['id'] = update.effective_user.id
        # admins + super_user
        user_data['to_save']['all_admins'] = user_data['request']['admins']
        # admins without super user
        user_data['to_save']['admins'] = user_data['request']['admins'][1:]
        user_data['to_save']['timestamp'] = datetime.now()
        user_data['to_save']['bot_id'] = resp['result']['id']
        user_data['to_save']['bot_username'] = '@' + resp['result']['username']
        user_data['to_save']['bot_name'] = resp['result']['first_name']
        user_data['to_save']['admins_id'] = [update.effective_user.id]
        user_data['to_save']['token'] = user_data['request']['token']
        user_data['to_save']['lang'] = user_data['request']['lang']  # ?

        pprint(user_data['to_save'])
        resp = requests.post('http://localhost:8000/crowdbot',
                             json={'params': user_data['request']})
        if resp.status_code == 200:
            bot_father_bots_table.insert_one(user_data['to_save'])
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'BOT_READY',
                                         user_data['to_save']['bot_username']),
                                 reply_markup=keyboard(lang, 'main_keyboard')))
            user_data.clear()
        else:
            print('status code not 200!')
            print(resp)
        return ConversationHandler.END

    def manage_bots(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        # why can access bots variable only one time?
        bots = bot_father_bots_table.find({'admins_id': update.effective_user.id})
        user_data['processed_bots'] = dict()
        for i in bots:
            user_data['processed_bots'][str(i['_id'])] = i
        if bots.count() > 0:
            kb = create_keyboard([InlineKeyboardButton(bot['bot_name'],
                                                       callback_data=_id)
                                  for _id, bot in user_data['processed_bots'].items()],
                                 [keyboard(lang, 'back_button')])
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'SELECT_BOT_TO_MANAGE') +
                                 get_str(lang, 'your_bots',
                                         '\n'.join([f"{i['bot_name']} - {i['bot_username']}"
                                                    for _id, i in user_data['processed_bots'].items()])),
                                 reply_markup=kb))
            return CHOOSE_BOT_FOR_MANAGE
        else:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'NO_BOTS'),
                                 reply_markup=keyboard(lang, 'main_keyboard')))
            return ConversationHandler.END

    def bot_menu(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        if update.callback_query.data != 'back':
            user_data['processed_bot'] = user_data['processed_bots'][update.callback_query.data]
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'CHOOSE_ACTION') +
                             get_str(lang, 'bot_template',
                                     user_data['processed_bot']['bot_name'],
                                     '\n'.join([i['email'] for i in user_data['processed_bot']['all_admins']]),
                                     str(user_data['processed_bot']['timestamp']).split('.')[0]),
                             reply_markup=keyboard(lang, 'bot_manage_keyboard')))
        return BOT_MANAGE

    def confirm_delete_bot(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'confirm_delete_bot',
                                     user_data['processed_bot']['bot_username']),
                             reply_markup=keyboard(lang, 'delete_back_keyboard')))
        return CONFIRM_DELETE_BOT

    def finish_delete_bot(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        resp = requests.delete('http://localhost:8000/crowdbot',
                               params={'token': user_data['processed_bot']['token']})
        if resp.status_code == 200:
            bot_father_bots_table.delete_one({'_id': user_data['processed_bot']['_id']})
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'BOT_DELETED',
                                         user_data['processed_bot']['bot_username']),
                                 reply_markup=keyboard(lang, 'main_keyboard')))
            user_data.clear()
        else:
            print('status code not 200!')
            print(resp)
        return ConversationHandler.END

    def add_admins(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['request'] = dict()
        user_data['request']['admins'] = list()
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'ENTER_NEW_ADMIN_EMAIL'),
                             reply_markup=keyboard(lang, 'cancel_keyboard')))
        return ADD_ADMINS

    def continue_add_admins(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        # https://pypi.org/project/validate_email/
        is_valid = validate_email(update.message.text)
        if is_valid:
            for admin in user_data['processed_bot']['admins']:
                if admin['email'] == update.message.text:
                    user_data['to_delete'].append(
                        bot.send_message(update.effective_chat.id,
                                         get_str(lang, 'add_already_exist_admin',
                                                 update.message.text),
                                         reply_markup=keyboard(lang, 'add_cancel_keyboard')
                                         if user_data['request']['admins'] else
                                         keyboard(lang, 'cancel_keyboard')))
                    return ADD_ADMINS
            user_data['request']['admins'].append(map_email(update.message.text))
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 emails_layout(user_data, get_str(lang, 'NEXT_EMAIL_REQUEST')),
                                 reply_markup=keyboard(lang, 'add_cancel_keyboard')))
        else:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 emails_layout(user_data, get_str(lang, 'WRONG_EMAIL')),
                                 reply_markup=keyboard(lang, 'add_cancel_keyboard')
                                 if user_data['request']['admins'] else
                                 keyboard(lang, 'cancel_keyboard')))
        return ADD_ADMINS

    def finish_add_admins(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['request']['token'] = user_data['processed_bot']['token']
        # print('here is user_data["request"]')
        # pprint(user_data['request'])
        resp = requests.post('http://localhost:8000/crowdbot/admin', json=user_data['request'])
        if resp.status_code == 200:
            bot_father_bots_table.update_one({'_id': user_data['processed_bot']['_id']},
                                             {'$push': {'admins': {'$each': user_data['request']['admins']},
                                                        'all_admins': {'$each': user_data['request']['admins']}}})
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'admins_added'),
                                 reply_markup=keyboard(lang, 'main_keyboard')))
            user_data.clear()
        else:
            print('status code not 200!')
            print(resp)
        return ConversationHandler.END

    def delete_admin(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        if len(user_data['processed_bot']['admins']) == 0:
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'only_one_admin'),
                                 reply_markup=keyboard(lang, 'main_keyboard')))
            user_data.clear()
            return ConversationHandler.END
        else:
            kb = create_keyboard([InlineKeyboardButton(admin['email'], callback_data=admin['email'])
                                  for admin in user_data['processed_bot']['admins']],
                                 [keyboard(lang, 'cancel_button')])
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'SELECT_ADMIN_TO_REMOVE'),
                                 reply_markup=kb))
            return DELETE_ADMIN

    def confirm_delete_admin(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        user_data['email_to_delete'] = update.callback_query.data
        user_data['to_delete'].append(
            bot.send_message(update.effective_chat.id,
                             get_str(lang, 'confirm_delete_admin',
                                     user_data['email_to_delete'],
                                     user_data['processed_bot']['bot_username']),
                             reply_markup=keyboard(lang, 'delete_cancel_keyboard')))
        return CONFIRM_DELETE_ADMIN

    def finish_delete_admin(self, bot, update, user_data):
        delete_messages(bot, update, user_data)
        lang = bot_father_users_table.find_one({'user_id': update.effective_user.id})['lang']
        resp = requests.delete('http://localhost:8000/crowdbot/admin',
                               json={'params': {'token': user_data['processed_bot']['token'],
                                                'email': user_data['email_to_delete']}})
        if resp.status_code == 200:
            bot_father_bots_table.update_one({'token': user_data['processed_bot']['token']},
                                             {'$pull': {'admins': {'email': user_data['email_to_delete']},
                                                        'all_admins': {'email': user_data['email_to_delete']}}})
            user_data['to_delete'].append(
                bot.send_message(update.effective_chat.id,
                                 get_str(lang, 'admin_removed_success',
                                         user_data['email_to_delete']),
                                 reply_markup=keyboard(lang, 'main_keyboard')))
            user_data.clear()
            return ConversationHandler.END
        else:
            print('status code not 200!')
            print(resp)
        return ConversationHandler.END


START_HANDLER = CommandHandler('start', BotFather().start, pass_user_data=True)

LANG_MENU = CallbackQueryHandler(BotFather().lang_menu,
                                 pattern=r"lang_menu", pass_user_data=True)

SET_LANG = CallbackQueryHandler(BotFather().set_lang,
                                pattern=r"language", pass_user_data=True)


CREATE_BOT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(BotFather().terms_of_use,
                                       pattern=r"create_new_bot", pass_user_data=True),
                  CommandHandler('create', BotFather().terms_of_use,
                                 pass_user_data=True)
                  ],
    states={
        TERMS_OF_USE: [CallbackQueryHandler(BotFather().terms_of_use,
                                            pattern=r"as_text_terms", pass_user_data=True),
                       CallbackQueryHandler(BotFather().terms_of_use,
                                            pattern=r"as_doc_terms", pass_user_data=True),
                       CallbackQueryHandler(BotFather().request_token,
                                            pattern=r"agree_with_terms", pass_user_data=True)],

        TOKEN_REQUEST: [MessageHandler(Filters.text, BotFather().request_email, pass_user_data=True)],

        ADMIN_EMAILS_REQUEST: [MessageHandler(Filters.text, BotFather().add_email, pass_user_data=True)],

        ADD_EMAIL: [MessageHandler(Filters.text, BotFather().add_email, pass_user_data=True),
                    CallbackQueryHandler(BotFather().enter_welcome_message,
                                         pattern=r"continue", pass_user_data=True),
                    ],


        WELCOME_MESSAGE: [MessageHandler(Filters.text, BotFather().category_choose, pass_user_data=True)],


        CHOOSE_CATEGORY: [CallbackQueryHandler(BotFather().start,
                                               pattern="^cancel$", pass_user_data=True),
                          CallbackQueryHandler(BotFather().finish_creating, pass_user_data=True)]
    },

    fallbacks=[CallbackQueryHandler(BotFather().start,
                                    pattern=r"cancel", pass_user_data=True)]
)

MANAGE_BOT_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(BotFather().manage_bots,
                                       pattern=r"manage_bots", pass_user_data=True)],
    states={
        CHOOSE_BOT_FOR_MANAGE: [CallbackQueryHandler(BotFather().start,
                                                     pattern=r"back", pass_user_data=True),
                                CallbackQueryHandler(BotFather().bot_menu, pass_user_data=True)],

        BOT_MANAGE: [CallbackQueryHandler(BotFather().confirm_delete_bot,
                                          pattern=r"confirm_delete", pass_user_data=True),
                     CallbackQueryHandler(BotFather().add_admins,
                                          pattern=r"add_admins", pass_user_data=True),
                     CallbackQueryHandler(BotFather().delete_admin,
                                          pattern=r"delete_admins", pass_user_data=True)],

        CONFIRM_DELETE_BOT: [CallbackQueryHandler(BotFather().bot_menu,
                                                  pattern='back', pass_user_data=True),
                             CallbackQueryHandler(BotFather().finish_delete_bot,
                                                  pattern=r"delete_bot", pass_user_data=True)],

        ADD_ADMINS: [MessageHandler(Filters.text, BotFather().continue_add_admins, pass_user_data=True),
                     CallbackQueryHandler(BotFather().finish_add_admins,
                                          pattern=r"add_admins", pass_user_data=True)],

        DELETE_ADMIN: [CallbackQueryHandler(BotFather().start,
                                            pattern=r"cancel", pass_user_data=True),
                       CallbackQueryHandler(BotFather().confirm_delete_admin,
                                            pass_user_data=True)],

        CONFIRM_DELETE_ADMIN: [CallbackQueryHandler(BotFather().finish_delete_admin,
                                                    pattern=r"delete_admin", pass_user_data=True)]

    },

    fallbacks=[CallbackQueryHandler(BotFather().start,
                                    pattern=r"back", pass_user_data=True),
               CallbackQueryHandler(BotFather().start,
                                    pattern=r"cancel", pass_user_data=True)]
)

BACK_TO_MAIN_MENU_HANDLER = CallbackQueryHandler(BotFather().start,
                                                 pattern=r'to_main_menu', pass_user_data=True)


def main():
    updater = Updater("836123673:AAE6AyfFCcRxjHZZhJHtdE8mKt8WNfgRm5Q")  # @crowd_supportbot
    dp = updater.dispatcher

    dp.add_handler(START_HANDLER)

    dp.add_handler(CREATE_BOT_HANDLER)
    dp.add_handler(MANAGE_BOT_HANDLER)
    dp.add_handler(LANG_MENU)
    dp.add_handler(SET_LANG)

    dp.add_handler(START_SUPPORT_HANDLER)
    dp.add_handler(CommandHandler('admin', Welcome().test_admin, pass_user_data=True))
    dp.add_handler(CONTACTS_HANDLER)
    dp.add_handler(SEND_REPORT_HANDLER)
    dp.add_handler(USER_REPORTS_HANDLER)
    dp.add_handler(ADMIN_REPORTS_HANDLER)

    dp.add_handler(BACK_TO_MAIN_MENU_HANDLER)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
