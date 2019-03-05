#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import json
import csv
import random
import logging
from uuid import uuid4
from dropbox import dropbox, sharing

from telegram import InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, Filters, RegexHandler, \
    CallbackQueryHandler, run_async
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.inline.inlinequeryresultarticle import InlineQueryResultArticle
from telegram.inline.inputtextmessagecontent import InputTextMessageContent

from database import polls_table, poll_instances_table, DROPBOX_TOKEN
from modules.create_survey import chats_table
from modules.helper_funcs.auth import initiate_chat_id

from .pollbot.basic_poll_handler import BasicPoll
from .pollbot.tie_break_instant_runoff_poll_handler import TieBreakInstantRunoffPollHandler
from .pollbot.stv_poll_handler import StvHandler
from .pollbot.instant_runoff_poll_handler import InstantRunoffPollHandler
from .pollbot.custom_description_poll_handler import CustomDescriptionHandler
from .pollbot.custom_description_instant_runoff_poll_handler import CustomDescriptionInstantRunoffPollHandler
from .pollbot.set_poll_handler import SetPollHandler
from .pollbot.multiple_options_poll_handler import MultipleOptionsHandler

POLL_TYPE_BASIC, \
POLL_TYPE_SET, \
POLL_TYPE_INSTANT_RUNOFF, \
POLL_TYPE_INSTANT_RUNOFF_TIE_BREAK, \
POLL_TYPE_CUSTOM_DESCRIPTION, \
POLL_TYPE_STV, \
POLL_TYPE_INSTANT_RUNOFF_CUSTOM_DESCRIPTION, \
POLL_TYPE_MULTIPLE_OPTIONS = range(8)

POLL_HANDLERS = {
    POLL_TYPE_BASIC: BasicPoll(),
    POLL_TYPE_SET: SetPollHandler(),
    POLL_TYPE_INSTANT_RUNOFF: InstantRunoffPollHandler(),
    POLL_TYPE_INSTANT_RUNOFF_TIE_BREAK: TieBreakInstantRunoffPollHandler(),
    POLL_TYPE_CUSTOM_DESCRIPTION: CustomDescriptionHandler(),
    POLL_TYPE_STV: StvHandler(),
    POLL_TYPE_INSTANT_RUNOFF_CUSTOM_DESCRIPTION: CustomDescriptionInstantRunoffPollHandler(),
    POLL_TYPE_MULTIPLE_OPTIONS: MultipleOptionsHandler(),
}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Conversation states:
NOT_ENGAGED, TYPING_TITLE, TYPING_TYPE, TYPING_OPTION, TYPING_META = range(5)
CHOOSE_TITLE, CHOOSE_OPTION = range(2)
CHOOSE_TITLE_DELETE = 21
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


