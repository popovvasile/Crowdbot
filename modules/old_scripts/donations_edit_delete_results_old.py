# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import uuid  # todo remake all functions to return END and user user_data[key] user_data[value]
from dropbox.files import WriteMode
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters, ConversationHandler, RegexHandler, run_async,
                          CallbackQueryHandler)
import logging
import datetime
from database import donations_table, users_table, chats_table, chatbots_table, DROPBOX_TOKEN, donations_table
from modules.helper_funcs.auth import initiate_chat_id, if_admin
import csv
import dropbox

# Enable logging
from modules.helper_funcs.helper import get_help

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START, CHOOSING_ACTION, FINISH_ACTION, EDIT_PAYMENT, CHOOSING_EDIT_ACTION, RESULTS, \
TYPING_TITLE, TYPING_DESCRIPTION, TYPING_AMOUNT, TYPING_CURRENCY, \
TYPING_TAGS, TYPING_TYPE, TYPING_DEADLINE, TYPING_REPEAT, \
TYPING_TOKEN, TYPING_TOKEN_FINISH, EDIT_FINISH, DOUBLE_CHECK_DELETE, DELETE_FINISH = range(19)


class EditPaymentHandler(object):
    def __init__(self):
        buttons = list()
        buttons.append([InlineKeyboardButton(text="Back", callback_data="cancel_donation_edit")])
        self.reply_markup = InlineKeyboardMarkup(
            buttons)

    @staticmethod
    def facts_to_str(user_data):
        facts = list()
        for key, value in user_data.items():
            facts.append('{} - {}'.format(key, value))

        return "\n".join(facts).join(['\n', '\n'])

    @run_async
    def start_donation(self, bot, update, user_data):
        command_list = [donation['title'] for donation in donations_table.find({"bot_id": bot.id})]
        reply_keyboard = [list(set(command_list))]
        update.message.reply_text(
            "Please choose one of your donation requests",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return CHOOSING_ACTION

    @run_async
    def handle_donation(self, bot, update, user_data):  # TODO check if the title is from keyboard
        chat_id, txt = initiate_chat_id(update)
        user_data["title"] = txt
        reply_keyboard = [["See the results"], ["Delete this donation"], ["Edit"]]
        update.message.reply_text(
            "What do you want to do with this donation?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

        return FINISH_ACTION

    def handle_action_finish(self, bot, update, user_data):  # TODO add if leifs for every action
        chat_id, txt = initiate_chat_id(update)
        if txt == "See the results":
            user_data['action'] = txt
            return RESULTS
        elif txt == "Delete this donation":
            user_data['action'] = txt
            return DOUBLE_CHECK_DELETE
        elif txt == "Edit":
            user_data['action'] = txt
            return EDIT_PAYMENT

    @run_async
    def handle_edit_action(self, bot, update, user_data):
        keyboard_markup = [["Title", "Description"],
                           ["Price", "Currency", "Tags"],
                           ["Type of donation", "Repeat frequency"]]
        chat_id, txt = initiate_chat_id(update)
        bot.send_message(chat_id, "Choose what exactly do you want to edit",
                         reply_markup=ReplyKeyboardMarkup(keyboard_markup))
        return CHOOSING_EDIT_ACTION

    def handle_edit_action_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['edit_action'] = txt
        # if txt == "Deadline":
        #     bot.send_message(chat_id,
        #                      "Enter a deadline for this donation, in the following format: dd.mm.yyyy")
        #     return TYPING_DEADLINE
        if txt == "Title":
            bot.send_message(chat_id,
                             "Please write a new title for this donation")
            return TYPING_TITLE
        elif txt == "Description":
            update.message.reply_text("Write a short text for your donation- what your users have to pay for?")
            return TYPING_DESCRIPTION
        elif txt == "Price":
            update.message.reply_text("Enter a floating number in following format: 10.50")
            return TYPING_AMOUNT
        elif txt == "Currency":
            currency_keyboard = [["RUB", "USD", "EUR", "GBP"], ["CHF", "AUD", "RON", "PLN"]]
            update.message.reply_text("Choose the currency of your donation",
                                      reply_markup=ReplyKeyboardMarkup(currency_keyboard, one_time_keyboard=True))
            return TYPING_CURRENCY
        elif txt == "Tags":
            tags_names = []
            for chat in chats_table.find({"bot_id": bot.id}):
                if chat["tag"] in tags_names:
                    pass
                else:
                    tags_names.append(chat["tag"])
            tags_names = [["Ready"] + list(set(tags_names))]
            bot.send_message(chat_id, "Send me the tags of the users that have to pay this donation. \n"
                                      "Click on one of the tags or click Ready to proceed to the next step",
                             reply_markup=ReplyKeyboardMarkup(tags_names))
            user_data['tags'] = []
            return TYPING_TAGS

        elif txt == "Type of donation":
            reply_keyboard = [["Crowdfunding"], ["Fee"]]
            bot.send_message(chat_id,
                             "Choose the type of your donation request: is it a donation,"
                             "a membership fee or a crowdfunding campaign?",
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard))
            return TYPING_TYPE
        elif txt == "Repeat frequency":
            reply_keyboard = [["Once a month", "Once in 6 months"], ["Never"]]
            bot.send_message(chat_id,
                             "Please choose how often should I request the donations from your users",
                             reply_markup=ReplyKeyboardMarkup(reply_keyboard))
            return TYPING_REPEAT

    @run_async
    def handle_title(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['title'] = txt
        return EDIT_FINISH

    @run_async
    def handle_description(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data["description"] = txt

        return EDIT_FINISH

    @run_async
    def handle_amount(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        amount_str = txt
        try:
            amount = float(amount_str)
        except ValueError:
            update.message.reply_text("Wrong format. Please enter a floating number in following format: 10.50")
            return TYPING_AMOUNT
        user_data["amount"] = amount
        return EDIT_FINISH

    @run_async
    def handle_currency(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        currency = txt
        user_data["currency"] = currency

        return EDIT_FINISH

    @run_async
    def handle_tags(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if txt == "Ready":
            return EDIT_FINISH
        else:
            user_data['tags'].append(txt)
            bot.send_message(chat_id, txt)

            tags_names = []
            for chat in chats_table.find({"bot_id": bot.id}):
                if chat["tag"] in tags_names:
                    pass
                else:
                    tags_names.append(chat["tag"])
            tags_names = [["Ready"] + list(set(tags_names))]
            bot.send_message(chat_id, "", reply_markup=ReplyKeyboardMarkup(tags_names))
            return TYPING_TAGS

    @run_async
    def handle_type(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['donation_type'] = txt

        return EDIT_FINISH

    @run_async
    def handle_repeat(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['repeat_type'] = txt
        return TYPING_DEADLINE

    #
    # @run_async
    # def handle_deadline(self, bot, update, user_data):
    #     chat_id, txt = initiate_chat_id(update)
    #     try:
    #         deadline = datetime.datetime.strptime(txt, '%d.%m.%Y')
    #     except ValueError:
    #         update.message.reply_text("Please enter the correct format for the deadline: dd.mm.yyyy")
    #         return TYPING_DEADLINE
    #
    #     user_data['deadline'] = deadline

    @run_async
    def handle_edit_finish(self, bot, update, user_data): # TODO double check
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        chatbot["donation"] = user_data
        chatbots_table.replace_one({"bot_id": bot.id}, chatbot)
        update.message.reply_text("Your donation has been updated")

        user_data.clear()
        return ConversationHandler.END

    @run_async
    def handle_delete_double_check(self, bot, update, user_data):
        reply_keyboard = [["Yes, I am sure"], ["No, let's get back"]]
        update.message.reply_text(
            "Are you sure that you want to delete this donation?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return DELETE_FINISH

    @run_async
    def handle_finish_delete(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        if txt == "Yes, I am sure":
            user_data['action'] = "delete"
            return ConversationHandler.END
        elif txt == "No, let's get back":
            return CHOOSING_ACTION

    @run_async
    def show_donation_results_finish(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        title = user_data['title']
        txt_to_send = ""
        filename = "{}_{}_{}.csv".format(update.message.from_user.id, chat_id, title)
        file = csv.writer(open(filename, "wb+"))

        for donation in donations_table.find({"user_id": update.message.from_user.id,
                                              "bot_id": bot.id,
                                              "title": title}):
            full_name = users_table.find_one({"user_id": donation['user_id']})["full_name"]
            txt_to_send += 'Users full name: {},\nPayment title:{} \nPayment status:{},'.format(
                full_name,
                donation["title"],
                donation['paid_status'],
            )
        client = dropbox.Dropbox(DROPBOX_TOKEN)
        response = client.files_upload(file.read(), filename, mode=WriteMode("overwrite"))
        print('uploaded: ', response)
        link = client.sharing_create_shared_link_with_settings(filename).url
        update.message.reply_text("This is the link to the result spreadsheet:{}\n"
                                  "Here is your requested data : \n {}".format(link, txt_to_send))
        return ConversationHandler.END

    @run_async
    def change_donation_token(self, bot, update):

        update.message.reply_text(
            "Please enter your new donation provider token"
        )
        return TYPING_TOKEN

    @run_async
    def change_donation_token_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        chatbot = chatbots_table.find_one({"bot_id": bot.id})
        chatbots_table.update_one(chatbot, chatbot.update({"donation_token": txt}))
        update.message.reply_text("Thank you! Your provider_token was changed successfully !")
        # TODO check if token is valid
        return ConversationHandler.END

    @staticmethod
    def error(bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def cancel(self, bot, update):
        get_help(bot, update)
        return ConversationHandler.END


# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY'

CREATE_PAYMENT_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('edit_donation', EditPaymentHandler().start_donation, pass_user_data=True)],

    states={
        TYPING_TOKEN: [MessageHandler(Filters.text,
                                      EditPaymentHandler().change_donation_token,
                                      pass_user_data=True),
                       CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_TOKEN_FINISH: [MessageHandler(Filters.text,
                                             EditPaymentHandler().change_donation_token_finish,
                                             pass_user_data=True),
                              CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_TITLE: [MessageHandler(Filters.text,
                                      EditPaymentHandler().handle_title,
                                      pass_user_data=True),
                       CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.text,
                                            EditPaymentHandler().handle_description,
                                            pass_user_data=True),
                             CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_AMOUNT: [MessageHandler(Filters.text,
                                       EditPaymentHandler().handle_amount,
                                       pass_user_data=True),
                        CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_CURRENCY: [MessageHandler(Filters.text,
                                         EditPaymentHandler().handle_currency,
                                         pass_user_data=True),
                          CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_TAGS: [MessageHandler(Filters.text,
                                     EditPaymentHandler().handle_tags,
                                     pass_user_data=True),
                      CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_TYPE: [MessageHandler(Filters.text,
                                     EditPaymentHandler().handle_type,
                                     pass_user_data=True),
                      CommandHandler('cancel', EditPaymentHandler().cancel)],
        TYPING_REPEAT: [MessageHandler(Filters.text,
                                       EditPaymentHandler().handle_repeat,
                                       pass_user_data=True),
                        CommandHandler('cancel', EditPaymentHandler().cancel)],
        # TYPING_DEADLINE: [MessageHandler(Filters.text,
        #                                  EditPaymentHandler().handle_deadline,
        #                                  pass_user_data=True),
        #                   CommandHandler('cancel', EditPaymentHandler().cancel)],
        DOUBLE_CHECK_DELETE: [MessageHandler(Filters.text,
                                             EditPaymentHandler().handle_delete_double_check,
                                             pass_user_data=True),
                              CommandHandler('cancel', EditPaymentHandler().cancel)],
        RESULTS: [MessageHandler(Filters.text,
                                 EditPaymentHandler().show_donation_results_finish,
                                 pass_user_data=True),
                  CommandHandler('cancel', EditPaymentHandler().cancel)],
    },

    fallbacks=[
        CallbackQueryHandler(callback=EditPaymentHandler().cancel, pattern=r"cancel_donation_edit"),
        MessageHandler(filters=Filters.command, callback=EditPaymentHandler().cancel)]
)
