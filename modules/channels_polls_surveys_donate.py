import ast

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler, run_async
from database import channels_table, polls_table, surveys_table
from telegram.error import TelegramError

# from modules.channels import Channels
from modules.new_channels import Channels
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict

# from modules.helper_funcs.auth import initiate_chat_id
# from modules.polls import PollBot

import logging

from modules.polls import PollBot
MY_CHANNELS, MANAGE_CHANNEL, ADD_CHANNEL, \
CHOOSE_TO_REMOVE, REMOVE_CHANNEL, \
CHOOSE_TO_SEND_POST, POST_TO_CHANNEL, MESSAGE_TO_USERS = range(8)

CHOOSE_TO_SEND_POLL, CHOOSE_POLL_TO_SEND = range(2)
CHOOSE_CHANNEL_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(2)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Post on channel -> Send a Poll -> no polls. wanna create one?(yes, back) ->
#         -> creating poll -> poll was created(send on channel, back) -> are u sure to send? -> send to channel


# for sending polls to channels

# TODO: need to refactor
class SendPoll(object):
    def choose_channel(self, bot, update, user_data):
        create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["create_button"], callback_data="create_poll"),
                           InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]]
        create_markup = InlineKeyboardMarkup(
            create_buttons)

        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        if polls_list_of_dicts.count() == 0:
            bot.send_message(update.callback_query.message.chat.id,
                             string_dict(bot)["polls_str_8"],
                             reply_markup=create_markup)
            return ConversationHandler.END
        else:
            return Channels().make_channels_layout(bot, update, CHOOSE_TO_SEND_POLL,
                                                   string_dict(bot)["choose_channel_to_send_poll"],
                                                   user_data)

    def handle_send_poll(self, bot, update, user_data):
        create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["create_button"], callback_data="create_poll"),
                           InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]]
        create_markup = InlineKeyboardMarkup(
            create_buttons)
        back_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                        callback_data="cancel_send_poll")]])

        channel = channels_table.find_one({'bot_id': bot.id, 'channel_username': update.message.text})
        if channel:
            bot.delete_message(update.message.chat_id, update.message.message_id)
            user_data['channel'] = update.message.text
            polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
            if polls_list_of_dicts.count() != 0:
                command_list = [command['title'] for command in polls_list_of_dicts]
                bot.send_message(update.message.chat.id,
                                 string_dict(bot)["polls_str_9"], reply_markup=back_keyboard)
                reply_keyboard = [command_list]
                bot.send_message(update.message.chat.id,
                                 string_dict(bot)["polls_str_10"],
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
                return CHOOSE_POLL_TO_SEND
            else:
                bot.send_message(update.message.chat.id,
                                 string_dict(bot)["polls_str_8"],
                                 reply_markup=create_markup)
                return ConversationHandler.END
        # else:
        #     return Channels().make_channels_layout(bot, update, CHOOSE_TO_SEND_POST,
        #                                            string_dict(bot)["choose_channel_to_send_poll"], user_data)

    def handle_send_title(self, bot, update, user_data):  # TODO save more poll instances
        chat_id, txt = initiate_chat_id(update)
        # sent = []
        poll_name = txt
        user_data["poll_name_to_send"] = poll_name
        # chats = chats_table.find({"bot_id": bot.id})
        # for chat in chats:
        #     if chat['chat_id'] != chat_id:
        #         if not any(sent_d['id'] == chat['chat_id'] for sent_d in sent):
        #             sent.append(chat['chat_id'])
        poll = polls_table.find_one({'title': poll_name})
        poll['options'] = ast.literal_eval(poll['options'])
        poll['meta'] = ast.literal_eval(poll['meta'])

        bot.send_message(user_data['channel'], PollBot().assemble_message_text(poll),
                         reply_markup=PollBot().assemble_inline_keyboard(poll, True),
                         parse_mode='Markdown'
                         )

        bot.send_message(chat_id, string_dict(bot)["polls_str_12"], reply_markup=ReplyKeyboardRemove())

        get_help(bot, update)

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


# for sending surveys to channels

class SendSurvey(object):

    def choose_channel(self, bot, update, user_data):
        return Channels().make_channels_layout(bot, update, CHOOSE_CHANNEL_TO_SEND_SURVEY,
                                               string_dict(bot)["choose_channel_to_send_survey"],
                                               user_data)

    def handle_send_survey(self, bot, update, user_data):
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="cancel_survey")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        channel = channels_table.find_one({'bot_id': bot.id, 'channel_username': update.message.text})
        if channel:
            bot.delete_message(update.message.chat_id, update.message.message_id)
            user_data['channel'] = update.message.text
            surveys_list = surveys_table.find({"bot_id": bot.id})
            if surveys_list.count() != 0:
                bot.send_message(update.message.chat.id,
                                 string_dict(bot)["survey_str_18"], reply_markup=reply_markup)
                command_list = [survey['title'] for survey in surveys_list]
                reply_keyboard = [command_list]
                bot.send_message(update.message.chat.id,
                                 string_dict(bot)["survey_str_19"],
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
                return CHOOSE_SURVEY_TO_SEND
            else:
                admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["create_button"],
                                                       callback_data="create_survey"),
                                  InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                       callback_data="help_back")]
                bot.send_message(update.message.chat.id,
                                 string_dict(bot)["survey_str_23"],
                                 reply_markup=InlineKeyboardMarkup([admin_keyboard]))
                return ConversationHandler.END
        else:
            return Channels().make_channels_layout(bot, update, CHOOSE_CHANNEL_TO_SEND_SURVEY,
                                                   string_dict(bot)["choose_channel_to_send_survey"],
                                                   user_data)

    def handle_send_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["title"] = txt
        survey = surveys_table.find_one({"bot_id": bot.id, 'title': txt})

        sent = []
        # chats = chats_table.find({"bot_id": bot.id})
        # for chat in chats:
        #     # if chat['chat_id'] != chat_id:
        #     if not any(sent_d == chat['chat_id'] for sent_d in sent):
        #         sent.append(chat['chat_id'])
        bot.send_message(chat_id=user_data['channel'], text=string_dict(bot)["survey_str_20"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["start_button"],
                                                    url="https://t.me/{}?start=survey_{}".format(bot.username,
                                                                                                 user_data["title"]),
                                                    callback_data="survey_{}".format(
                                                        str(txt)
                                                    ))]]
                         ))

        # if len(sent) == 0:
        #     bot.send_message(chat_id, survey_str_21, reply_markup=ReplyKeyboardRemove())
        # else:
        #     bot.send_message(chat_id=chat_id, text=survey_str_22, reply_markup=ReplyKeyboardRemove())
        get_help(bot, update)
        logger.info("Admin {} on bot {}:{} sent a survey to the users:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, txt))
        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(bot, update)
        return ConversationHandler.END

    def back(self, bot, update):
        bot.delete_message(update.effective_chat.id,
                           update.effective_message.message_id)
        get_help(bot, update)
        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)


