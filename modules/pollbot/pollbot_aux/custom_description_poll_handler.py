from helper_funcs.lang_strings.strings import string_dict
from .basic_poll_handler import BasicPoll


class CustomDescriptionHandler(BasicPoll):
    def __init__(self):
        super(CustomDescriptionHandler, self).__init__()
        self.name = "Basic poll"
        self.desc = "Basic poll"

    def evaluation(self, poll):
        message = ""
        for i, option in enumerate(poll['options']):
            message += "\n"
            message += "{}: {}".format(option['text'], self.num_votes(poll, i))
        return message

    def ask_for_extra_config(self, meta, update):
        return string_dict(context)["ask_for_extra_config"]

    def register_extra_config(self, text, meta):
        meta['text'] = text

    def num_votes(self, poll, i):
        return list(poll['votes'].values()).count(i) if 'votes' in poll else 0

    def requires_extra_config(self, meta):
        return False
