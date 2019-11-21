# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (MessageHandler, Filters, ConversationHandler, CallbackQueryHandler, )
from helper_funcs.main_runnner_helper import get_help
from database import surveys_table
from helper_funcs.lang_strings.strings import string_dict

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

    def start_answering(self, bot, update, user_data):
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["cancel_button_survey"],
                                         callback_data="help_back")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        bot.delete_message(chat_id=update.callback_query.message.chat_id,
                           message_id=update.callback_query.message.message_id)
        user_data['title'] = update.callback_query.data.replace("survey_", "")
        user_data["question_id"] = 0
        survey = surveys_table.find_one({
            "bot_id": bot.id,
            "title": user_data["title"]
        })
        if "answers" not in survey:
            survey["answers"] = []
            surveys_table.update({"title": survey["title"]}, survey)
        for index, answer in enumerate(survey["answers"]):
            if answer.get('user_id', "") == update.callback_query.message.from_user.id:
                survey["answers"][index] = []
                surveys_table.update({"title": survey["title"]}, survey)
        bot.send_message(update.callback_query.message.chat_id,
                         string_dict(bot)["answer_survey_str_1"]
                         )
        bot.send_message(update.callback_query.message.chat_id,
                         survey["questions"][int(user_data["question_id"])]["text"],
                         reply_markup=reply_markup)

        return ANSWERING

    def received_information(self, bot, update, user_data):
        buttons = [[InlineKeyboardButton(text=string_dict(bot)["cancel_button_survey"],
                                         callback_data="help_back")]]
        reply_markup = InlineKeyboardMarkup(
            buttons)
        user_data["question_id"] += 1
        survey = surveys_table.find_one({
            "bot_id": bot.id,
            "title": user_data["title"]
        })
        answer = update.message.text
        user_id = update.message.from_user.id

        survey["answers"] = list(filter(lambda i: i['user_id'] != update.effective_user.id, survey["answers"]))

        if "answers" not in user_data:
            user_data["answers"] = survey["answers"]
        user_data["answers"].append({"user_id": user_id,
                                     "question_id": int(user_data["question_id"]),
                                     "title": survey["title"],
                                     "answer": answer})

        if user_data["question_id"] > len(survey["questions"]) - 1:
            survey["answers"] = user_data["answers"]
            print(user_data)
            surveys_table.replace_one({"title": survey["title"]}, survey)

            to_send_text = ""
            users_answers = []
            for answer in survey["answers"]:
                if answer["user_id"] == user_id and answer["title"] == user_data["title"]:
                    users_answers.append(answer)
                    question = survey["questions"][int(answer["question_id"]) - 1]["text"]
                    to_send_text += string_dict(bot)["answer_survey_str_2"].format(question, answer['answer'])
            user_data.clear()
            create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                    callback_data="help_back")]]
            create_markup = InlineKeyboardMarkup(create_buttons)
            bot.send_message(update.message.chat_id,
                             string_dict(bot)["answer_survey_str_3"] + "\n" +
                             string_dict(bot)["answer_survey_str_4"] + "\n" + to_send_text, reply_markup=create_markup)
            del user_data
            del answer
            return ConversationHandler.END

        else:

            question = survey["questions"][int(user_data["question_id"])]["text"]
            bot.send_message(update.message.chat_id, question,
                             reply_markup=reply_markup)
            user_data["last_question"] = question

            return ANSWERING

    def done(self, bot, update, user_data):
        create_buttons = [[InlineKeyboardButton(text=string_dict(bot)["back_button"],
                                                callback_data="help_back")]]
        create_markup = InlineKeyboardMarkup(create_buttons)
        update.message.reply_text(string_dict(bot)["answer_survey_str_3"] + "{}" +
                                  string_dict(bot)["answer_survey_str_4"].format(facts_to_str(user_data)),
                                  reply_markup=create_markup)
        logger.info("User {} on bot {}:{} answered to survey:{}".format(
            update.effective_user.first_name, bot.first_name, bot.id, user_data["title"]))

        user_data.clear()
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

    fallbacks=[
        CallbackQueryHandler(AnswerSurveys().back, pattern=r"help_back"),
    ]
)