# There are already 'send_poll' pattern handler - mb use it
SEND_POLL_TO_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendPoll().choose_channel, pattern=r"post_poll_to_channel", pass_user_data=True),],
    states={
        CHOOSE_TO_SEND_POLL: [RegexHandler(r"@", SendPoll().handle_send_poll, pass_user_data=True),
                              RegexHandler('^Back$', SendPoll().back, pass_user_data=True)],

        CHOOSE_POLL_TO_SEND: [MessageHandler(Filters.text, SendPoll().handle_send_title, pass_user_data=True),
                              CallbackQueryHandler(callback=SendPoll().back, pattern=r"cancel_send_poll")],
    },
    fallbacks=[]
)

SEND_SURVEY_TO_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendSurvey().choose_channel,
                                       pattern="post_survey_to_channel", pass_user_data=True)],
    states={
        CHOOSE_CHANNEL_TO_SEND_SURVEY: [RegexHandler(r"@", SendSurvey().handle_send_survey, pass_user_data=True),
                                        RegexHandler('^Back$', SendSurvey().back, pass_user_data=True)],

        CHOOSE_SURVEY_TO_SEND: [MessageHandler(Filters.text, SendSurvey().handle_send_title, pass_user_data=True),
                                CallbackQueryHandler(callback=SendSurvey().back, pattern=r"cancel_survey")]
    },
    fallbacks=[]
)
