# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, run_async)
import logging

from database import surveys_table, users_table, profile_topics_table, chats_table
from modules.helper_funcs.auth import initiate_chat_id, if_admin

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING_TITLE, CHOOSING_TAGS, CHOOSING_QUESTIONS = range(3)
CHOOSING = 89
TYPING_SEND_TITLE, TYPING_SEND_TAGS = range(2)
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
        update.message.reply_text("Please enter a title for your survey")

        return CHOOSING_TITLE

    @run_async
    def handle_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        # if txt:
        title = txt
        user_data["title"] = title
        bot.send_message(chat_id, "Please send me the tags of the users."
                                  " Which groups of users should answer this survey")

        return CHOOSING_QUESTIONS

    # surveys = [{"admin_id": "",
    #             "title": "",
    #             "bot_id": "",
    #             "target_tags": ["#berlin", "#bucharest"],
    #             "questions": [{"question_id": "", "text": ""},
    #                           {"question_id": "", "text": ""}],
    #             "answers": [{"user_id": "", "question_id": "", "answer": ""}]},

    @run_async
    def receive_questions(self, bot, update, user_data):
        question = update.message.text
        if int(user_data["question_id"]) == 0:
            chat_id, txt = initiate_chat_id(update)
            txt_split = txt.split(" ")
            while "" in txt_split:
                txt_split.remove("")
            i = 0
            send_tags = []
            for i in range(len(txt_split)):
                if txt_split[i][0] == "#":
                    send_tags.append(txt_split[i].lower())
                    i += 1
            user_data["tags"] = send_tags
            if not send_tags:
                bot.send_message(chat_id, "Looks like there are yet no users to send this poll to. "
                                          "Ask them to add this tag to there chat")

            survey = surveys_table.find_one({
                "bot_id": bot.id,
                "title": user_data["title"]
            })

            if not survey:
                surveys_table.insert({
                    "bot_id": bot.id,
                    "title": user_data["title"],
                    "questions": [],
                    "answers": []
                })

                update.message.reply_text("Type your first question or click /cancel")
                user_data["question_id"] = 1
            else:
                update.message.reply_text("You already have a survey with this title.\n"
                                          "Please, type another title for your survey")

        elif user_data["question_id"] > 0:
            survey = surveys_table.find_one({
                "bot_id": bot.id,
                "title": user_data["title"]
            })
            user_data['questions'] = survey["questions"].append({"question_id": int(user_data["question_id"]) - 1,
                                                                 "text": question})

            surveys_table.update({"title": survey["title"]}, survey)
            user_data["question_id"] = int(user_data["question_id"]) + 1
            update.message.reply_text("Please type your next question or write /done if you are finished")

        return CHOOSING_QUESTIONS

    def done(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        send_tags = user_data['tags']
        approved = []
        rejected = []
        sent = []
        for tag in send_tags:
            tags = chats_table.find({"tag": tag})
            for tag in tags:
                if tag['chat_id'] != chat_id:
                    if not any(sent_d['id'] == tag['chat_id'] for sent_d in sent):
                        sent.append(tag['chat_id'])
                        approved.append(tag['name'])

                        bot.send_message(text="Dear {}, a survey has been sent to you. Please press ".format(
                            update.message.from_user.first_name
                        ),
                            reply_markup=InlineKeyboardMarkup(
                                [InlineKeyboardButton(text="START",
                                                      callback_data="survey_{}".format(
                                                          user_data["title"]
                                                      )
                                                      )]
                            ))
                else:
                    rejected.append(tag)
        if len(rejected) > 0:
            bot.send_message(chat_id,
                             "Failed to send messages to tags <i>" + ", ".join(rejected) + "</i>",
                             parse_mode="HTML")
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
        return TYPING_SEND_TAGS

    @run_async
    def handle_send_tags(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["title"] = txt
        approved = []
        sent = []
        tags = chats_table.find()
        print(tags)
        if tags.count() == 0:
            bot.send_message(chat_id, "Looks like there are yet no users to send this poll to. "
                                      "Ask them to add this tag to there chat. Command finished.")
            return ConversationHandler.END
        for tag in tags:
            if tag['chat_id'] != chat_id:
                if not any(sent_d['id'] == tag['chat_id'] for sent_d in sent):
                    sent.append(tag['chat_id'])
                    approved.append(tag['name'])

                    bot.send_message(text="Dear {}, a survey has been sent to you. Please press ".format(
                        update.message.from_user.first_name),
                        reply_markup=InlineKeyboardMarkup(
                            [InlineKeyboardButton(text="START",
                                                  callback_data="survey_{}".format(
                                                      user_data["title"]
                                                  ))]
                        ))

        return ConversationHandler.END

    def cancel(self, bot, update):
        update.message.reply_text("Command is finished. Until next time!")
        return ConversationHandler.END


DELETE_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('delete_survey', SurveyHandler().delete_surveys, pass_user_data=True)],

    states={
        CHOOSING: [MessageHandler(Filters.text,
                                  SurveyHandler().delete_surveys_finish),
                   CommandHandler('cancel', SurveyHandler().cancel),
                   ],
    },

    fallbacks=[
        CommandHandler('done', SurveyHandler().done, pass_user_data=True),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel)]
)

# CHOOSING_TITLE, CHOOSING_TAGS, CHOOSING_QUESTIONS
CREATE_SURVEY_HANDLER = ConversationHandler(  # TODO set an initial survey for the users. Ask a user to answer it by clicking "ANSWER"
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
        CommandHandler('done', SurveyHandler().done, pass_user_data=True),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel)]
)
SEND_SURVEYS_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('send_survey', SurveyHandler().handle_send_survey),

                  ],
    states={
        # TYPING_SEND_TITLE: [MessageHandler(Filters.text, SurveyHandler().handle_send_title, pass_user_data=True)],
        TYPING_SEND_TAGS: [MessageHandler(Filters.text, SurveyHandler().handle_send_tags, pass_user_data=True),
                           CommandHandler('cancel', SurveyHandler().cancel),
                           ],

    },
    fallbacks=[
        CommandHandler('done', SurveyHandler().done, pass_user_data=True),
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel)]
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
        MessageHandler(filters=Filters.command, callback=SurveyHandler().cancel)]
)
