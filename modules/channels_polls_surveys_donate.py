import ast

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters, RegexHandler
from database import polls_table, surveys_table, chatbots_table, channels_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.helper import get_help
from modules.helper_funcs.lang_strings.strings import string_dict
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

class SendPoll(object):
    def handle_send_poll(self, bot, update, user_data):

        if update.callback_query:
            channel_username = update.callback_query.data.replace("send_poll_to_channel_", "")
            update_data = update.callback_query
            if channel_username == "send_poll_to_channel":
                channels_markup = [channel['channel_username'] for channel in channels_table.find({'bot_id': bot.id})]
                bot.send_message(update.callback_query.message.chat.id, "Choose a channel that you want to send",
                                 reply_markup=ReplyKeyboardMarkup([channels_markup]))
                return CHOOSE_POLL_TO_SEND_DONATION
        else:
            channel_username = update.message.text
            update_data = update

        bot.delete_message(chat_id=update_data.message.chat_id,
                           message_id=update_data.message.message_id)
        create_buttons = [
            [InlineKeyboardButton(text=string_dict(bot)["create_button_str"], callback_data="create_poll"),
             InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="help_back")]]
        create_markup = InlineKeyboardMarkup(
            create_buttons)
        back_keyboard = \
            InlineKeyboardMarkup([[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                        callback_data="cancel_send_poll")]])

        polls_list_of_dicts = polls_table.find({"bot_id": bot.id})
        if polls_list_of_dicts.count() == 0:
            bot.send_message(update_data.message.chat.id,
                             string_dict(bot)["polls_str_8"],
                             reply_markup=create_markup)
            return ConversationHandler.END
        else:
            user_data['channel'] = channel_username
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

        bot.send_message(user_data['channel'], PollBot().assemble_message_text(poll),
                         reply_markup=PollBot().assemble_inline_keyboard(poll, True),
                         parse_mode='Markdown'
                         )

        bot.send_message(chat_id, string_dict(bot)["polls_str_12"], reply_markup=ReplyKeyboardRemove())

        create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(channels)")]]
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


# for sending surveys to channels

class SendSurvey(object):
    def handle_send_survey(self, bot, update, user_data):  # TODO for callback_query and text messages
        if update.callback_query:
            channel_username = update.callback_query.data.replace("send_survey_to_channel_", "")
            update_data = update.callback_query
            if channel_username == "send_survey_to_channel":
                channels_markup = [channel['channel_username'] for channel in channels_table.find({'bot_id': bot.id})]
                bot.send_message(update.callback_query.message.chat.id, "Choose a channel that you want to send",
                                 reply_markup=ReplyKeyboardMarkup([channels_markup]))
                return CHOOSE_CHANNEL_TO_SEND_SURVEY
        else:
            channel_username = update.message.text
            update_data = update
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"], callback_data="cancel_survey")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.delete_message(update_data.message.chat.id, update_data.message.message_id)
        user_data['channel'] = channel_username
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
        bot.send_message(chat_id=user_data['channel'], text=string_dict(bot)["survey_str_20"],
                         reply_markup=InlineKeyboardMarkup(
                             [[InlineKeyboardButton(text=string_dict(bot)["start_button"],
                                                    url="https://t.me/{}?start=survey_{}".format(bot.username,
                                                                                                 user_data["title"]),
                                                    callback_data="survey_{}".format(
                                                        str(txt)
                                                    ))]]
                         ))
        create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_module(channels)")]]
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
CHOOSE_CHANNEL_TO_SEND_DONATION = 23
CHOOSE_POLL_TO_SEND_DONATION = 34


