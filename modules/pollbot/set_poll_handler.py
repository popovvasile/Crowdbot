from functools import reduce
from .base_poll_handler import BasePoll


class SetPollHandler(BasePoll):
    def __init__(self):
        super(SetPollHandler, self).__init__()
        self.max_options = 4

        self.name = "Subset poll"
        self.desc = "Lets you vote for any subset of the available options"

    def options(self, poll):
        buttons = []
        set_opts = self.get_subsets_of(poll['options'])

        for set_opt in set_opts:
            index_set = [opt['index'] for opt in set_opt]
            title_set = [opt['text'] for opt in set_opt]
            votes = self.num_votes_on_set(poll, index_set)
            buttons.append([{
                'text': "{}{}{}".format(self.get_set_opt_text(title_set),
                                        " - " if votes > 0 else "",
                                        votes if votes > 0 else ""),
                'callback_data': {'i': index_set}
            }])
        return buttons

    def evaluation(self, poll):
        message = ""
        for option in poll['options']:
            message += "\n"
            message += "{}: {}".format(option['text'], self.num_votes_on_option(poll, option['index']))
        return message

    def handle_vote(self, votes, user, name, callback_data):
        old_vote = None
        if user in votes:
            old_vote = votes.pop(user)
        if old_vote is not None and old_vote == callback_data['i']:
            # remove old vote
            pass
        else:
            votes[user] = callback_data['i']

    def get_confirmation_message(self, poll, user):
        votes = poll['votes']
        if user in votes:
            vote = votes[user]
            opts = poll['options']
            vote_set = [opt['text'] for opt in opts if opt['index'] in vote]
            string = ",".join(vote_set) if vote_set else "nothing"
            return "You voted for {}.".format(vote)
        return "Your vote was removed."

    def get_set_opt_text(self, title_set):
        return ','.join(title_set) if title_set else "None"

    def num_votes_on_option(self, poll, index):
        if 'votes' not in poll:
            return 0
        votes = poll['votes']

        num = 0
        for cast_vote in votes.values():
            if index in cast_vote:
                num += 1
        return num

    def num_votes_on_set(self, poll, index_set):
        if 'votes' not in poll:
            return 0
        votes = poll['votes']

        num = 0
        for cast_vote in votes.values():
            if cast_vote == index_set:
                num += 1
        return num

    def get_subsets_of(self, some_set):
        return reduce(lambda z, x: z + [y + [x] for y in z], some_set, [[]])
