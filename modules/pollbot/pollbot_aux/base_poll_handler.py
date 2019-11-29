from helper_funcs.lang_strings.strings import string_dict


class BasePoll(object):
    def __init__(self):
        self.max_options = 10
        self.name = "Unconfigured Poll Type"
        self.desc = "Poll type description goes here."

    def options(self, poll):
        buttons = [[]]
        return buttons

    def title(self, poll):
        return "*{}*".format(poll['title'])

    def evaluation(self, poll):
        return "Somebody messed up! This poll type is not configured."

    def handle_vote(self, votes, user, name, callback_data):
        pass

    def get_confirmation_message(self, poll, user):
        return "Nothing happened."

    def requires_extra_config(self, meta):
        return False

    def ask_for_extra_config(self, meta, update):
        return string_dict(context)["ask_for_extra_config_wrong"]

    def register_extra_config(self, text, meta):
        pass
