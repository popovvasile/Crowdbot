from .instant_runoff_poll_handler import InstantRunoffPollHandler
from .custom_description_poll_handler import CustomDescriptionHandler


class CustomDescriptionInstantRunoffPollHandler(InstantRunoffPollHandler, CustomDescriptionHandler):
    def __init__(self):
        super(CustomDescriptionInstantRunoffPollHandler, self).__init__()
        self.name = "Order of preference with description"
        self.desc = "Like order of preference poll, but with a custom description"

    def evaluation(self, poll):
        votes = poll.get('votes', {})
        candidates = [opt['index'] for opt in poll['options']]

        explanation = "Order of preference"

        if votes:
            elected = self.run_election(candidates, list(votes.values()))

            elected_names = [self.get_option_name_by_index(poll, el) for el in elected]
            message = "{}: {}".format(
                "Current winner" if len(elected_names) == 1 else "We have a tie",
                ",".join(elected_names)
            )
        else:
            message = "There are currently no votes."

        num_votes = len(poll.get('votes', {}))
        body = poll['meta']['text']
        body += "\n\n{}\n\n*{}*\n{} people voted so far".format(explanation, message, num_votes)
        return body

