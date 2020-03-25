from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, CallbackQueryHandler, MessageHandler, Filters
from database import surveys_table, chatbots_table, groups_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.helper import get_help
from logs import logger

MY_GROUPS, MANAGE_GROUP, ADD_GROUP, \
CHOOSE_TO_REMOVE, REMOVE_GROUP, \
CHOOSE_TO_SEND_POST, POST_TO_GROUP, MESSAGE_TO_USERS = range(8)

CHOOSE_GROUP_TO_SEND_SURVEY, CHOOSE_SURVEY_TO_SEND = range(2)


# for sending surveys to groups

class SendSurvey(object):
    def handle_send_survey(self, update, context):  # TODO for callback_query and text messages
        if update.callback_query:
            group_name = update.callback_query.data.replace("send_survey_to_group_", "")
            update_data = update.callback_query
            if group_name == "send_survey_to_group":
                groups_markup = [group['group_name'] for group in groups_table.find({'bot_id': context.bot.id})]
                context.bot.send_message(update.callback_query.message.chat.id, "Choose a group that you want to send",
                                         reply_markup=ReplyKeyboardMarkup([groups_markup]))
                return CHOOSE_GROUP_TO_SEND_SURVEY
        else:
            group_name = update.message.text
            update_data = update
        buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_back")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.delete_message(update_data.message.chat.id, update_data.message.message_id)
        context.user_data['group'] = group_name
        surveys_list = surveys_table.find({"bot_id": context.bot.id})
        if surveys_list.count() != 0:
            context.bot.send_message(update_data.message.chat.id,
                                     context.bot.lang_dict["survey_str_18"], reply_markup=reply_markup)
            command_list = [survey['title'] for survey in surveys_list]
            reply_keyboard = [command_list]
            context.bot.send_message(update_data.message.chat.id,
                                     context.bot.lang_dict["survey_str_19"],
                                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return CHOOSE_SURVEY_TO_SEND
        else:
            admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["create_button_str"],
                                                   callback_data="create_survey"),
                              InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                   callback_data="help_back")]
            context.bot.send_message(update_data.message.chat.id,
                                     context.bot.lang_dict["survey_str_23"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def handle_send_title(self, update, context):
        chat_id, txt = initiate_chat_id(update)
        context.user_data["title"] = txt
        group = groups_table.find_one({"group_name": context.user_data["group"]})
        context.bot.send_message(chat_id=group["group_id"], text=context.bot.lang_dict["survey_str_20"],
                                 reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton(text=context.bot.lang_dict["start_button"],
                                                            url="https://t.me/{}?start=survey_{}".format(
                                                                context.bot.username,
                                                                context.user_data["title"]),
                                                            callback_data="survey_{}".format(
                                                                str(txt)
                                                            ))]]
                                 ))
        create_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                callback_data="help_module(channels_groups)")]]
        create_markup = InlineKeyboardMarkup(create_buttons)
        context.bot.send_message(update.message.chat.id, context.bot.lang_dict["back_text"],
                                 reply_markup=create_markup)
        logger.info("Admin {} on bot {}:{} sent a survey to the users:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, txt))
        return ConversationHandler.END

    def cancel(self, update, context):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(update, context)
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(update.effective_chat.id,
                                   update.effective_message.message_id)
        get_help(update, context)
        return ConversationHandler.END


DONATION_TO_USERS = 1
CHOOSE_GROUP_TO_SEND_DONATION = 23
CHOOSE_POLL_TO_SEND_DONATION = 34


class SendDonationToGroup(object):
    def send_donation(self, update, context):
        groups = groups_table.find({'bot_id': context.bot.id})
        update_data = update.callback_query
        group_id = update.callback_query.data.replace("send_donation_to_group_", "")

        if groups != 0:
            # TODO here is a bug, AttributeError: 'Update' object has no attribute 'data'

            if group_id == "send_donation_to_group":
                groups_markup = [group['group_name'] for group in groups]
                context.bot.send_message(update_data.message.chat.id, "Choose a group that you want to send",
                                         reply_markup=ReplyKeyboardMarkup([groups_markup]))
                return CHOOSE_GROUP_TO_SEND_DONATION

            context.user_data["group_name"] = group_id
            buttons = list()
            buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                 callback_data="help_back")])
            reply_markup = InlineKeyboardMarkup(
                buttons)

            context.bot.delete_message(chat_id=update_data.message.chat_id,
                                       message_id=update_data.message.message_id)
            chatbot = chatbots_table.find_one({"bot_id": context.bot.id})
            if chatbot.get("donate") != {} and "donate" in chatbot:
                context.bot.send_message(update_data.message.chat.id,
                                         context.bot.lang_dict["send_donation_request_1"],
                                         reply_markup=reply_markup)
                return DONATION_TO_USERS
            else:
                admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["allow_donations_button"],
                                                       callback_data="allow_donation"),
                                  InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                       callback_data="help_back")]
                context.bot.send_message(update_data.message.chat.id,
                                         context.bot.lang_dict["allow_donation_text"],
                                         reply_markup=InlineKeyboardMarkup([admin_keyboard]))
                return ConversationHandler.END
        else:
            admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["add_group"],
                                                   callback_data="add_group"),
                              InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                   callback_data="help_back")]
            context.bot.send_message(update_data.message.chat.id,
                                     context.bot.lang_dict["no_groups"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def received_donation(self, update, context):
        if "content" not in context.user_data:
            context.user_data["content"] = []
        if update.message.text:
            context.user_data["content"].append({"text": update.message.text})

        elif update.message.photo:
            photo_file = update.message.photo[-1].get_file().file_id
            context.user_data["content"].append({"photo_file": photo_file})

        elif update.message.audio:
            audio_file = update.message.audio.get_file().file_id
            context.user_data["content"].append({"audio_file": audio_file})

        elif update.message.voice:
            voice_file = update.message.voice.get_file().file_id
            context.user_data["content"].append({"audio_file": voice_file})

        elif update.message.document:
            document_file = update.message.document.get_file().file_id
            context.user_data["content"].append({"document_file": document_file})

        elif update.message.video:
            video_file = update.message.video.get_file().file_id
            context.user_data["content"].append({"video_file": video_file})

        elif update.message.video_note:
            video_note_file = update.message.audio.get_file().file_id
            context.user_data["content"].append({"video_file": video_note_file})

        final_reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                   callback_data="send_donation_finish")],
             [InlineKeyboardButton(text=context.bot.lang_dict["cancel_button"],
                                   callback_data="help_module(donation_payment)k")]
             ]
        )
        context.bot.send_message(update.message.chat_id,
                                 context.bot.lang_dict["send_donation_request_2"],
                                 reply_markup=final_reply_markup)

        return DONATION_TO_USERS

    def send_donation_finish(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        buttons = list()
        buttons.append([InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                             callback_data="help_module(channels_groups)")])
        final_reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.send_message(update.callback_query.message.chat_id,
                                 context.bot.lang_dict["send_donation_request_3"],
                                 reply_markup=final_reply_markup)

        donation_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=context.bot.lang_dict["donate_button"],

                                                                            url="https://t.me/{}?start=pay_donation".format(
                                                                                context.bot.username),
                                                                            )]])
        for content_dict in context.user_data["content"]:
            if "text" in content_dict:
                context.bot.send_message(context.user_data["group_name"],
                                         content_dict["text"])
            if "audio_file" in content_dict:
                context.bot.send_audio(context.user_data["group_name"], content_dict["audio_file"])
            if "voice_file" in content_dict:
                context.bot.send_voice(context.user_data["group_name"], content_dict["voice_file"])
            if "video_file" in content_dict:
                context.bot.send_video(context.user_data["group_name"], content_dict["video_file"])
            if "video_note_file" in content_dict:
                context.bot.send_video_note(context.user_data["group_name"], content_dict["video_note_file"])
            if "document_file" in content_dict:
                if ".png" in content_dict["document_file"] or ".jpg" in content_dict["document_file"]:
                    context.bot.send_photo(context.user_data["group_name"], content_dict["document_file"])
                else:
                    context.bot.send_document(context.user_data["group_name"], content_dict["document_file"])
            if "photo_file" in content_dict:
                context.bot.send_photo(context.user_data["group_name"], content_dict["photo_file"])
            if "animation_file" in content_dict:
                context.bot.send_animation(context.user_data["group_name"], content_dict["animation_file"])
            if "sticker_file" in content_dict:
                context.bot.send_sticker(context.user_data["group_name"], content_dict["sticker_file"])

            context.bot.send_message(context.user_data["group_name"],
                                     text=context.bot.lang_dict["donate_button"],
                                     reply_markup=donation_reply_markup)
            context.user_data.clear()
        return ConversationHandler.END

    def cancel(self, update, context):
        update.message.reply_text(
            "Command is cancelled =("
        )
        get_help(update, context)
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(update.effective_chat.id,
                                   update.effective_message.message_id)
        get_help(update, context)
        return ConversationHandler.END

    @staticmethod
    def error(update, context, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)


