import os

os.environ.get("CHATBOT_TOKEN")

conf = dict(
    # Number of reports on one page
    PER_PAGE=5,
    # TOKEN="836123673:AAE6AyfFCcRxjHZZhJHtdE8mKt8WNfgRm5Q",  # @crowd_supportbot
    # TOKEN="892372248:AAEM32Ye0ye4rTkyTuk5Z4minhsNKVhSQ-w",  # @CrowdRobot  CrowdBot
    TOKEN=os.environ.get("CHATBOT_TOKEN")
)
