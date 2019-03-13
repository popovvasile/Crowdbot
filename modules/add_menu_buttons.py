from telegram import ReplyKeyboardMarkup
from telegram.ext import (CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
import logging
# Enable logging
from database import custom_buttons_table
from modules.helper_funcs.auth import initiate_chat_id
from modules.helper_funcs.restart_program import restart_program

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
TYPING_BUTTON, TYPING_DESCRIPTION, FINISH = range(3)
TYPING_TO_DELETE_BUTTON = 1
__mod_name__ = "Custom buttons"

__admin_keyboard__ = [["/create_button"], ["/delete_button"]]

__admin_help__ = """
 - /create_button - to create a custom button for your bot
 - /delete_button -  delete a button with a specific name\n

"""  # TODO current_buttons and delete


class AddCommands(object):
    def start(self, bot, update):
        reply_keyboard = [['Rules', 'Contacts'],
                          ['Useful links', 'Something else...'],
                          ['Done']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text(
            "Please type your new button, for example 'Contacts' or 'Rules'. Please note that"
            "you can't modify the buttons available by default ", reply_keyboard=markup)
        return TYPING_BUTTON

    def button_handler(self, bot, update, user_data):
        chat_id, txt = initiate_chat_id(update)
        user_data['button'] = txt
        update.message.reply_text('Excellent! Now, please send me the description of your new button')
        return TYPING_DESCRIPTION

    def description_handler(self, bot, update, user_data):
        user_id = update.message.from_user.id
        chat_id, txt = initiate_chat_id(update)
        custom_buttons_table.save({"button": user_data['button'],
                                   "description": txt,
                                   "button_lower": user_data['button'].replace(" ", "").lower(),
                                   "admin_id": user_id,
                                   "chat_id": chat_id,
                                   "bot_id": bot.id})
        update.message.reply_text(
            'Thank you! Now your button will be accessible by typing or clicking \n'
            '{}:{}'.format(user_data["button"], txt))
        restart_program()
        return ConversationHandler.END

    def cancel(self, bot, update):
        user = update.message.from_user
        logger.info("User %s canceled the conversation.", user.first_name)
        update.message.reply_text('Bye! I hope we can talk again some day.')

        return ConversationHandler.END

    def error(self, bot, update, error):
        """Log Errors caused by Updates."""
        logger.warning('Update "%s" caused error "%s"', update, error)

    def delete_button(self, bot, update):
        chat_id, txt = initiate_chat_id(update)

        button_list_of_dicts = custom_buttons_table.find({
            "chat_id": chat_id,
            "bot_id": bot.id})
        button_list = [button['button'] for button in button_list_of_dicts]
        reply_keyboard = [button_list]
        update.message.reply_text(
            "Please choose the button that button that you want to delete",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
        return TYPING_TO_DELETE_BUTTON  # TODO make it with buttons

    def delete_button_finish(self, bot, update):
        chat_id, txt = initiate_chat_id(update)
        custom_buttons_table.delete_one({
            "button": txt,
            "chat_id": chat_id,
            "bot_id": bot.id
        })
        update.message.reply_text(
            'Thank you! We deleted the button {}'.format(txt))
        restart_program()
        return ConversationHandler.END


# Get the dispatcher to register handlers


# Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
BUTTON_ADD_HANDLER = ConversationHandler(
    entry_points=[CommandHandler('create_button', AddCommands().start)],

    states={
        TYPING_BUTTON: [MessageHandler(Filters.text,
                                       AddCommands().button_handler, pass_user_data=True)],
        TYPING_DESCRIPTION: [MessageHandler(Filters.text,
                                            AddCommands().description_handler, pass_user_data=True)]
    },

    fallbacks=[CommandHandler('cancel', AddCommands().cancel),
               MessageHandler(filters=Filters.command, callback=AddCommands().cancel)]
)
DELETE_BUTTON_HANDLER = ConversationHandler(
    entry_points=[CommandHandler("delete_button", AddCommands().delete_button)],

    states={
        TYPING_TO_DELETE_BUTTON: [MessageHandler(Filters.text,
                                                 AddCommands().delete_button_finish)],
    },

    fallbacks=[CommandHandler('cancel', AddCommands().cancel),
               MessageHandler(filters=Filters.command, callback=AddCommands().cancel)]
)
