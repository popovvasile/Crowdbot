import ast

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler
from database import polls_table, surveys_table, chatbots_table, groups_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict
import logging

from modules.polls import PollBot

MY_GROUPS, MANAGE_GROUP, ADD_GROUP, \
CHOOSE_TO_REMOVE, REMOVE_GROUP, \
CHOOSE_TO_SEND_POST, POST_TO_GROUP, MESSAGE_TO_USERS = range(8)

CHOOSE_GROUP_TO_SEND_POLL, CHOOSE_POLL_TO_SEND = range(2)
CHOOSE_GROUP_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(2)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Post on group -> Send a Poll -> no polls. wanna create one?(yes, back) ->
#         -> creating poll -> poll was created(send on group, back) -> are u sure to send? -> send to group


# for sending polls to groups

class SendPoll(object):   # TODO send poll by group id, not name
    def handle_send_poll(self, bot, update, user_data):

        if update.callback_query:
            group_name = update.callback_query.data.replace("send_poll_to_group_", "")
            update_data = update.callback_query
            if group_name == "send_poll_to_group":
                groups_markup = [group['group_name'] for group in groups_table.find({'bot_id': bot.id})]
                bot.send_message(update.callback_query.message.chat.id, "Choose a group that you want to send",
                                 reply_markup=ReplyKeyboardMarkup([groups_markup]))
                bot.delete_message(chat_id=update_data.message.chat_id,
                                   message_id=update_data.message.message_id)
                return CHOOSE_GROUP_TO_SEND_POLL
        else:
            group_name = update.message.text
            update_data = update

        create_buttons = [
            [InlineKeyboardButton(text=string_dict(bot)["create_button_str"], callback_data="create_poll"),
             InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]]
        create_markup = InlineKeyboardMarkup(
            create_buttons)
        back_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                        callback_data="help_back")]])

        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        if polls_list_of_dicts.count() == 0:
            bot.send_message(update_data.message.chat.id,
                             string_dict(bot)["polls_str_8"],
                             reply_markup=create_markup)
            return ConversationHandler.END
        else:
            user_data['group'] = group_name
            polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
            if polls_list_of_dicts.count() != 0:
                command_list = [command['title'] for command in polls_list_of_dicts]
                bot.send_message(update_data.message.chat.id,
                                 string_dict(bot)["polls_str_9"], reply_markup=back_keyboard)
                reply_keyboard = [command_list]
                bot.send_message(update_data.message.chat.id,
                                 string_dict(bot)["polls_str_10"],
                                 reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
                return CHOOSE_POLL_TO_SEND
            else:
                bot.send_message(update_data.message.chat.id,
                                 string_dict(bot)["polls_str_8"],
                                 reply_markup=create_markup)
                return ConversationHandler.END

    def handle_send_title(self, bot, update, user_data):  # TODO save more poll instances
        chat_id, txt = initiate_chat_id(update)
        poll_name = txt
        user_data["poll_name_to_send"] = poll_name
        poll = polls_table.find_one({'title': poll_name})
        poll['options'] = ast.literal_eval(poll['options'])
        poll['meta'] = ast.literal_eval(poll['meta'])

        bot.send_message(user_data['group'], PollBot().assemble_message_text(poll),
                         reply_markup=PollBot().assemble_inline_keyboard(poll, True),
                         parse_mode='Markdown'
                         )

        bot.send_message(chat_id, string_dict(bot)["polls_str_12"], reply_markup=ReplyKeyboardRemove())

        create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(groups)")]]
        create_markup = InlineKeyboardMarkup(create_buttons)
        bot.send_message(update.message.chat.id, string_dict(bot)["back_text"],
                         reply_markup=create_markup)
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


# for sending surveys to groups

class SendSurvey(object):
    def handle_send_survey(self, bot, update, user_data):  # TODO for callback_query and text messages
        if update.callback_query:
            group_name = update.callback_query.data.replace("send_survey_to_group_", "")
            update_data = update.callback_query
            if group_name == "send_survey_to_group":
                groups_markup = [group['group_name'] for group in groups_table.find({'bot_id': bot.id})]
                bot.send_message(update.callback_query.message.chat.id, "Choose a group that you want to send",
                                 reply_markup=ReplyKeyboardMarkup([groups_markup]))
                return CHOOSE_GROUP_TO_SEND_SURVEY
        else:
            group_name = update.message.text
            update_data = update
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.delete_message(update_data.message.chat.id, update_data.message.message_id)
        user_data['group'] = group_name
        surveys_list = surveys_table.find({"bot_id": bot.id})
        if surveys_list.count() != 0:
            bot.send_message(update_data.message.chat.id,
                             string_dict(bot)["survey_str_18"], reply_markup=reply_markup)
            command_list = [survey['title'] for survey in surveys_list]
            reply_keyboard = [command_list]
            bot.send_message(update_data.message.chat.id,
                             string_dict(bot)["survey_str_19"],
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return CHOOSE_SURVEY_TO_SEND
        else:
            admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["create_button_str"],
                                                   callback_data="create_survey"),
                              InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                   callback_data="help_back")]
            bot.send_message(update_data.message.chat.id,
                             string_dict(bot)["survey_str_23"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def handle_send_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["title"] = txt
        bot.send_message(chat_id=user_data['group'], text=string_dict(bot)["survey_str_20"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["start_button"],
                                                    url="https://t.me/{}?start=survey_{}".format(bot.username,
                                                                                                 user_data["title"]),
                                                    callback_data="survey_{}".format(
                                                        str(txt)
                                                    ))]]
                         ))
        create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(groups)")]]
        create_markup = InlineKeyboardMarkup(create_buttons)
        bot.send_message(update.message.chat.id, string_dict(bot)["back_text"],
                         reply_markup=create_markup)
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