class PollBot(object):

    # Conversation handlers:
    @run_async
    def start(self, bot, update):
        """Send a message when the command /start is issued."""
        update.message.reply_text('Hi! Please send me the title of your poll. (/cancel to exit)')

        return TYPING_TITLE

    @run_async
    def handle_title(self, bot, update, user_data):
        text = update.message.text
        user_data['title'] = text
        update.message.reply_text("{}! What kind of poll is it going to be? (/cancel to shut me up)"
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
            update.message.reply_text(POLL_HANDLERS[polltype].ask_for_extra_config(user_data.get('meta')))
            return TYPING_META
        else:
            update.message.reply_text("{}. Now, send me the first answer option. (or /cancel)".format(
                self.get_affirmation()
            ))
            return TYPING_OPTION

    @run_async
    def handle_meta(self, bot, update, user_data):
        text = update.message.text
        polltype = user_data['type']
        POLL_HANDLERS[polltype].register_extra_config(text, user_data.get('meta'))

        if POLL_HANDLERS[polltype].requires_extra_config(user_data.get('meta')):
            update.message.reply_text(POLL_HANDLERS[polltype].ask_for_extra_config(user_data.get('meta')))
            return TYPING_META
        else:
            update.message.reply_text("{}, that's it! Next, please send me the first answer option."
                                      .format(self.get_affirmation()))
            return TYPING_OPTION

    def handle_option(self, bot, update, user_data):
        text = update.message.text
        handler = POLL_HANDLERS[user_data['type']]
        user_data['options'].append(text)

        if len(user_data['options']) >= handler.max_options:
            return self.handle_done(bot, update, user_data)

        update.message.reply_text("{}! Now, send me another answer option or type /done to publish."
                                  .format(self.get_affirmation()),
                                  reply_markup=ReplyKeyboardRemove())

        if len(user_data['options']) >= handler.max_options - 1:
            update.message.reply_text("Uh oh, you're running out of options. You can only have one more option.")

        return TYPING_OPTION

    @run_async
    def handle_done(self, bot, update, user_data):
        update.message.reply_text("Thank you! you can send this poll to other groups "
                                  "or chats by writing /send_poll \n"
                                  "You can use the tag #all to send to every authorized user of this bot"
                                  )
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
        filename = "{}{}.csv".format(poll['title'], random.random())
        with open(filename, 'w+') as csvfile:
            filewriter = csv.writer(csvfile, delimiter=',',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)
            filewriter.writerow(['Option', 'Votes', 'Details'])
            with open(filename, 'wb+') as csvfile1:
                dbx = dropbox.Dropbox(DROPBOX_TOKEN)
                dbx.files_upload(csvfile1.read(), "/" + filename)
            poll['results_link'] = sharing.CreateSharedLinkArg(path=filename, short_url=True).short_url
        table = polls_table

        table.insert(self.serialize(poll))

        update.message.reply_text(self.assemble_message_text(poll),
                                  reply_markup=self.assemble_inline_keyboard(poll, True),
                                  parse_mode='Markdown'
                                  )

        user_data.clear()

        return NOT_ENGAGED

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
        # if include_publish_button:
        #     publish_button = InlineKeyboardButton("Publish!",
        #                                           switch_inline_query=poll['poll_id'])
        #     inline_keyboard_items.append([publish_button])

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
        query = update.callback_query
        print(update.callback_query.data)
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

        old_instances = table.find({"poll_id": poll["poll_id"], "bot_id": bot.id})
        vote_instances = []
        for instance in old_instances:
            vote_instances.append(instance["votes"])
        if len(vote_instances) > 0:
            vote_instances[0] = ast.literal_eval(vote_instances[0])
            vote_instances[0].update(poll["votes"])
            poll["votes"] = vote_instances[0]
        poll["bot_id"] = bot.id
        table.update({'poll_id': poll['poll_id'], "bot_id": bot.id},
                     self.serialize(poll),
                     upsert=True)
        # TODO edit to actual result from db, the sum of votes
        bot.edit_message_text(text=self.assemble_message_text(poll),
                              parse_mode='Markdown',
                              reply_markup=self.assemble_inline_keyboard(poll),
                              **kwargs)
        return

    @run_async
    def cancel(self, bot, update):
        update.message.reply_text("Oh, too bad. Maybe next time!",
                                  reply_markup=ReplyKeyboardRemove())
        return NOT_ENGAGED

    # Error handler
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)
        return

    @run_async
    def handle_send_poll(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        bot.send_message(chat_id, "This is the list of the current polls. "
                                  "Choose the pool that you want to send or click /cancel")

        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        command_list = [command['title'] for command in polls_list_of_dicts]
        reply_keyboard = [command_list]
        update.message.reply_text(
            "Please choose the poll that you want to send",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return TYPING_SEND_TITLE

    @run_async
    def handle_send_title(self, bot, update, user_data):
        tags_names = []
        for chat in chats_table.find({"bot_id": bot.id}):
            if chat["tag"] in tags_names:
                pass
            else:
                tags_names.append(chat["tag"])
        response = "This is the list of tags assinged in your chatbot.\n To remove one of these tags, click /rmtag"
        for tag in sorted(tags_names):
            response = response + "\n<b>" + tag + "</b>"

        chat_id, txt = initiate_chat_id(update)
        # if txt:
        poll_name = txt
        user_data["poll_name_to_send"] = poll_name
        bot.send_message(chat_id, "Please send me the tags that you want to send to. "
                                  "Try to send them in one message. For example:\n"
                                  "#tag1 #tag2 #tag3 ... \n"
                                  "If you want you want to send it to all users, click the button below",
                         reply_markup=ReplyKeyboardMarkup([["All users"]], one_time_keyboard=True)
                         )

        return TYPING_TAGS

    @run_async
    def handle_send_tags(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if txt == "All users":
            txt = "#user"
        txt_split = txt.split(" ")
        while "" in txt_split:
            txt_split.remove("")
        poll_name = user_data["poll_name_to_send"]
        i = 0
        send_tags = []
        for i in range(len(txt_split)):
            if txt_split[i][0] == "#":
                send_tags.append(txt_split[i].lower())
                i += 1
        # if i == len(txt_split):
        approved = []
        rejected = []
        sent = []
        print(send_tags)

        for tag_to_send in send_tags:
            tags = chats_table.find({"tag": tag_to_send})
            for tag in tags:
                if tag['chat_id'] != chat_id:
                    if not any(sent_d['id'] == tag['chat_id'] for sent_d in sent):
                        sent.append(tag['chat_id'])
                        approved.append(tag['name'])

                        poll = polls_table.find_one({'title': poll_name})
                        poll['options'] = ast.literal_eval(poll['options'])
                        poll['meta'] = ast.literal_eval(poll['meta'])

                        bot.send_message(tag['chat_id'], self.assemble_message_text(poll),
                                         reply_markup=self.assemble_inline_keyboard(poll, True),
                                         parse_mode='Markdown'
                                         )
                        bot.send_message(chat_id, "Poll sent! ")

        if len(sent) == 0:
            bot.send_message(chat_id, "Looks like there are yet no users to send this poll to.")

        return NOT_ENGAGED

    @run_async
    def handle_bots_polls(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        command_list = [command['title'] for command in polls_list_of_dicts]
        reply_keyboard = [command_list]
        update.message.reply_text(
            "Please choose the poll that you want to check",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CHOOSE_TITLE

    @run_async
    def handle_bots_polls_title(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        poll = polls_table.find_one(title=txt)

        poll_title = poll['title']
        poll_type = POLL_HANDLERS.get(poll['type']).name
        if "description" in poll:
            poll_description = poll['description']
        else:
            poll_description = POLL_HANDLERS.get(poll['type']).desc
        poll_results_link = poll['results_link']
        poll_id = poll['poll_id']
        poll_instances = poll_instances_table.find({"poll_id": poll_id, "bot_id": bot.id})
        txt_to_send = ""

        for poll_instance in poll_instances:
            votes = ast.literal_eval(poll_instance["votes"])
            for vote in votes:
                txt_to_send += str(votes[vote]["data"])
        poll_results = txt_to_send

        if poll is not None:
            bot.send_message(chat_id,
                             "Poll title:{} \nPoll_type:{} \nResults:{} \nDescription:{} \nLink to the results:{}".
                             format(poll_title,
                                    poll_type,
                                    poll_results,
                                    poll_description,
                                    poll_results_link
                                    ))

        else:
            bot.send_message(chat_id, "No poll with such title exists")
        return ConversationHandler.END

    @run_async
    def handle_delete_poll(self, bot, update):
        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        command_list = [command['title'] for command in polls_list_of_dicts]
        reply_keyboard = [command_list]
        update.message.reply_text(
            "Please choose the poll that you want to check",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CHOOSE_TITLE_DELETE

    @run_async
    def handle_delete_poll_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        polls_table.delete_one({"bot_id": bot.id, "title": txt})
        poll_instances_table.delete_one({"bot_id": bot.id, "title": txt})
        update.message.reply_text(
            "Poll with title {} has been deleted".format(txt))


__mod_name__ = "Polls"

__admin_help__ = """

Admin only:*
 - /create_poll - to create a new poll
 - /delete_poll
 - /bots_polls - to see all created polls created by you
 - /send_poll -  to send a poll to all users that added a specific hashtag/hashtags
 - /cancel -  to cancel the creation of the poll

"""
__admin_keyboard__ = [["/create_poll", "/delete_poll"],
                      ["/bots_polls", "/send_poll"],
                      ["/cancel"]]

DELETE_POLLS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('delete_poll', PollBot().handle_delete_poll),

                  ],
    states={

        CHOOSE_TITLE_DELETE: [MessageHandler(Filters.text, PollBot().handle_delete_poll_finish, pass_user_data=True),
                              CommandHandler('cancel', PollBot().cancel)],

    },
    fallbacks=[CommandHandler('cancel', PollBot().cancel, pass_user_data=True)]
)

BOTS_POLLS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('bots_polls', PollBot().handle_bots_polls),

                  ],
    states={

        CHOOSE_TITLE: [MessageHandler(Filters.text, PollBot().handle_send_title, pass_user_data=True),
                       CommandHandler('cancel', PollBot().cancel)],

    },
    fallbacks=[CommandHandler('cancel', PollBot().cancel, pass_user_data=True)]
)
POLL_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('create_poll', PollBot().start),
                  ],
    states={
        NOT_ENGAGED: [CommandHandler('poll', PollBot().start)],
        TYPING_TITLE: [MessageHandler(Filters.text,
                                      PollBot().handle_title,
                                      pass_user_data=True),
                       CommandHandler('cancel', PollBot().cancel),
                       ],
        TYPING_TYPE: [RegexHandler(PollBot().assemble_type_regex(),
                                   PollBot().handle_type,
                                   pass_user_data=True),
                      CommandHandler('cancel', PollBot().cancel),
                      ],
        TYPING_META: [MessageHandler(Filters.text,
                                     PollBot().handle_meta,
                                     pass_user_data=True),
                      CommandHandler('cancel', PollBot().cancel),
                      ],
        TYPING_OPTION: [MessageHandler(Filters.text,
                                       PollBot().handle_option,
                                       pass_user_data=True),
                        CommandHandler('cancel', PollBot().cancel),
                        ]
    },
    fallbacks=[CommandHandler('done', PollBot().handle_done, pass_user_data=True)]
)
BUTTON_HANDLER = CallbackQueryHandler(PollBot().button)

NOT_ENGAGED_SEND, TYPING_SEND_TITLE, TYPING_TAGS = range(3)

SEND_POLLS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('send_poll', PollBot().handle_send_poll),

                  ],
    states={
        NOT_ENGAGED_SEND: [CommandHandler('send_poll', PollBot().handle_send_poll),
                           CommandHandler('cancel', PollBot().cancel), ],
        TYPING_SEND_TITLE: [MessageHandler(Filters.text, PollBot().handle_send_title, pass_user_data=True),
                            CommandHandler('cancel', PollBot().cancel), ],
        TYPING_TAGS: [MessageHandler(Filters.text, PollBot().handle_send_tags, pass_user_data=True),
                      CommandHandler('cancel', PollBot().cancel)],

    },
    fallbacks=[CommandHandler('cancel', PollBot().cancel, pass_user_data=True)]
)
