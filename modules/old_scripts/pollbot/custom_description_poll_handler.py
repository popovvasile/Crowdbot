from .basic_poll_handler import BasicPoll


class CustomDescriptionHandler(BasicPoll):
    def __init__(self):
        super(CustomDescriptionHandler, self).__init__()
        self.name = "Basic poll with custom description"
        self.desc = "Like basic poll, but lets you add a custom text to the poll message."

    def evaluation(self, poll):
        message = poll['meta']['text']
        message += "\n"
        for i, option in enumerate(poll['options']):
            message += "\n"
            message += "{}: {}".format(option['text'], self.num_votes(poll, i))
        return message

    def ask_for_extra_config(self, meta):
        return "Please enter the text to be displayed above your poll:"

    def register_extra_config(self, text, meta):
        meta['text'] = text

    def num_votes(self, poll, i):
        return list(poll['votes'].values()).count(i) if 'votes' in poll else 0

    def requires_extra_config(self, meta):
        return 'text' not in meta