DONATION_TO_USERS = 1
CHOOSE_GROUP_TO_SEND_DONATION = 23
CHOOSE_POLL_TO_SEND_DONATION = 34


class SendDonationToChannel(object):
    def send_donation(self, bot, update, user_data):
        groups = groups_table.find({'bot_id': bot.id})
        update_data = update.callback_query
        group_name = update.callback_query.data.replace("send_donation_to_group_", "")

        if groups != 0:
              # TODO here is a bug, AttributeError: 'Update' object has no attribute 'data'

            if group_name == "send_donation_to_group":
                groups_markup = [group['group_name'] for group in groups]
                bot.send_message(update_data.message.chat.id, "Choose a group that you want to send",
                                 reply_markup=ReplyKeyboardMarkup([groups_markup]))
                return CHOOSE_GROUP_TO_SEND_DONATION

            user_data["group_name"] = group_name
            buttons = list()
            buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                 callback_data="help_back")])
            reply_markup = InlineKeyboardMarkup(
                buttons)

            bot.delete_message(chat_id=update_data.message.chat_id,
                               message_id=update_data.message.message_id)
            chatbot = chatbots_table.find_one({"bot_id": bot.id})
            if chatbot.get("donate") != {} and "donate" in chatbot:
                bot.send_message(update_data.message.chat.id,
                                 string_dict(bot)["send_donation_request_1"],
                                 reply_markup=reply_markup)
                return DONATION_TO_USERS
            else:
                admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["allow_donations_button"],
                                                       callback_data="allow_donation"),
                                  InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                       callback_data="help_back")]
                bot.send_message(update_data.message.chat.id,
                                 string_dict(bot)["allow_donation_text"],
                                 reply_markup=InlineKeyboardMarkup([admin_keyboard]))
                return ConversationHandler.END
        else:
            admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["add_group"],
                                                   callback_data="add_group"),
                              InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                   callback_data="help_back")]
            bot.send_message(update_data.message.chat.id,
                             string_dict(bot)["no_groups"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def received_donation(self, bot, update, user_data):  # TODO change like in messages

        if update.message.text:
            bot.send_message(user_data["group_name"], update.message.text)

        elif update.message.photo:
            photo_file = update.message.photo[0].get_file().file_id
            bot.send_photo(user_data["group_name"], photo=photo_file)

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            bot.send_audio(user_data["group_name"], audio_file)

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            bot.send_voice(user_data["group_name"], voice_file)

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            bot.send_document(user_data["group_name"], document_file)

        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            bot.send_sticker(user_data["group_name"], sticker_file)

        elif update.message.game:
            sticker_file = update.message.game.get_file().file_id
            bot.send_game(user_data["group_name"], sticker_file)

        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            bot.send_animation(user_data["group_name"], animation_file)

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            bot.send_video(user_data["group_name"], video_file)

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            bot.send_video_note(user_data["group_name"], video_note_file)

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=string_dict(bot)["done_button"],
                                   callback_data="send_donation_finish")]]
        )
        bot.send_message(update.message.chat_id,
                         string_dict(bot)["send_donation_request_2"],
                         reply_markup=final_reply_markup)

        return DONATION_TO_USERS

    def send_donation_finish(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=string_dict(bot)["donate_button"],

                                             url="https://t.me/{}?start=pay_donation".format(bot.username),
                                             )])
        donation_reply_markup = InlineKeyboardMarkup(
            buttons)
        create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(groups)")]]
        create_markup = InlineKeyboardMarkup(create_buttons)

        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_donation_request_3"],
                         reply_markup=create_markup)

        bot.send_message(user_data["group_name"],
                         string_dict(bot)["donate_button"],
                         reply_markup=donation_reply_markup)
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


