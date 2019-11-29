from requests.exceptions import ConnectionError, RequestException
from modules.shop.helper.strings import strings
from modules.shop.modules.welcome import Welcome
from modules.shop.helper.helper import clear_user_data
from telegram.error import TimedOut


def catch_request_exception(func):
    def wrapper(self, update, context):
        try:
            return func(self, update, context)
        except ConnectionError:
            clear_user_data(context)
            context.context.user_data["msg_to_send"] = strings["api_off"]
            return Welcome().start(update, context)
        except RequestException:
            clear_user_data(context)
            context.context.user_data["msg_to_send"] = strings["something_gone_wrong"]
        except TimedOut:
            clear_user_data(context)
            context.context.user_data["msg_to_send"] = strings["timed_out"]
            return Welcome().start(update, context)
    return wrapper


def append_to_delete(func):
    def wrapper():
        func()
    return wrapper
