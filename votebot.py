#!/usr/bin/python3

import json

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# load Config
with open("config.json","r") as f:
    config = json.load(f)

######################
# Listener functions #
######################

# Initialise slack

app = App(token=config["SLACK_BOT_TOKEN"])

# Start listening for commands
if __name__ == "__main__":
    SocketModeHandler(app, config["SLACK_APP_TOKEN"]).start()

