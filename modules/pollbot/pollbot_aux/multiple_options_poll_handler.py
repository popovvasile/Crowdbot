from .basic_poll_handler import BasicPoll


class MultipleOptionsHandler(BasicPoll):
    def __init__(self):
        super(MultipleOptionsHandler, self).__init__()
        self.name = "Multiple options poll"
        self.desc = "Lets you vote for multiple options"

    def options(self, poll):
        buttons = [[{
            'text': "Clear my votes",
            'callback_data': {'i': "C"}
        }]]
        for opt in poll['options']:
            votes = self.num_votes_on_option(poll, opt['index'])
            buttons.append([{
                'text': "{}{}{}".format(opt['text'],
                                        " : " if votes > 0 else "",
                                        votes if votes > 0 else ""),
                'callback_data': {'i': opt['index']}
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
        if old_vote is not None and callback_data['i'] in old_vote:
            old_vote.remove(callback_data['i'])
            if old_vote:
                votes[user] = old_vote
        elif old_vote is not None:
            old_vote.append(callback_data['i'])
            votes[user] = old_vote
        else:
            votes[user] = [callback_data['i']]
        if callback_data['i'] == 'C':
            votes.pop(user, None)

    def get_confirmation_message(self, poll, user):
        votes = poll['votes']
        if user in votes:
            vote = votes[user]
            opts = poll['options']
            vote_set = [opt['text'] for opt in opts if opt['index'] in vote]
            string = ",".join(vote_set) if vote_set else "nothing"
            return "You voted for {}.".format(string)
        return "Your vote was removed."

    def num_votes_on_option(self, poll, index):
        if 'votes' not in poll:
            return 0
        votes = poll['votes']

        num = 0
        for cast_vote in votes.values():
            if index in cast_vote:
                num += 1
        return num