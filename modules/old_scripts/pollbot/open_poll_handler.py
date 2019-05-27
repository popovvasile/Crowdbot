from .basic_poll_handler import BasicPoll


class OpenPollHandler(BasicPoll):
    def __init__(self):
        super(OpenPollHandler, self).__init__()
        self.name = "Open poll"
        self.desc = "Like basic poll, but you can see who voted for what."

    def evaluation(self, poll):
        message = "This is an open poll. People will see what you voted for.\n"
        for i, option in enumerate(poll['options']):
            message += "\n"
            message += "*{}: {}*".format(option['text'], self.num_votes(poll, i))
            users = self.get_users_voting_for(poll, option)
            for user in users:
                message += "\n "
                message += user
        return message

    def handle_vote(self, votes, user, name, callback_data):
        old_vote = None
        if user in votes:
            old_vote = votes.pop(user)
        if old_vote is not None and str(old_vote['data']) == str(callback_data['i']):
            # remove old vote
            pass
        else:
            votes[user] = {
                'data': callback_data['i'],
                'name': name
            }

    def get_confirmation_message(self, poll, user):
        votes = poll['votes']
        if user in votes:
            vote = votes[user]
            for option in poll['options']:
                if option['index'] == vote['data']:
                    return "You voted for \"{}\".".format(option['text'])
        return "Your vote was removed."

    def num_votes(self, poll, i):
        return [val['data'] for val in poll['votes'].values()].count(i) if 'votes' in poll else 0

    def get_users_voting_for(self, poll, option):
        return [val['name'] for val in poll['votes'].values() if
                val['data'] == option['index']] if 'votes' in poll else []