SEND_SURVEY_TO_GROUP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(SendSurvey().handle_send_survey,
                                       pattern="send_survey_to_group")],
    states={
        CHOOSE_GROUP_TO_SEND_SURVEY: [
            MessageHandler(Filters.text, SendSurvey().handle_send_survey),
        ],
        CHOOSE_SURVEY_TO_SEND: [MessageHandler(Filters.text, SendSurvey().handle_send_title),
                                ]
    },
    fallbacks=[CallbackQueryHandler(callback=SendSurvey().back, pattern=r"help_back"),
               CallbackQueryHandler(callback=SendSurvey().back, pattern=r"help_module"),
               MessageHandler(Filters.regex('^Back$'), SendSurvey().back),
               ]
)
SEND_DONATION_TO_GROUP_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(pattern=r"send_donation_to_group",
                                       callback=SendDonationToGroup().send_donation)],

    states={
        DONATION_TO_USERS: [MessageHandler(Filters.all,
                                           SendDonationToGroup().received_donation),
                            ],
        CHOOSE_GROUP_TO_SEND_DONATION: [MessageHandler(Filters.all,
                                                       SendDonationToGroup().send_donation),
                                        ],
    },

    fallbacks=[CallbackQueryHandler(callback=SendDonationToGroup().send_donation_finish,
                                    pattern=r"send_donation_finish"),
               CallbackQueryHandler(callback=SendDonationToGroup().back, pattern=r"help_back"),
               CallbackQueryHandler(callback=SendDonationToGroup().back, pattern=r"help_module"),

               ]
)