class SendDonationToChannel(object):
    def send_donation(self, bot, update, user_data):
        channels = channels_table.find({'bot_id': bot.id})
        if update.callback_query:
            update_data = update.callback_query
        else:
            update_data = update
        if channels != 0:
            channel_username = update_data.data.replace("send_donation_to_channel_", "")

            if channel_username == "send_donation_to_channel":
                channels_markup = [channel['channel_username'] for channel in channels]
                bot.send_message(update_data.message.chat.id, "Choose a channel that you want to send",
                                 reply_markup=ReplyKeyboardMarkup([channels_markup]))
                return CHOOSE_CHANNEL_TO_SEND_DONATION

            user_data["channel_username"] = channel_username
            buttons = list()
            buttons.append([InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                 callback_data="cancel_send_donation")])
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
            admin_keyboard = [InlineKeyboardButton(text=string_dict(bot)["add_channel"],
                                                   callback_data="add_channel"),
                              InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                   callback_data="help_back")]
            bot.send_message(update_data.message.chat.id,
                             string_dict(bot)["no_channels"],
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def received_donation(self, bot, update, user_data):

        if update.message.text:
            bot.send_message(user_data["channel_username"], update.message.text)

        elif update.message.photo:
            photo_file = update.message.photo[0].get_file().file_id
            bot.send_photo(user_data["channel_username"], photo=photo_file)

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            bot.send_audio(user_data["channel_username"], audio_file)

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            bot.send_voice(user_data["channel_username"], voice_file)

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            bot.send_document(user_data["channel_username"], document_file)

        elif update.message.sticker:
            sticker_file = update.message.sticker.get_file().file_id
            bot.send_sticker(user_data["channel_username"], sticker_file)

        elif update.message.game:
            sticker_file = update.message.game.get_file().file_id
            bot.send_game(user_data["channel_username"], sticker_file)

        elif update.message.animation:
            animation_file = update.message.animation.get_file().file_id
            bot.send_animation(user_data["channel_username"], animation_file)

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            bot.send_video(user_data["channel_username"], video_file)

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            bot.send_video_note(user_data["channel_username"], video_note_file)

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
                                                callback_data="help_module(channels)")]]
        create_markup = InlineKeyboardMarkup(create_buttons)

        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["send_donation_request_3"],
                         reply_markup=create_markup)

        bot.send_message(user_data["channel_username"],
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
SEND_POLL_TO_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(SendPoll().handle_send_poll, pattern=r"send_poll_to_channel", pass_user_data=True), ],
    states={

        CHOOSE_POLL_TO_SEND: [MessageHandler(Filters.text, SendPoll().handle_send_title, pass_user_data=True), ],
        CHOOSE_POLL_TO_SEND_DONATION: [
            MessageHandler(Filters.text, SendPoll().handle_send_poll, pass_user_data=True), ],
    },
    fallbacks=[CallbackQueryHandler(callback=SendPoll().back, pattern=r"cancel_send_poll"),
               RegexHandler('^Back$', SendPoll().back),
               CallbackQueryHandler(callback=SendPoll().back, pattern=r"error_back"),
               ]
)

SEND_SURVEY_TO_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendSurvey().handle_send_survey,
                                       pattern="send_survey_to_channel", pass_user_data=True)],
    states={
        CHOOSE_CHANNEL_TO_SEND_SURVEY: [
            MessageHandler(Filters.text, SendSurvey().handle_send_survey, pass_user_data=True),
        ],
        CHOOSE_SURVEY_TO_SEND: [MessageHandler(Filters.text, SendSurvey().handle_send_title, pass_user_data=True),
                                ]
    },
    fallbacks=[CallbackQueryHandler(callback=SendSurvey().back, pattern=r"cancel_survey"),
               RegexHandler('^Back$', SendSurvey().back),
               CallbackQueryHandler(callback=SendPoll().back, pattern=r"error_back"),
               ]
)
SEND_DONATION_TO_CHANNEL_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern=r"send_donation_to_channel",
                                       callback=SendDonationToChannel().send_donation,
                                       pass_user_data=True)],

    states={
        DONATION_TO_USERS: [MessageHandler(Filters.all,
                                           SendDonationToChannel().received_donation,
                                           pass_user_data=True),
                            ],
        CHOOSE_CHANNEL_TO_SEND_DONATION: [MessageHandler(Filters.all,
                                                         SendDonationToChannel().send_donation,
                                                         pass_user_data=True),
                                          ],
    },

    fallbacks=[CallbackQueryHandler(callback=SendDonationToChannel().send_donation_finish,
                                    pattern=r"send_donation_finish", pass_user_data=True),
               CallbackQueryHandler(callback=SendDonationToChannel().back,
                                    pattern=r"cancel_send_donation"),
               MessageHandler(filters=Filters.command, callback=SendDonationToChannel().cancel),
               CallbackQueryHandler(callback=SendDonationToChannel().back, pattern=r"error_back"),
               ]
)
