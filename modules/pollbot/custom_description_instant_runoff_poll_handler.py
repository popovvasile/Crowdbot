import ast

from .instant_runoff_poll_handler import InstantRunoffPollHandler
from .custom_description_poll_handler import CustomDescriptionHandler


class CustomDescriptionInstantRunoffPollHandler(CustomDescriptionHandler, InstantRunoffPollHandler):
    def __init__(self):
        super(CustomDescriptionInstantRunoffPollHandler, self).__init__()
        self.name = "Order of preference with custom description"
        self.desc = "Order of preference with custom description"

    def evaluation(self, poll):
        print(poll)
        votes = poll.get('votes', {})
        if type(poll["options"]) is str:
            poll["options"] = ast.literal_eval(poll["options"])
        if type(poll["meta"]) is str:
            poll["meta"] = ast.literal_eval(poll["meta"])
        if type(votes) is str:
            votes = ast.literal_eval(votes)
        candidates = [opt['index'] for opt in poll['options']]

        explanation = "Click on only those options that work for you, in the order of your preference."

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

