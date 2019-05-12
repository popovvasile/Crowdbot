#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import json
# import csv
import random
import logging
from uuid import uuid4
# from dropbox import dropbox, sharing

from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters, RegexHandler, \
    CallbackQueryHandler, run_async
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.inline.inlinequeryresultarticle import InlineQueryResultArticle
from telegram.inline.inputtextmessagecontent import InputTextMessageContent

from database import polls_table, poll_instances_table
from modules.create_survey import chats_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help
from modules.pollbot.basic_poll_handler import BasicPoll
from modules.pollbot.instant_runoff_poll_handler import InstantRunoffPollHandler
from modules.pollbot.custom_description_poll_handler import CustomDescriptionHandler
from modules.pollbot.multiple_options_poll_handler import MultipleOptionsHandler
from modules.pollbot.custom_description_instant_runoff_poll_handler import CustomDescriptionInstantRunoffPollHandler

POLL_TYPE_BASIC, \
POLL_TYPE_INSTANT_RUNOFF, \
POLL_TYPE_CUSTOM_DESCRIPTION, \
POLL_TYPE_INSTANT_RUNOFF_CUSTOM_DESCRIPTION, \
POLL_TYPE_MULTIPLE_OPTIONS = range(5)

POLL_HANDLERS = {
    POLL_TYPE_BASIC: BasicPoll(),
    POLL_TYPE_INSTANT_RUNOFF: InstantRunoffPollHandler(),
    POLL_TYPE_INSTANT_RUNOFF_CUSTOM_DESCRIPTION: CustomDescriptionInstantRunoffPollHandler(),
    POLL_TYPE_CUSTOM_DESCRIPTION: CustomDescriptionHandler(),
    POLL_TYPE_MULTIPLE_OPTIONS: MultipleOptionsHandler(),
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Conversation states:
NOT_ENGAGED, TYPING_TITLE, TYPING_TYPE, TYPING_OPTION, TYPING_META = range(5)
CHOOSE_TITLE, CHOOSE_OPTION = range(2)
CHOOSE_TITLE_DELETE = 21
CHOOSE_TITLE_RESULTS = 13
AFFIRMATIONS = [
    "Cool",
    "Nice",
    "Doing great",
    "Awesome",
    "Okey dokey",
    "Neat",
    "Whoo",
    "Wonderful",
    "Splendid",
]
__admin_keyboard__ = [
    InlineKeyboardButton(text="Create", callback_data="create_poll"),
    InlineKeyboardButton(text="Delete", callback_data="delete_poll"),
    InlineKeyboardButton(text="Send", callback_data="send_poll"),
]


class PollBot(object):
    def __init__(self):
        buttons = [[InlineKeyboardButton(text="Back", callback_data="cancel_poll")]]
        self.reply_markup = InlineKeyboardMarkup(
            buttons)
        done_buttons = [[InlineKeyboardButton(text="Done", callback_data="done_poll")]]
        self.done_markup = InlineKeyboardMarkup(
            done_buttons)
        send_buttons = [[InlineKeyboardButton(text="Menu", callback_data="cancel_poll"),
                         InlineKeyboardButton(text="Send", callback_data="send_poll")]]
        self.send_markup = InlineKeyboardMarkup(
            send_buttons)
    # Conversation handlers:

    @run_async
    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        bot.send_message(update.callback_query.message.chat.id,
                         'Hi! Please send me the title of your new poll', reply_markup=self.reply_markup)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        return TYPING_TITLE

    @run_async
    def handle_title(self, bot, update, user_data):
        text = update.message.text
        user_data['title'] = text
        update.message.reply_text("{}! What kind of poll is it going to be?"
                                  .format(self.get_affirmation()),
                                  reply_markup=self.assemble_reply_keyboard())

        return TYPING_TYPE

    @run_async
    def handle_type(self, bot, update, user_data):
        text = update.message.text
        polltype = next((i for i, handler in POLL_HANDLERS.items() if handler.name == text), None)
        user_data['type'] = polltype
        user_data['options'] = []
        user_data['meta'] = dict()

        if POLL_HANDLERS[polltype].requires_extra_config(user_data['meta']):
            update.message.reply_text(POLL_HANDLERS[polltype].ask_for_extra_config(user_data.get('meta')), reply_markup=self.reply_markup)
            return TYPING_META
        else:
            update.message.reply_text("{}! Now, send me the first answer option".format(
                self.get_affirmation()
            ), reply_markup=self.reply_markup)
            return TYPING_OPTION

    @run_async
    def handle_meta(self, bot, update, user_data):
        text = update.message.text
        polltype = user_data['type']
        POLL_HANDLERS[polltype].register_extra_config(text, user_data.get('meta'))

        if POLL_HANDLERS[polltype].requires_extra_config(user_data.get('meta')):
            update.message.reply_text(POLL_HANDLERS[polltype].ask_for_extra_config(user_data.get('meta')),
                                      replu_markup=self.reply_markup)
            return TYPING_META
        else:
            update.message.reply_text("{}, that's it! Next, please send me the first answer option."
                                      .format(self.get_affirmation()), replu_markup=self.reply_markup)
            return TYPING_OPTION

    def handle_option(self, bot, update, user_data):
        text = update.message.text
        handler = POLL_HANDLERS[user_data['type']]
        user_data['options'].append(text)

        if len(user_data['options']) >= handler.max_options:
            return self.handle_done(bot, update, user_data)
        update.message.reply_text("{}!".format(self.get_affirmation()), reply_markup=ReplyKeyboardRemove())
        update.message.reply_text("Now, send me another answer option or click DONE to publish.",
                                  reply_markup=self.done_markup)

        if len(user_data['options']) >= handler.max_options - 1:
            update.message.reply_text("Uh oh, you're running out of options. You can only have one more option.",
                                      replu_markup=self.reply_markup)

        return TYPING_OPTION

    @run_async
    def handle_done(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        options = []
        for i, opt in enumerate(user_data['options']):
            options.append({
                'text': opt,
                'index': i
            })

        poll = {
            'poll_id': str(uuid4()).replace("-", ""),
            'title': user_data['title'],
            'type': user_data['type'],
            'options': options,
            'meta': user_data.get('meta'),
            'bot_id': bot.id
        }
        # filename = "{}{}.csv".format(poll['title'], random.random())
        # with open(filename, 'w+') as csvfile:
        #     filewriter = csv.writer(csvfile, delimiter=',',
        #                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
        #     filewriter.writerow(['Option', 'Votes', 'Details'])
        #     with open(filename, 'wb+') as csvfile1:
        #         dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        #         dbx.files_upload(csvfile1.read(), "/" + filename)
        # poll['results_link'] = sharing.CreateSharedLinkArg(path=filename, short_url=True).short_url
        table = polls_table

        table.insert(self.serialize(poll))

        bot.send_message(update.callback_query.message.chat.id,
                         self.assemble_message_text(poll),
                                  reply_markup=self.assemble_inline_keyboard(poll, True),
                                  parse_mode='Markdown'
                                  )

        user_data.clear()
        bot.send_message(update.callback_query.message.chat.id,
                         "Thank you! you can send this poll to your users "
                         "by clicking 'Send' \n",
                         reply_markup=self.send_markup
                                  )
        return ConversationHandler.END

    def get_affirmation(self):
        return random.choice(AFFIRMATIONS)

    def assemble_reply_keyboard(self):
        keyboard = []
        for _, val in POLL_HANDLERS.items():
            keyboard.append([val.name])

        return ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True
        )

    def assemble_type_regex(self):
        orclause = '|'.join([handler.name for handler in POLL_HANDLERS.values()])
        regex = '^({})$'.format(orclause)
        return regex

    def assemble_inline_keyboard(self, poll, include_publish_button=False):
        inline_keyboard_items = self.get_inline_keyboard_items(poll)

        return InlineKeyboardMarkup(inline_keyboard_items)

    def get_inline_keyboard_items(self, poll):
        handler = POLL_HANDLERS[poll['type']]
        button_items = handler.options(poll)
        buttons = []
        for row in button_items:
            current_row = []
            for item in row:
                item['callback_data']['id'] = poll['poll_id']
                current_row.append(InlineKeyboardButton(item['text'],
                                                        callback_data=json.dumps(item['callback_data'],
                                                                                 separators=(',', ':'))))
            buttons.append(current_row)
        return buttons

    def assemble_message_text(self, poll):
        handler = POLL_HANDLERS[poll['type']]
        message = '{}\n{}'.format(handler.title(poll),
                                  handler.evaluation(poll))
        return message

    def serialize(self, poll):
        ser = dict(poll)
        ser['options'] = json.dumps(poll['options'])
        if 'votes' in ser:
            ser['votes'] = json.dumps(poll['votes'])
        if 'meta' in ser:
            ser['meta'] = json.dumps(poll['meta'])
        return ser

    def deserialize(self, serialized):
        poll = dict(serialized)
        poll['options'] = json.loads(serialized['options'])
        if 'votes' in poll:
            poll['votes'] = serialized['votes']
        if 'meta' in poll:
            meta = serialized['meta']
            poll['meta'] = "" if meta is None else json.loads(meta)
        return poll

    # Inline query handler
    def inline_query(self, bot, update):
        query = update.inline_query.query

        result = list(polls_table.find(dict(poll_id=query, bot_id=bot.id)))

        if not result:
            update.inline_query.answer(results=[],
                                       switch_pm_text="Create a new poll",
                                       switch_pm_parameter="start")
            return

        inline_results = []
        for res in result:
            poll = self.deserialize(res)
            inline_results.append(
                InlineQueryResultArticle(
                    id=poll['poll_id'],
                    title=poll['title'],
                    input_message_content=InputTextMessageContent(
                        message_text=self.assemble_message_text(poll),
                        parse_mode='Markdown'
                    ),
                    reply_markup=self.assemble_inline_keyboard(poll)
                )
            )
        update.inline_query.answer(inline_results)
        return

    # Inline button press handler
    def button(self, bot, update):
        chat_id = update.effective_chat.id

        query = update.callback_query
        data_dict = json.loads(update.callback_query.data)
        table = poll_instances_table
        templates = polls_table
        result = {}
        kwargs = {}
        if query.inline_message_id:
            kwargs['inline_message_id'] = query.inline_message_id
            try:
                result = table.find_one(dict(inline_message_id=query.inline_message_id))
            except TypeError:
                result = None
            if not result:
                result = templates.find_one(dict(poll_id=data_dict['id']))
                try:
                    result = dict(result)
                except TypeError:
                    result = {}
                try:
                    result['inline_message_id'] = query.inline_message_id
                    result['votes'] = {}
                except KeyError:
                    result['message_id'] = query.message_id
                    result['votes'] = {}

        elif query.message:
            if query.message:
                if query.message.from_user.bot == bot:
                    include_publish_button = True

                kwargs['message_id'] = query.message.message_id
                kwargs['chat_id'] = query.message.chat.id
                try:
                    result = table.find_one(dict(message_id=query.message.message_id,
                                                 chat_id=query.message.chat.id))
                except TypeError:
                    result = None
                if not result:
                    result = templates.find_one(dict(poll_id=data_dict['id'], bot_id=bot.id))
                    result = dict(result)
                    if "id" in result:
                        result.pop('id')
                    if "_id" in result:
                        result.pop('_id')
                    result['message_id'] = query.message.message_id
                    result['chat_id'] = query.message.chat.id
                    result['votes'] = '{}'
        poll = self.deserialize(result)
        try:
            poll['votes'] = ast.literal_eval(poll['votes'])
        except ValueError:
            poll['votes'] = {}
        uid_str = str(query.from_user.id)
        name = str(query.from_user.first_name)
        handler = POLL_HANDLERS[poll['type']]
        handler.handle_vote(poll['votes'], uid_str, name, data_dict)
        query.answer(handler.get_confirmation_message(poll, uid_str))
        if "_id" in poll:
            poll.pop('_id')
        table.update({'poll_id': poll['poll_id'], "bot_id": bot.id},
                     self.serialize(poll),
                     upsert=True)
        old_instances = table.find({"poll_id": poll["poll_id"], "bot_id": bot.id})
        vote_instances = []
        for instance in old_instances:
            vote_instances.append(instance["votes"])
            print(instance["votes"])

        if len(vote_instances) > 0:  # TODO this makes no sense at all- we should have the posibility to add toghether the results of different instaces of the polls
            vote_instances[0] = ast.literal_eval(vote_instances[0])
            vote_instances[0].update(poll["votes"])
            poll["votes"] = vote_instances[0]

        poll["bot_id"] = bot.id
        votes_list = []
        for po in table.find({"bot_id": bot.id, "poll_id": poll["poll_id"]}):
            if po["chat_id"] != chat_id:
                votes_list.append(po["votes"])
        votes_dict = {}
        for d in votes_list:
            votes_dict.update(ast.literal_eval(d))
        if votes_dict:
            poll["votes"] = votes_dict

        bot.edit_message_text(text=self.assemble_message_text(poll),
                              parse_mode='Markdown',
                              reply_markup=self.assemble_inline_keyboard(poll),
                              **kwargs)
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(bot, update)

        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    # Error handler
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)
        return

    @run_async
    def handle_send_poll(self, bot, update):

        bot.send_message(update.callback_query.message.chat.id,
                         "This is the list of the current polls. ", reply_keyboard=self.reply_markup)

        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        command_list = [command['title'] for command in polls_list_of_dicts]
        reply_keyboard = [command_list]
        bot.send_message(update.callback_query.message.chat.id,
                         "Choose the poll that you want to send",
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        return TYPING_SEND_TITLE

    @run_async
    def handle_send_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        sent = []
        poll_name = txt
        user_data["poll_name_to_send"] = poll_name
        chats = chats_table.find({"bot_id": bot.id})
        for chat in chats:
            if chat['chat_id'] != chat_id:
                if not any(sent_d['id'] == chat['chat_id'] for sent_d in sent):
                    sent.append(chat['chat_id'])
                    poll = polls_table.find_one({'title': poll_name})
                    poll['options'] = ast.literal_eval(poll['options'])
                    poll['meta'] = ast.literal_eval(poll['meta'])

                    bot.send_message(chat['chat_id'], self.assemble_message_text(poll),
                                     reply_markup=self.assemble_inline_keyboard(poll, True),
                                     parse_mode='Markdown'
                                     )
        if len(sent) == 0:
            bot.send_message(chat_id, "Looks like there are yet no users to send this poll to. "
                                      "No polls sent :( ", reply_markup=ReplyKeyboardRemove())
        else:
            bot.send_message(chat_id, "Your poll was sent to all you users! ", reply_markup=ReplyKeyboardRemove())

        get_help(bot, update)

        return ConversationHandler.END

    # @run_async
    # def handle_bots_polls(self, bot, update):
    #     chat_id, txt = initiate_chat_id(update)
    #     polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
    #     command_list = [command['title'] for command in polls_list_of_dicts]
    #     reply_keyboard = [command_list]
    #     update.message.reply_text(
    #         "Please choose the poll that you want to check",
    #         reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    #     return CHOOSE_TITLE_RESULTS
    #
    # @run_async
    # def handle_bots_polls_title(self, bot, update):
    #     print("TEST")
    #     chat_id, txt = initiate_chat_id(update)
    #     poll = polls_table.find_one({'title': txt})
    #
    #     poll_title = poll['title']
    #     poll_type = POLL_HANDLERS.get(poll['type']).name
    #     if "description" in poll:
    #         poll_description = poll['description']
    #     else:
    #         poll_description = POLL_HANDLERS.get(poll['type']).desc
    #     # poll_results_link = poll['results_link']
    #     poll_id = poll['poll_id']
    #     poll_instances = poll_instances_table.find({"poll_id": poll_id, "bot_id": bot.id})
    #     txt_to_send = ""
    #
    #     for poll_instance in poll_instances:
    #         votes = ast.literal_eval(poll_instance["votes"])
    #         for vote in votes:
    #             txt_to_send += str(votes[vote]["data"])
    #     poll_results = txt_to_send
    #
    #     if poll is not None:
    #         bot.send_message(chat_id,
    #                          "Poll title:{} \nPoll_type:{} \nResults:{} \nDescription:{}".
    #                          format(poll_title,
    #                                 poll_type,
    #                                 poll_results,
    #                                 poll_description
    #                                 ))
    #
    #     else:
    #         bot.send_message(chat_id, "No poll with such title exists")
    #     return ConversationHandler.END

    @run_async
    def handle_delete_poll(self, bot, update):
        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        if polls_list_of_dicts.count() != 0:

            command_list = [command['title'] for command in polls_list_of_dicts]
            reply_keyboard = [command_list]
            bot.send_message(update.callback_query.message.chat.id,
                             "Please choose the poll that you want to delete",
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
            bot.send_message(update.callback_query.message.chat.id,
                             "Click 'Back' to cancel", reply_keyboard=self.reply_markup)
            return CHOOSE_TITLE_DELETE
        else:
            bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
            admin_keyboard = [InlineKeyboardButton(text="Create", callback_data="create_poll"),
                              InlineKeyboardButton(text="Back", callback_data="help_back")]
            bot.send_message(update.callback_query.message.chat.id,
                             """You have no polls created yet. \n"""
                             """Click "Create" to configure your first poll or "Back" for main menu""",
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    @run_async
    def handle_delete_poll_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        poll_to_delete_instances = poll_instances_table.find_many({"bot_id": bot.id, "title": txt})

        for poll_instance in poll_to_delete_instances:
            bot.delete_message(chat_id=chat_id,
                               message_id=poll_instance["message_id"])

        polls_table.delete_one({"bot_id": bot.id, "title": txt})
        poll_instances_table.delete_many({"bot_id": bot.id, "title": txt})

        update.message.reply_text("Ok!", reply_markup=ReplyKeyboardRemove())

        update.message.reply_text(
            "Poll with title {} has been deleted from all chats.".format(txt))
        get_help(bot, update)
        return ConversationHandler.END


__mod_name__ = "Polls"

__admin_help__ = """
Here you can:
 - Create a new poll
 - Delete_poll
 - Send a poll to all users 

"""


DELETE_POLLS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=PollBot().handle_delete_poll,
                                       pattern=r"delete_poll")
                  ],
    states={

        CHOOSE_TITLE_DELETE: [MessageHandler(Filters.text, PollBot().handle_delete_poll_finish),
                              CommandHandler('cancel', PollBot().cancel)],

    },
    fallbacks=[CallbackQueryHandler(callback=PollBot().cancel, pattern=r"cancel_poll")]
)

