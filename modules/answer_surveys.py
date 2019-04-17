# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler, RegexHandler, run_async, CallbackQueryHandler)
from modules.helper_funcs.helper import get_help

import logging

# Enable logging
from database import surveys_table
from modules.helper_funcs.auth import initiate_chat_id

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING_SURVEY, ANSWERING = range(2)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


# surveys = [{"admin_id": "",
#             "title": "",
#             "bot_id": "",
#             "target_tags": ["#berlin", "#bucharest"],
#             "questions": [{"question_id": "", "text": ""},
#                           {"question_id": "", "text": ""}],
#             "answers": [{"user_id": "", "question_id": "", "answer": ""}]},
#            {"admin_id": "",
#             "title": "",
#             "bot_id": "",
#             "questions": [{"question_id": "", "text": ""},
#                           {"question_id": "", "text": ""}]
#               }]


class AnswerSurveys(object):
    def __init__(self):
        buttons = [[InlineKeyboardButton(text="Cancel survey", callback_data="cancel_survey_answering")]]
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @run_async
    def start_answering(self, bot, update, user_data):  # TODO add the "skip" button
        user_data['title'] = update.callback_query.data.replace("survey_", "")
        user_data["question_id"] = 0
        survey = surveys_table.find_one({
            "bot_id": bot.id,
            "title": user_data["title"]
        })
        for answer in survey["answers"]:
            if answer.get('user_id', "") == update.message.from_user.id:
                survey["answers"] = []
                surveys_table.update({"title": survey["title"]}, survey)
        bot.send_message(update.message.chat_id,
                         "Please answer the following question.\n\n"
                         )
        bot.send_message(update.message.chat_id, survey["questions"][int(user_data["question_id"])]["text"],
                         reply_markup=self.reply_markup)

        return ANSWERING

    @run_async
    def received_information(self, bot, update, user_data):
        user_data["question_id"] += 1
        survey = surveys_table.find_one({
            "bot_id": bot.id,
            "title": user_data["title"]
        })
        answer = update.message.text
        user_id = update.message.from_user.id

        survey["answers"].append({"user_id": user_id,
                                  "question_id": int(user_data["question_id"]),
                                  "title": survey["title"],
                                  "answer": answer})
        surveys_table.update({"title": survey["title"]}, survey)
        if user_data["question_id"] > len(survey["questions"]) - 1:
            to_send_text = ""
            users_answers = []
            for answer in survey["answers"]:
                if answer["user_id"] == user_id and answer["title"] == user_data["title"]:
                    users_answers.append(answer)
                    question = survey["questions"][int(answer["question_id"]) - 1]["text"]
                    to_send_text += "Question:{}, Answer: {} \n".format(question,
                                                                        answer['answer'])

            bot.send_message(update.message.chat_id, "Thank you for your responses!\n" + to_send_text + "\n" +
                             "Until next time!")
            del user_data
            del answer
            return ConversationHandler.END

        else:

            question = survey["questions"][int(user_data["question_id"])]["text"]
            bot.send_message(update.message.chat_id, question,
                             reply_markup=self.reply_markup)
            user_data["last_question"] = question

            return ANSWERING

    @run_async
    def done(self, bot, update, user_data):
        update.message.reply_text("Thank you for your responses!"
                                  "{}"
                                  "Until next time!".format(facts_to_str(user_data)))

        user_data.clear()
        return ConversationHandler.END

    @run_async
    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

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


ANSWER_SURVEY_HANDLER = ConversationHandler(
    entry_points=[CallbackQueryHandler(AnswerSurveys().start_answering, pattern=r"survey_", pass_user_data=True)],

    states={
        ANSWERING: [MessageHandler(Filters.all,
                                   AnswerSurveys().received_information,
                                   pass_user_data=True)],

    },

    fallbacks=[CommandHandler('done', AnswerSurveys().back),
               CommandHandler('cancel', AnswerSurveys().cancel),
               MessageHandler(filters=Filters.command, callback=AnswerSurveys().back)]
)

__mod_name__ = "Surveys"
__admin_help__ = """
 Here you can:
 -  Create a survey and ask your users any questions \n
 -  Delete a survey\n
 -  Send an invitation to answer to your survey\n
 -  Check the results of the survey

"""

__admin_keyboard__ = [
    InlineKeyboardButton(text="Create", callback_data="create_survey"),
     InlineKeyboardButton(text="Delete", callback_data="delete_survey"),
    InlineKeyboardButton(text="Send", callback_data="send_survey"),
     InlineKeyboardButton(text="Results", callback_data="surveys_results")
]
