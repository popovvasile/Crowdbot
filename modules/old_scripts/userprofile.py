from pymongo import MongoClient
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler)

import logging

# Enable logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)

client = MongoClient('localhost', 27017)
db = client['chatbots']
profile_topics_table = db["profile_topics"]
users_table = db['users']

__mod_name__ = "User profile"

__admin_help__ = """
  -  /userprofile -  complete your user profile 
"""



def return_markup(bot):
    reply_keyboard = []
    for topic in profile_topics_table.find({"bot_id": bot.id}):
        reply_keyboard.append(topic)
    reply_keyboard.append('Something else...').append('Done')
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    return markup


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(bot, update):
    update.message.reply_text(
        "I will hold a more complex conversation with you. "
        "Why don't you tell me something about yourself?",
        reply_markup=return_markup(bot))

    return CHOOSING


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
        'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

    return TYPING_REPLY


def custom_choice(bot, update):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def received_information(bot, update, user_data):
    text = update.message.text
    category = user_data['choice']
    user_data[category] = text
    del user_data['choice']

    update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                              "{}"
                              "You can tell me more, or change your opinion on something.".format(
                                  facts_to_str(user_data)), reply_markup=return_markup(bot))

    return CHOOSING


def done(bot, update, user_data):
    user_id = update.message.from_user.id
    user = users_table.find_one({"user_id": user_id})
    user.update(user_data)
    users_table.update_one({"user_id": user_id}, user)
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("I learned these facts about you:"
                              "{}"
                              "Until next time!".format(facts_to_str(user_data)))

    user_data.clear()
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def USER_PROFILE_HANDLER(dispatcher):
    topics_string_regex = ""
    topic_list = profile_topics_table.find({"bot_id": dispatcher.bot.id})
    for topic in topic_list:
        topics_string_regex += "{}|".format(topic)
    topics_string_regex = topics_string_regex[:-1]

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('my_profile', start)],

        states={
            CHOOSING: [RegexHandler('^({})$'.format(topics_string_regex),
                                    regular_choice,
                                    pass_user_data=True),
                       RegexHandler('^Something else...$',
                                    custom_choice),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice,
                                           pass_user_data=True),
                            ],

            TYPING_REPLY: [MessageHandler(Filters.text,
                                          received_information,
                                          pass_user_data=True),
                           ],
        },

        fallbacks=[CommandHandler('cancel', done, pass_user_data=True)]
    )
    return conv_handler


def set_topics(bot, update):   # TODO ADMIN
    pass
