# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler)
import logging

from database import surveys_table, users_table
from helper_funcs.auth import initiate_chat_id
from helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING_TITLE, CHOOSING_QUESTIONS = range(2)
CHOOSING = 89
TYPING_SEND_TITLE = range(2)
TYPING_TOPICS = 19
DELETE_SURVEY = 23


def surveys_send_menu(update, context):
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
    no_channel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=context.bot.lang_dict["send_survey_to_group"],
                               callback_data="send_survey_to_group")],
         [InlineKeyboardButton(text=context.bot.lang_dict["send_survey_to_channel"],
                               callback_data="send_survey_to_channel")],

         ]
    )
    context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["post_message"], reply_markup=no_channel_keyboard)
    return ConversationHandler.END


def surveys_menu(update, context):
    string_d_str = context.bot.lang_dict
    context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
    no_channel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=string_d_str["create_button_str"], callback_data="create_survey")],
         [InlineKeyboardButton(text=string_d_str["delete_button_str"], callback_data="delete_survey")],
         [InlineKeyboardButton(text=string_d_str["send_button"], callback_data="sending_survey_menu")],
         [InlineKeyboardButton(text=string_d_str["results_button"], callback_data="results_surveys")],
         [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")]
         ]
    )
    context.bot.send_message(update.callback_query.message.chat.id,
                             context.bot.lang_dict["polls_str_9"], reply_markup=no_channel_keyboard)
    return ConversationHandler.END