# BOTS_POLLS_HANDLER = ConversationHandler(
#     entry_points=[CommandHandler('bots_polls', PollBot().handle_bots_polls),
#
#                   ],
#     states={
#
#         CHOOSE_TITLE_RESULTS: [MessageHandler(Filters.text, PollBot().handle_bots_polls_title),
#                        CommandHandler('cancel', PollBot().cancel)],
#
#     },
#     fallbacks=[CommandHandler('cancel', PollBot().cancel, pass_user_data=True)]
# )
POLL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=PollBot().start,
                                       pattern=r"create_poll"),
                  ],
    states={
        NOT_ENGAGED: [CommandHandler('poll', PollBot().start)],
        TYPING_TITLE: [MessageHandler(Filters.text,
                                      PollBot().handle_title,
                                      pass_user_data=True),
                       CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll"),
                       CommandHandler('cancel', PollBot().cancel),
                       ],
        TYPING_TYPE: [RegexHandler(PollBot().assemble_type_regex(),
                                   PollBot().handle_type,
                                   pass_user_data=True),
                      CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll"),
                      CommandHandler('cancel', PollBot().cancel),
                      ],
        TYPING_META: [MessageHandler(Filters.text,
                                     PollBot().handle_meta,
                                     pass_user_data=True),
                      CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll"),
                      CommandHandler('cancel', PollBot().cancel),
                      ],
        TYPING_OPTION: [MessageHandler(Filters.text,
                                       PollBot().handle_option,
                                       pass_user_data=True),
                        CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll"),
                        CommandHandler('cancel', PollBot().cancel),
                        ]
    },
    fallbacks=[
        CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll"),
        CallbackQueryHandler(callback=PollBot().handle_done, pattern=r"done_poll", pass_user_data=True),
        CommandHandler('cancel', PollBot().cancel),
        MessageHandler(filters=Filters.command, callback=PollBot().back),
    ]
)
BUTTON_HANDLER = CallbackQueryHandler(PollBot().button, pattern='{"i":')

NOT_ENGAGED_SEND, TYPING_SEND_TITLE = range(2)

SEND_POLLS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=PollBot().handle_send_poll,
                                       pattern=r"send_poll"),
                  CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll")
                  ],
    states={
        NOT_ENGAGED_SEND: [CommandHandler('send_poll', PollBot().handle_send_poll),
                           CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll"),
                           CommandHandler('cancel', PollBot().cancel), ],
        TYPING_SEND_TITLE: [MessageHandler(Filters.text, PollBot().handle_send_title, pass_user_data=True),
                            CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll"),
                            CommandHandler('cancel', PollBot().cancel), ],

    },
    fallbacks=[
        CallbackQueryHandler(callback=PollBot().back, pattern=r"cancel_poll"),
        CommandHandler('cancel', PollBot().cancel),
        MessageHandler(filters=Filters.command, callback=PollBot().back),

    ]
)
