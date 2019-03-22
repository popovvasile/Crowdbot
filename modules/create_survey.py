# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler,
                          run_async, CallbackQueryHandler)
import logging

from database import surveys_table, users_table, chats_table
from modules.helper_funcs.auth import initiate_chat_id, if_admin

# Enable logging
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING_TITLE, CHOOSING_QUESTIONS = range(2)
CHOOSING = 89
TYPING_SEND_TITLE = range(2)
TYPING_TOPICS = 19
DELETE_SURVEY = 23


class SurveyHandler(object):
    @staticmethod
    def facts_to_str(user_data):
        facts = list()

        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @staticmethod
    @run_async
    def start(bot, update, user_data):
        user_data["question_id"] = 0
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back to menu", callback_data="cancel_survey")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        update.message.reply_text("Please enter a title for your survey", reply_markup=reply_markup)
        return CHOOSING_TITLE

    @run_async
    def handle_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if txt == "MAIN SURVEY":
            user_data["title"] = "initial"
        else:
            title = txt
            user_data["title"] = title
            survey = surveys_table.find_one({
                "bot_id": bot.id,
                "title": user_data["title"]
            })
            if not survey:
                surveys_table.insert({
                    "bot_id": bot.id,
                    "title": user_data["title"],
                    "questions": []
                })
                user_data["title"] = title
                update.message.reply_text("Type your first question")
                buttons = list()
                buttons.append([InlineKeyboardButton(text="Back to menu", callback_data="cancel_survey")])
                reply_markup = InlineKeyboardMarkup(
                    buttons)
                update.message.reply_text("If you want to quit this command, click 'Back' ", reply_markup=reply_markup)
                user_data["question_id"] = 1
                return CHOOSING_QUESTIONS

            else:
                buttons = list()
                buttons.append([InlineKeyboardButton(text="Back to menu", callback_data="cancel_survey")])
                reply_markup = InlineKeyboardMarkup(
                    buttons)
                update.message.reply_text("You already have a survey with this title.\n"
                                          "Please, type another title for your survey", reply_markup=reply_markup)
                return CHOOSING_TITLE

    # surveys = [{"admin_id": "",
    #             "title": "",
    #             "bot_id": "",
    #             "questions": [{"question_id": "", "text": ""},
    #                           {"question_id": "", "text": ""}],
    #             "answers": [{"user_id": "", "question_id": "", "answer": ""}]},

    @run_async
    def receive_questions(self, bot, update, user_data):
        question = update.message.text
        if user_data["question_id"] > 0:
            survey = surveys_table.find_one({
                "bot_id": bot.id,
                "title": user_data["title"]
            })
            user_data['questions'] = survey["questions"].append({"question_id": int(user_data["question_id"]) - 1,
                                                                 "text": question})

            surveys_table.update({"title": survey["title"]}, survey)
            user_data["question_id"] = int(user_data["question_id"]) + 1
            update.message.reply_text("Please type your next question or write /done if you are finished")
            buttons = list()
            buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_survey")])
            reply_markup = InlineKeyboardMarkup(
                buttons)
            update.message.reply_text("If you want to quit this command, click 'Back' ", reply_markup=reply_markup)
            return CHOOSING_QUESTIONS

    def done(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        sent = []
        chats = chats_table.find({"bot_id": bot.id})
        for chat in chats:
            if chat['chat_id'] != chat_id:
                if not any(sent_d['id'] == chat['chat_id'] for sent_d in sent):
                    sent.append(chat['chat_id'])

                    bot.send_message(text="Dear {}, a survey has been sent to you. Please press ".format(
                        chat['full_name']
                    ),
                        reply_markup=InlineKeyboardMarkup(
                            [InlineKeyboardButton(text="START",
                                                  callback_data="survey_{}".format(
                                                      user_data["title"]
                                                  )
                                                  )]))
        survey = surveys_table.find_one({
            "bot_id": bot.id,
            "title": user_data["title"]
        })
        questions = ''
        for question in survey["questions"]:
            questions += str(question['question_id'] + 1) + ") " + question['text'] + "\n"
        user_data["questions"] = survey["questions"]
        texr_to_send = "\nQuestions: \n{}".format(questions)
        update.message.reply_text("Created a survey with title: {}\n"
                                  "{}"
                                  "\nUntil next time!".format(survey['title'], texr_to_send))
        surveys_table.update_one({
            "bot_id": bot.id,
            "title": user_data["title"]
        }, {'$set': user_data}, upsert=True)
        user_data.clear()
        return ConversationHandler.END

    @run_async
    def show_surveys(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        bot.send_message(chat_id, "This is the list of your current surveys:")
        command_list = [survey['title'] for survey in surveys_table.find({"bot_id": bot.id})]
        reply_keyboard = [command_list]
        update.message.reply_text(
            "Please choose the survey that you want to see",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_survey")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        update.message.reply_text("If you want to quit this command, click 'Back' ", reply_markup=reply_markup)
        return CHOOSING

    @run_async
    def show_surveys_finish(self, bot, update):  # TODO add a link to results here as well
        chat_id, txt = initiate_chat_id(update)
        survey = surveys_table.find_one({"bot_id": bot.id, 'title': txt})
        txt_to_send = ""
        for answer in survey['answers']:
            txt_to_send += 'Users full name: {},\nQuestion: {}\nAnswer :{} \n\n'.format(
                users_table.find_one({"user_id": answer['user_id']})["full_name"],
                survey["questions"][answer["question_id"] - 1]['text'],
                answer["answer"])
        update.message.reply_text("Here is your requested data : \n {}".format(txt_to_send))
        return ConversationHandler.END

    @run_async
    def delete_surveys(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        bot.send_message(chat_id, "This is the list of your current surveys:")
        command_list = [survey['title'] for survey in surveys_table.find({"bot_id": bot.id})]
        reply_keyboard = [command_list]
        update.message.reply_text(
            "Please choose the survey that you want to delete",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_survey")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        update.message.reply_text("If you want to quit this command, click 'Back' ", reply_markup=reply_markup)
        return DELETE_SURVEY

    @run_async
    def delete_surveys_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        surveys_table.delete_one({"bot_id": bot.id, 'title': txt})
        update.message.reply_text("The survey with the title '{}' has been deleted".format(txt))
        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    @run_async
    def handle_send_survey(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        bot.send_message(chat_id, "This is the list of your current surveys:")
        command_list = [survey['title'] for survey in surveys_table.find({"bot_id": bot.id})]
        reply_keyboard = [command_list]
        update.message.reply_text(
            "Please choose the survey that you want to send",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_survey")])
        reply_markup = InlineKeyboardMarkup(
            buttons)
        update.message.reply_text("If you want to quit this command, click 'Back' ", reply_markup=reply_markup)
        return TYPING_SEND_TITLE

    @run_async
    def handle_send_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["title"] = txt
        sent = []
        chats = chats_table.find({"bot_id": bot.id})
        for chat in chats:
            if chat['chat_id'] != chat_id:
                if not any(sent_d['id'] == chat['chat_id'] for sent_d in sent):
                    sent.append(chat['chat_id'])

                    bot.send_message(chat_id=chat['chat_id'], text="Dear {}, a survey has been sent to you. \n"
                                                                   "Please press the button START".format(
                        chat["full_name"]),
                                     reply_markup=InlineKeyboardMarkup(
                                         [InlineKeyboardButton(text="START",
                                                               callback_data="survey_{}".format(
                                                                   user_data["title"]
                                                               ))]
                                     ))
        bot.send_message(chat_id=chat_id, text="Survey sent to all users!"),
        return ConversationHandler.END

    def cancel(self, bot, update):
        get_help(bot, update)

        return ConversationHandler.END


DELETE_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('delete_survey', SurveyHandler().delete_surveys)],

    states={
        DELETE_SURVEY: [MessageHandler(Filters.text,
                                       SurveyHandler().delete_surveys_finish),
                        CommandHandler('cancel', SurveyHandler().cancel),
                        ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().cancel, pattern=r"cancel_survey"),

        CommandHandler('done', SurveyHandler().done, pass_user_data=True),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel)]
)

CREATE_SURVEY_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('create_survey', SurveyHandler().start, pass_user_data=True)],

    states={
        CHOOSING_TITLE: [MessageHandler(Filters.text,
                                        SurveyHandler().handle_title,
                                        pass_user_data=True),
                         CommandHandler('cancel', SurveyHandler().cancel)],

        CHOOSING_QUESTIONS: [MessageHandler(Filters.text,
                                            SurveyHandler().receive_questions,
                                            pass_user_data=True),
                             CommandHandler('cancel', SurveyHandler().cancel)],
    },

    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().cancel, pattern=r"cancel_survey"),

        CommandHandler('done', SurveyHandler().done, pass_user_data=True),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel)

    ]
)
SEND_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('send_survey', SurveyHandler().handle_send_survey),

                  ],
    states={
        TYPING_SEND_TITLE: [MessageHandler(Filters.text, SurveyHandler().handle_send_title, pass_user_data=True),
                            CommandHandler('cancel', SurveyHandler().cancel)
                            ],

    },
    fallbacks=[
        CommandHandler('done', SurveyHandler().done, pass_user_data=True),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel),
        CallbackQueryHandler(callback=SurveyHandler().cancel, pattern=r"cancel_survey")]
)
SHOW_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('survey_results', SurveyHandler().show_surveys)],

    states={
        CHOOSING: [MessageHandler(Filters.text,
                                  SurveyHandler().show_surveys_finish),
                   CommandHandler('cancel', SurveyHandler().cancel),
                   ],
    },

    fallbacks=[
        CommandHandler('cancel', SurveyHandler().cancel),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel),
        CallbackQueryHandler(callback=SurveyHandler().cancel, pattern=r"cancel_survey")]
)
