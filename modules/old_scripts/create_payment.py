# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import uuid
from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, run_async)
import logging
import datetime
from database import payments_requests_table, chats_table, chatbots_table, payments_table
from modules.helper_funcs.auth import initiate_chat_id

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

TYPING_TOKEN, TYPING_TITLE, TYPING_DESCRIPTION, TYPING_AMOUNT, TYPING_CURRENCY, \
    TYPING_TAGS, TYPING_TAGS_FINISH, TYPING_TYPE, TYPING_DEADLINE, TYPING_REPEAT = range(10)
CHOOSING_PAYMENT = 1
CHOOSING_ACTION, FINISHING_ACTION, DOUBLE_CHECK_DELETE, EDIT_PAYMENT, FINISH_DELETE, FINISH_EDIT = range(6)


class CreatePaymentHandler(object):
    @staticmethod
    def facts_to_str(user_data):
        facts = list()

        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @run_async
    def start_create_payment(self, bot, update, user_data):
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        if "payment_token" in chatbot:
            update.message.reply_text("Please enter a title for your payment.\n"
                                      "If you want to change your payment provider token, "
                                      "please click /change_payment_token")
            return TYPING_TITLE
        else:
            update.message.reply_text("Please enter your payment provider token"
                                      "In order to get it,"
                                      "please visit https://core.telegram.org/bots/payments#getting-a-token")
            return TYPING_TOKEN

    @run_async
    def handle_token(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        if not "payment_token" in chatbot:
            user_data['payment_token'] = txt
        update.message.reply_text("Enter a title for your payment")
        return TYPING_TITLE

    @run_async
    def handle_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['title'] = txt
        update.message.reply_text("Write a short text for your payment- what your users have to pay for?")
        return TYPING_DESCRIPTION

    @run_async
    def handle_description(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["description"] = txt
        tags_names = []
        for chat in chats_table.find({"bot_id": bot.id}):
            if chat["tag"] in tags_names:
                pass
            else:
                tags_names.append(chat["tag"])
        tags_names = [["Ready"] + list(set(tags_names))]
        bot.send_message(chat_id, "Type a floating point amount for your payment. Like this: 10.50"
                         ,
                         reply_markup=ReplyKeyboardMarkup(tags_names))
        user_data['tags'] = []
        return TYPING_AMOUNT

    @run_async
    def handle_amount(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        amount_str = txt
        try:
            amount = float(amount_str)
        except ValueError:
            update.message.reply_text("Please enter a floating number in following format: 10.50")
            return TYPING_AMOUNT
        user_data["amount"] = amount
        currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
        update.message.reply_text("Now, choose the currency of your payment",
                                  reply_markup=ReplyKeyboardMarkup(currency_keyboard, one_time_keyboard=True))
        return TYPING_CURRENCY

    @run_async
    def handle_currency(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        currency = txt
        user_data["currency"] = currency
        tags_names = []
        for chat in chats_table.find({"bot_id": bot.id}):
            if chat["tag"] in tags_names:
                pass
            else:
                tags_names.append(chat["tag"])
        tags_names = [["Ready"] + list(set(tags_names))]
        bot.send_message(chat_id, "Send me the tags of the users that have to pay this payment. \n"
                                  "Click on one of the tags or click Ready to proceed to the next step",
                         reply_markup=ReplyKeyboardMarkup(tags_names))
        user_data['tags'] = []
        bot.send_message(chat_id, )

        return TYPING_TAGS

    @run_async
    def handle_tags(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if txt == "Ready":
            return TYPING_TAGS_FINISH
        else:
            user_data['tags'].append(txt)
            bot.send_message(chat_id, txt)
            return TYPING_TAGS

    @run_async
    def handle_tags_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)

        reply_keyboard = [["Donation", "Membership fee"], ["Crowdfunding"]]
        bot.send_message(chat_id,
                         "Please choose the type of your payment request: is it a donation,"
                         "a membership fee or a crowdfunding campaign?",
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard))
        return TYPING_TYPE

    @run_async
    def handle_type(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['payment_type'] = txt
        reply_keyboard = [["Once a month", "Once in 6 months"], ["Never"]]
        bot.send_message(chat_id,
                         "Please choose how often should I request the payments from your users",
                         reply_markup=ReplyKeyboardMarkup(reply_keyboard))

        return TYPING_REPEAT

    @run_async
    def handle_repeat(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['repeat_type'] = txt
        bot.send_message(chat_id,
                         "Please enter a deadline for this payment, in the following format: dd.mm.yyyy")

    #     return TYPING_DEADLINE
    #
    # @run_async
    # def handle_deadline(self, bot, update, user_data):
    #     chat_id, txt = initiate_chat_id(update)
    #     try:
    #         deadline = datetime.datetime.strptime(txt, '%d.%m.%Y')
    #     except ValueError:
    #         update.message.reply_text("Please enter the correct format for the deadline: dd.mm.yyyy")
    #         return TYPING_DEADLINE
    #     user_data['deadline'] = deadline

        user_data['payment_request_id'] = uuid.uuid4().hex.upper()
        send_tags = user_data['tags']
        payment_title = user_data['title']
        approved = []
        rejected = []
        sent = []
        for tag_name in send_tags:
            tags = chats_table.find({"tag": tag_name})
            for tag in tags:
                if tag['chat_id'] != chat_id:
                    if not any(sent_d['id'] == tag['chat_id'] for sent_d in sent):
                        sent.append(tag['chat_id'])
                        approved.append(tag['name'])
                        bot.send_message(tag['chat_id'], "Dear user, a payment has been sent to you. "
                                                         "Please type /execute_payment_{} to start the payment".
                                         format(payment_title))
                        payments_table.insert(user_data.update({"bot_id": bot.id,
                                                                "user_id": tag['user_id'],
                                                                "paid_status": False,
                                                                }))
                else:
                    rejected.append(tag)
        if len(rejected) > 0:
            bot.send_message(chat_id,
                             "Failed to send messages to tags <i>" + ", ".join(rejected) + "</i>",
                             parse_mode="HTML")
        update.message.reply_text("We sent a request to your users to pay this bill\n"
                                  "Until next time!".format(user_data['title']))
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        if 'payment_token' in user_data:
            chatbots_table.update_one(chatbot, chatbot.update({"payment_token": user_data['token']}))
        user_data.pop('user_id', None)
        user_data.pop('status', None)

        payments_requests_table.save(user_data)
        user_data.clear()
        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def cancel(self, bot, update):
        update.message.reply_text("Command is finished. Until next time!")
        return ConversationHandler.END


# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY'


CREATE_PAYMENT_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('create_payment', CreatePaymentHandler().start_create_payment, pass_user_data=True)],
    # TYPING_TOKEN, TYPING_TITLE,  TYPING_DESCRIPTION, TYPING_AMOUNT, TYPING_CURRENCY,\
    # TYPING_TAGS, TYPING_TAGS_FINISH, TYPING_TYPE, TYPING_DEADLINE, TYPING_REPEAT
    states={
        TYPING_TOKEN: [MessageHandler(Filters.text,
                                      CreatePaymentHandler().handle_token,
                                      pass_user_data=True),
                       CommandHandler('cancel', CreatePaymentHandler().cancel)],
        TYPING_TITLE: [MessageHandler(Filters.text,
                                      CreatePaymentHandler().handle_title,
                                      pass_user_data=True),
                       CommandHandler('cancel', CreatePaymentHandler().cancel)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.text,
                                            CreatePaymentHandler().handle_description,
                                            pass_user_data=True),
                             CommandHandler('cancel', CreatePaymentHandler().cancel)],
        TYPING_AMOUNT: [MessageHandler(Filters.text,
                                       CreatePaymentHandler().handle_amount,
                                       pass_user_data=True),
                        CommandHandler('cancel', CreatePaymentHandler().cancel)],
        TYPING_CURRENCY: [MessageHandler(Filters.text,
                                         CreatePaymentHandler().handle_currency,
                                         pass_user_data=True),
                          CommandHandler('cancel', CreatePaymentHandler().cancel)],
        TYPING_TAGS: [MessageHandler(Filters.text,
                                     CreatePaymentHandler().handle_tags,
                                     pass_user_data=True),
                      CommandHandler('cancel', CreatePaymentHandler().cancel)],
        TYPING_TAGS_FINISH: [MessageHandler(Filters.text,
                                            CreatePaymentHandler().handle_tags_finish,
                                            pass_user_data=True),
                             CommandHandler('cancel', CreatePaymentHandler().cancel)],
        TYPING_TYPE: [MessageHandler(Filters.text,
                                     CreatePaymentHandler().handle_type,
                                     pass_user_data=True),
                      CommandHandler('cancel', CreatePaymentHandler().cancel)],
        TYPING_REPEAT: [MessageHandler(Filters.text,
                                       CreatePaymentHandler().handle_repeat,
                                       pass_user_data=True),
                        CommandHandler('cancel', CreatePaymentHandler().cancel)],
        # TYPING_DEADLINE: [MessageHandler(Filters.text,
        #                                  CreatePaymentHandler().handle_deadline,
        #                                  pass_user_data=True),
        #                   CommandHandler('cancel', CreatePaymentHandler().cancel)],

    },

    fallbacks=[
        MessageHandler(filters=Filters.command, callback=CreatePaymentHandler().cancel)]
)