# There are already 'send_survey_to_users' pattern handler - mb use it
SEND_POLL_TO_GROUP_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(SendPoll().handle_send_poll, pattern=r"send_poll_to_group", pass_user_data=True), ],
    states={

        CHOOSE_POLL_TO_SEND: [MessageHandler(Filters.text, SendPoll().handle_send_title, pass_user_data=True), ],
        CHOOSE_GROUP_TO_SEND_POLL: [
            MessageHandler(Filters.text, SendPoll().handle_send_poll, pass_user_data=True), ],
    },
    fallbacks=[CallbackQueryHandler(callback=SendPoll().back, pattern=r"help_back"),
               CallbackQueryHandler(callback=SendPoll().back, pattern=r"help_module"),
               RegexHandler('^Back$', SendPoll().back),
               ]
)

SEND_SURVEY_TO_GROUP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendSurvey().handle_send_survey,
                                       pattern="send_survey_to_group", pass_user_data=True)],
    states={
        CHOOSE_GROUP_TO_SEND_SURVEY: [
            MessageHandler(Filters.text, SendSurvey().handle_send_survey, pass_user_data=True),
        ],
        CHOOSE_SURVEY_TO_SEND: [MessageHandler(Filters.text, SendSurvey().handle_send_title, pass_user_data=True),
                                ]
    },
    fallbacks=[CallbackQueryHandler(callback=SendSurvey().back, pattern=r"help_back"),
               CallbackQueryHandler(callback=SendSurvey().back, pattern=r"help_module"),
               RegexHandler('^Back$', SendSurvey().back),
               ]
)
SEND_DONATION_TO_GROUP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern=r"send_donation_to_group",
                                       callback=SendDonationToChannel().send_donation,
                                       pass_user_data=True)],

    states={
        DONATION_TO_USERS: [MessageHandler(Filters.all,
                                           SendDonationToChannel().received_donation,
                                           pass_user_data=True),
                            ],
        CHOOSE_GROUP_TO_SEND_DONATION: [MessageHandler(Filters.all,
                                                         SendDonationToChannel().send_donation,
                                                         pass_user_data=True),
                                          ],
    },

    fallbacks=[CallbackQueryHandler(callback=SendDonationToChannel().send_donation_finish,
                                    pattern=r"send_donation_finish", pass_user_data=True),
               CallbackQueryHandler(callback=SendDonationToChannel().back, pattern=r"help_back"),
               CallbackQueryHandler(callback=SendDonationToChannel().back, pattern=r"help_module"),

               ]
)
