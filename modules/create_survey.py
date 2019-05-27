# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
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
    def __init__(self):
        buttons = [[InlineKeyboardButton(text="Back", callback_data="cancel_survey")]]
        self.reply_markup = InlineKeyboardMarkup(
            buttons)
        done_buttons = [[InlineKeyboardButton(text="DONE", callback_data="done_survey")]]
        self.done_markup = InlineKeyboardMarkup(
            done_buttons)

    @staticmethod
    def facts_to_str(user_data):
        facts = list()

        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @run_async
    def start(self, bot, update, user_data):

        user_data["question_id"] = 0
        bot.send_message(update.callback_query.message.chat.id,
                         "Enter a title for your survey", reply_markup=self.reply_markup)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
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
                update.message.reply_text("Type your first question", reply_markup=self.reply_markup)
                user_data["question_id"] = 1
                return CHOOSING_QUESTIONS

            else:

                update.message.reply_text("You already have a survey with this title.\n"
                                          "Please type another title for your survey", reply_markup=self.reply_markup)
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
            update.message.reply_text("Type your next question or click DONE if you are finished",
                                      reply_markup=self.done_markup)

            return CHOOSING_QUESTIONS

    def done(self, bot, update, user_data):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        sent = []
        chats = chats_table.find({"bot_id": bot.id})
        for chat in chats:
            if chat['chat_id'] != update.callback_query.message.chat_id:
                if not any(sent_d['id'] == chat['chat_id'] for sent_d in sent):
                    sent.append(chat['chat_id'])

                    bot.send_message(text="Dear user, a survey has been sent to you.\n"
                                          "Please press START to answer to the questions",
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
        user_data["answers"] = []
        texr_to_send = "\nQuestions: \n{}".format(questions)
        bot.send_message(update.callback_query.message.chat.id,
                         "Created a survey with title: {}\n"
                         "{}"
                         "\nUntil next time!".format(survey['title'], texr_to_send))
        surveys_table.update_one({
            "bot_id": bot.id,
            "title": user_data["title"]
        }, {'$set': user_data}, upsert=True)
        user_data.clear()
        get_help(bot, update)
        logger.info("Admin {} on bot {}:{} added a new survey:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["title"]))
        return ConversationHandler.END

    @run_async
    def show_surveys(self, bot, update):
        survey_list = surveys_table.find({"bot_id": bot.id})
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        if survey_list.count() != 0:

            bot.send_message(update.callback_query.message.chat.id,
                             "This is the list of your current surveys:")
            command_list = [survey['title'] for survey in survey_list]
            reply_keyboard = [command_list]
            bot.send_message(update.callback_query.message.chat.id,
                             "Choose the survey that you want to see",
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            buttons = list()
            buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_survey")])
            reply_markup = InlineKeyboardMarkup(
                buttons)
            bot.send_message(update.callback_query.message.chat.id,
                             "If you want to quit this command, click 'Back' ", reply_markup=reply_markup)
            return CHOOSING
        else:

            admin_keyboard = [InlineKeyboardButton(text="Create", callback_data="create_survey"),
                              InlineKeyboardButton(text="Back", callback_data="help_back")]
            bot.send_message(update.callback_query.message.chat.id,
                             """You have no surveys created yet. \n"""
                             """Click "Create" to configure your first survey or "Back" for main menu""",
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    @run_async
    def show_surveys_finish(self, bot, update):  # TODO add a link to results here as well
        chat_id, txt = initiate_chat_id(update)
        survey = surveys_table.find_one({"bot_id": bot.id, 'title': txt})
        txt_to_send = ""
        if survey.get("answers") is not None:
            for answer in survey['answers']:
                txt_to_send += 'Users full name: {},\nQuestion: {}\nAnswer :{} \n\n'.format(
                    users_table.find_one({"user_id": answer['user_id']})["name"],
                    survey["questions"][answer["question_id"] - 1]['text'],
                    answer["answer"])
            update.message.reply_text("Here is your requested data : \n {}".format(txt_to_send),
                                      reply_markup=ReplyKeyboardRemove())
            admin_keyboard = [
                InlineKeyboardButton(text="Back", callback_data="help_back")]
            update.message.reply_text("Back to main menu",
                                      reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        else:
            update.message.reply_text("Your survey doesn't have any answers yet =/",
                                      reply_markup=ReplyKeyboardRemove())
            admin_keyboard = [InlineKeyboardButton(text="Send", callback_data="send_survey"),
                              InlineKeyboardButton(text="Back", callback_data="help_back")]
            update.message.reply_text("Send your users a reminder to answer to your questions using the button 'Send'",
                                      reply_markup=InlineKeyboardMarkup([admin_keyboard]))
        return ConversationHandler.END

    @run_async
    def delete_surveys(self, bot, update):
        surveys = surveys_table.find({"bot_id": bot.id})
        if surveys.count() != 0:
            bot.send_message(update.callback_query.message.chat.id,
                             "This is the list of your current surveys:", reply_markup=self.reply_markup)
            command_list = [survey['title'] for survey in surveys_table.find({"bot_id": bot.id})]
            reply_keyboard = [command_list]
            bot.send_message(update.callback_query.message.chat.id,
                             "Choose the survey that you want to delete",
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

            bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)

            return DELETE_SURVEY
        else:
            bot.delete_message(chat_id=update.callback_query.message.chat_id,
                               message_id=update.callback_query.message.message_id)
            admin_keyboard = [InlineKeyboardButton(text="Create", callback_data="create_survey"),
                              InlineKeyboardButton(text="Back", callback_data="help_back")]
            bot.send_message(update.callback_query.message.chat.id,
                             """You have no surveys created yet. \n"""
                             """Click "Create" to configure your first survey or "Back" for main menu""",
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    @run_async
    def delete_surveys_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        surveys_table.delete_one({"bot_id": bot.id, 'title': txt})
        update.message.reply_text("The survey with the title '{}' has been deleted".format(txt),
                                  reply_markup=ReplyKeyboardRemove())
        get_help(bot, update)
        logger.info("Admin {} on bot {}:{} deleted a survey:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, txt))
        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    @run_async
    def handle_send_survey(self, bot, update):
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        surveys_list = surveys_table.find({"bot_id": bot.id})
        if surveys_list.count() != 0:
            bot.send_message(update.callback_query.message.chat.id,
                             "This is the list of your current surveys:", reply_markup=self.reply_markup)
            command_list = [survey['title'] for survey in surveys_table.find({"bot_id": bot.id})]
            reply_keyboard = [command_list]
            bot.send_message(update.callback_query.message.chat.id,
                             "Choose the survey that you want to send to your users",
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
            return TYPING_SEND_TITLE
        else:

            admin_keyboard = [InlineKeyboardButton(text="Create", callback_data="create_survey"),
                              InlineKeyboardButton(text="Back", callback_data="help_back")]
            bot.send_message(update.callback_query.message.chat.id,
                             """You have no surveys created yet. \n"""
                             """Click "Create" to configure your first survey or "Back" for main menu""",
                             reply_markup=InlineKeyboardMarkup([admin_keyboard]))
            return ConversationHandler.END

    @run_async
    def handle_send_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["title"] = txt
        survey = surveys_table.find_one({"bot_id": bot.id, 'title': txt})

        sent = []
        chats = chats_table.find({"bot_id": bot.id})
        for chat in chats:
            # if chat['chat_id'] != chat_id:
            if not any(sent_d['id'] == chat['chat_id'] for sent_d in sent):
                sent.append(chat['chat_id'])
                bot.send_message(chat_id=chat['chat_id'], text="Dear user, a survey has been sent to you.\n"
                                                               "Please press START to answer to the questions",
                                 reply_markup=InlineKeyboardMarkup(
                                     [[InlineKeyboardButton(text="START",
                                                            callback_data="survey_{}".format(
                                                                str(txt)
                                                            ))]]
                                 ))

        if len(sent) == 0:
            bot.send_message(chat_id, "Looks like there are yet no users to send this survey to. "
                                      "No surveys sent :( ", reply_markup=ReplyKeyboardRemove())
        else:
            bot.send_message(chat_id=chat_id, text="Survey sent to all users!", reply_markup=ReplyKeyboardRemove())
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
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)

        get_help(bot, update)
        return ConversationHandler.END


DELETE_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=SurveyHandler().delete_surveys,
                                       pattern=r"delete_survey")],

    states={
        DELETE_SURVEY: [MessageHandler(Filters.text,
                                       SurveyHandler().delete_surveys_finish),
                        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"),
                        ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().back)]
)

CREATE_SURVEY_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=SurveyHandler().start,
                                       pattern=r"create_survey", pass_user_data=True)],

    states={
        CHOOSING_TITLE: [MessageHandler(Filters.text,
                                        SurveyHandler().handle_title,
                                        pass_user_data=True),
                         CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey")
                         ],

        CHOOSING_QUESTIONS: [MessageHandler(Filters.text,
                                            SurveyHandler().receive_questions,
                                            pass_user_data=True),
                             CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"),
                             ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"),

        CallbackQueryHandler(callback=SurveyHandler().done, pattern=r"done_survey", pass_user_data=True),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().back)

    ]
)
SEND_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=SurveyHandler().handle_send_survey,
                                       pattern=r"send_survey"),

                  ],
    states={
        TYPING_SEND_TITLE: [MessageHandler(Filters.text, SurveyHandler().handle_send_title, pass_user_data=True),
                            CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"),
                            ],

    },
    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel)]
)

SHOW_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(callback=SurveyHandler().show_surveys,
                                       pattern=r"surveys_results"),
                  ],

    states={
        CHOOSING: [MessageHandler(Filters.text,
                                  SurveyHandler().show_surveys_finish),
                   CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"),
                   ],
    },

    fallbacks=[
        CallbackQueryHandler(callback=SurveyHandler().back, pattern=r"cancel_survey"),
        CommandHandler('cancel', SurveyHandler().cancel),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel),
    ]
)