class SurveyHandler(object):
    @staticmethod
    def facts_to_str(context):
        facts = list()

        for key, value in context.user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    def start(self, update, context):
        buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        context.user_data["question_id"] = 0
        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["survey_str_1"], reply_markup=reply_markup)
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        return CHOOSING_TITLE

    def handle_title(self, update, context):
        buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        chat_id, txt = initiate_chat_id(update)
        if txt == context.bot.lang_dict["main_survey_button"]:
            context.user_data["title"] = "initial"
        else:
            title = txt
            context.user_data["title"] = title
            survey = surveys_table.find_one({
                "bot_id": context.bot.id,
                "title": context.user_data["title"]
            })
            if not survey:
                context.user_data["title"] = title
                update.message.reply_text(context.bot.lang_dict["survey_str_2"], reply_markup=reply_markup)
                context.user_data["question_id"] = 1
                context.user_data["questions"] = []
                return CHOOSING_QUESTIONS

            else:

                update.message.reply_text(context.bot.lang_dict["survey_str_3"], reply_markup=reply_markup)
                return CHOOSING_TITLE

    # surveys = [{"admin_id": "",
    #             "title": "",
    #             "bot_id": "",
    #             "questions": [{"question_id": "", "text": ""},
    #                           {"question_id": "", "text": ""}],
    #             "answers": [{"user_id": "", "question_id": "", "answer": ""}]},

    def receive_questions(self, update, context):
        done_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["done_button"],
                                              callback_data="done_survey")]]
        done_markup = InlineKeyboardMarkup(
            done_buttons)
        question = update.message.text
        if context.user_data["question_id"] > 0:
            context.user_data["questions"].append({"question_id": int(context.user_data["question_id"]) - 1,
                                                   "text": question})
            context.user_data["question_id"] = int(context.user_data["question_id"]) + 1
            update.message.reply_text(context.bot.lang_dict["survey_str_4"],
                                      reply_markup=done_markup)

            return CHOOSING_QUESTIONS

    def done(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        questions = ''
        for question in context.user_data["questions"]:
            questions += str(question['question_id'] + 1) + ") " + question['text'] + "\n"
        context.user_data["questions"] = context.user_data["questions"]
        context.user_data["answers"] = []
        texr_to_send = "\nQuestions: \n{}".format(questions)
        admin_keyboard = [InlineKeyboardButton(text=context.bot.lang_dict["send_button"],
                                               callback_data="send_survey_to_channel"),
                          InlineKeyboardButton(text=context.bot.lang_dict["menu_button"],
                                               callback_data="help_module(polls)")]
        context.bot.send_message(update.callback_query.message.chat.id,
                                 context.bot.lang_dict["survey_str_6"].format(
                                     context.user_data['title'], texr_to_send),
                                 reply_markup=InlineKeyboardMarkup(
                                     [admin_keyboard]))
        context.user_data.pop('to_delete', None)
        surveys_table.update_one({
            "bot_id": context.bot.id,
            "title": context.user_data["title"]
        }, {'$set': context.user_data}, upsert=True)
        logger.info("Admin {} on bot {}:{} added a new survey:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, context.user_data["title"]))
        context.user_data.clear()
        return ConversationHandler.END

    def show_surveys(self, update, context):
        survey_list = surveys_table.find({"bot_id": context.bot.id})
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        if survey_list.count() != 0:

            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_7"])
            command_list = [survey['title'] for survey in survey_list]
            reply_keyboard = [command_list]
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_8"],
                                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            buttons = list()
            buttons.append(
                [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")])
            reply_markup = InlineKeyboardMarkup(
                buttons)
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["back_text"], reply_markup=reply_markup)
            return CHOOSING
        else:

            admin_keyboard = [
                InlineKeyboardButton(text=context.bot.lang_dict["create_button_str"], callback_data="create_survey"),
                InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")]
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_9"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def show_surveys_finish(self, update, context):  # TODO add a link to results here as well
        chat_id, txt = initiate_chat_id(update)
        survey = surveys_table.find_one({"bot_id": context.bot.id, 'title': txt})
        txt_to_send = ""
        try:
            if survey.get("answers") is not None:
                for answer in survey['answers']:
                    txt_to_send += context.bot.lang_dict["survey_str_10"].format(
                        users_table.find_one({"user_id": answer['user_id']})["full_name"],
                        survey["questions"][answer["question_id"] - 1]['text'],
                        answer["answer"])
                update.message.reply_text(context.bot.lang_dict["survey_str_11"].format(txt_to_send),
                                          reply_markup=ReplyKeyboardRemove())
                admin_keyboard = [
                    InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="help_module(polls)")]
                update.message.reply_text(context.bot.lang_dict["back_text"],
                                          reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            else:
                update.message.reply_text(context.bot.lang_dict["survey_str_12"],
                                          reply_markup=ReplyKeyboardRemove())
                admin_keyboard = [
                    InlineKeyboardButton(text=context.bot.lang_dict["send_button"],
                                         callback_data="send_survey_to_users"),
                    InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                         callback_data="help_module(polls)")]
                update.message.reply_text(context.bot.lang_dict["survey_str_13"],
                                          reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        except KeyError:
            update.message.reply_text("Please click /start to register yourself as a user",
                                      reply_markup=ReplyKeyboardRemove())
            get_help(update, context)
        return ConversationHandler.END

    def delete_surveys(self, update, context):
        buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        surveys = surveys_table.find({"bot_id": context.bot.id})
        if surveys.count() != 0:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_14"], reply_markup=reply_markup)
            command_list = [survey['title'] for survey in surveys_table.find({"bot_id": context.bot.id})]
            reply_keyboard = [command_list]
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_15"],
                                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

            context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                       message_id=update.callback_query.message.message_id)

            return DELETE_SURVEY
        else:
            context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                       message_id=update.callback_query.message.message_id)
            admin_keyboard = [
                InlineKeyboardButton(text=context.bot.lang_dict["create_button_str"], callback_data="create_survey"),
                InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")]
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_16"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def delete_surveys_finish(self, update, context):
        chat_id, txt = initiate_chat_id(update)
        surveys_table.delete_one({"bot_id": context.bot.id, 'title': txt})
        update.message.reply_text(context.bot.lang_dict["survey_str_17"].format(txt),
                                  reply_markup=ReplyKeyboardRemove())
        logger.info("Admin {} on bot {}:{} deleted a survey:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, txt))
        admin_keyboard = [
            InlineKeyboardButton(text=context.bot.lang_dict["create_button_str"], callback_data="create_survey"),
            InlineKeyboardButton(text=context.bot.lang_dict["menu_button"], callback_data="help_module(polls)")]
        context.bot.send_message(update.message.chat.id,
                                 context.bot.lang_dict["survey_str_24"],
                                 reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        return ConversationHandler.END

    @staticmethod
    def error(update, context, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def handle_send_survey(self, update, context):
        buttons = [
            [InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)
        surveys_list = surveys_table.find({"bot_id": context.bot.id})
        if surveys_list.count() != 0:
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_18"], reply_markup=reply_markup)
            command_list = [survey['title'] for survey in surveys_table.find({"bot_id": context.bot.id})]
            reply_keyboard = [command_list]
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_19"],
                                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return TYPING_SEND_TITLE
        else:

            admin_keyboard = [
                InlineKeyboardButton(text=context.bot.lang_dict["create_button"], callback_data="create_survey"),
                InlineKeyboardButton(text=context.bot.lang_dict["back_button"], callback_data="help_module(polls)")]
            context.bot.send_message(update.callback_query.message.chat.id,
                                     context.bot.lang_dict["survey_str_23"],
                                     reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    def handle_send_title(self, update, context):
        chat_id, txt = initiate_chat_id(update)
        context.user_data["title"] = txt
        sent = []
        chats = users_table.find({"bot_id": context.bot.id})
        for chat in chats:
            # if chat['chat_id'] != chat_id:
            if not any(sent_d == chat['chat_id'] for sent_d in sent):
                # TODO TypeError: 'int' object is not subscriptable
                sent.append(chat['chat_id'])
                context.bot.send_message(chat_id=chat['chat_id'], text=context.bot.lang_dict["survey_str_20"],
                                         reply_markup=InlineKeyboardMarkup(
                                             [[InlineKeyboardButton(text=context.bot.lang_dict["start_button"],
                                                                    callback_data="survey_{}".format(
                                                                        str(txt)
                                                                    ))]]
                                         ))

        if len(sent) == 0:
            context.bot.send_message(chat_id, context.bot.lang_dict["survey_str_21"],
                                     reply_markup=ReplyKeyboardRemove())
        else:
            context.bot.send_message(chat_id=chat_id, text=context.bot.lang_dict["survey_str_22"],
                                     reply_markup=ReplyKeyboardRemove())
        logger.info("Admin {} on bot {}:{} sent a survey to the users:{}".format(
            update.effective_user.first_name, context.bot.first_name, context.bot.id, txt))
        create_buttons = [[InlineKeyboardButton(text=context.bot.lang_dict["back_button"],
                                                callback_data="help_module(polls)")]]
        create_markup = InlineKeyboardMarkup(create_buttons)
        context.bot.send_message(chat_id, context.bot.lang_dict["back_text"], reply_markup=create_markup)
        return ConversationHandler.END

    def back(self, update, context):
        context.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                   message_id=update.callback_query.message.message_id)

        get_help(update, context)
        return ConversationHandler.END


SEND_SURVEYS_MENU_HANDLER = CallbackQueryHandler(callback=surveys_send_menu, pattern="sending_survey_menu")

SURVEYS_MENU = CallbackQueryHandler(callback=surveys_menu, pattern="surveys")

DELETE_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=SurveyHandler().delete_surveys,
                                       pattern=r"delete_survey")],

    states={
        DELETE_SURVEY: [MessageHandler(Filters.text,
                                       SurveyHandler().delete_surveys_finish),
                        ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"help_module"),
    ]
)

CREATE_SURVEY_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=SurveyHandler().start,
                                       pattern=r"create_survey")],

    states={
        CHOOSING_TITLE: [MessageHandler(Filters.text,
                                        SurveyHandler().handle_title),
                         ],

        CHOOSING_QUESTIONS: [MessageHandler(Filters.text,
                                            SurveyHandler().receive_questions),
                             ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"help_module"),

        CallbackQueryHandler(callback=SurveyHandler().done, pattern=r"done_survey"),

    ]
)
SEND_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=SurveyHandler().handle_send_survey,
                                       pattern=r"send_survey_to_users"),

                  ],
    states={
        TYPING_SEND_TITLE: [MessageHandler(Filters.text, SurveyHandler().handle_send_title),
                            ],

    },
    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"help_module"),
    ]
)

SHOW_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=SurveyHandler().show_surveys,
                                       pattern=r"results_surveys"),
                  ],

    states={
        CHOOSING: [MessageHandler(Filters.text,
                                  SurveyHandler().show_surveys_finish),
                   ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"help_module"),
    ]
)
