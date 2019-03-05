from .open_poll_handler import OpenPollHandler
from .custom_description_poll_handler import CustomDescriptionHandler


class CustomDescriptionOpenPollHandler(OpenPollHandler, CustomDescriptionHandler):
    def __init__(self):
        super(CustomDescriptionOpenPollHandler, self).__init__()
        self.name = "Open poll with custom description"
        self.desc = "Like open poll, but lets you add a custom text to the poll message."

    def evaluation(self, poll):
        message = poll['meta']['text']
        message += "\n"
        for i, option in enumerate(poll['options']):
            message += "\n"
            message += "*{}: {}*".format(option['text'], self.num_votes(poll, i))
            users = self.get_users_voting_for(poll, option)
            for user in users:
                message += "\n "
                message += user
        return message
