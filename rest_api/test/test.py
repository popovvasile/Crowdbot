from pprint import pprint
import requests
from telegram.ext import Updater, CommandHandler, ConversationHandler


def test_conflict():
    def start(update, context):
        context.bot.send_message(update.effective_chat.id, "Hello")
        return ConversationHandler.END

    updater = Updater('1266487119:AAG_0q4p6TiW70ykWuikEO8hRGGOXxUMzlc', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", callback=start))

    updater.start_polling()
    updater.idle()


def test():
    resp = requests.get(
        "http://localhost:8000/crowdbot",
        json={"API_KEY": "1aa189ce-9a96-4b5d-9c23-d39e49175e21"
                         "-7a01f777-a969-4d2a-a3f5-4d5c92913286",
              "bot_id": 1213897606})
    pprint(resp.json())
    pprint(resp.status_code)


if __name__ == "__main__":
    # test()
    test_conflict()
