#!/usr/bin/python3

import json
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slackblocks import Button, SectionBlock, Message, HeaderBlock, DividerBlock, Modal

import util.users

# Initialise slack
with open("config.json", "r") as f:
    config = json.load(f)

app = App(token=config["SLACK_BOT_TOKEN"])


@app.command("/newvote")
def handle_newvote(ack, body, logger):
    ack()

    blocks = []

    blocks.append(SectionBlock(text="Hello"))

    my_modal = Modal(title="My first modal", close="Cancel", submit="Submit", blocks=blocks)

    app.client.views_open(trigger_id=body["trigger_id"], view=my_modal.json())

    print("Stuff happened!")
    pass


# Listens to incoming messages that contain "hello"
# To learn available listener method arguments,
# visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
@app.message("list_users")
def message_list_users(message, say):
    channel = message["channel"]
    users = util.users.get_users_in_channel(channel)

    all_users = "\n".join([u_real_name for u_id, u_real_name in users])
    msg_text = f"Hello to:\n{all_users}"

    my_button = Button(text="Foo", action_id="Foo_action", url=None, value=None, style=None, confirm=None)
    my_header = HeaderBlock(text="Foo Header", block_id=None)
    my_divider = DividerBlock(block_id=None)
    my_section = SectionBlock(text=msg_text, block_id=None, fields=None, accessory=my_button)

    my_message = Message(channel=message["channel"], text="No text?", blocks=[my_header, my_divider, my_section])

    # say() sends a message to the channel where the event was triggered
    say(**my_message)


@app.action("button_click")
def action_button_click(body, ack, say):
    # Acknowledge the action
    ack()
    say(f"<@{body['user']['id']}> confused the sheep")


# Listen for a shortcut invocation
@app.action("open_modal")
def open_modal(body, ack, say):
    client = say.client
    # Acknowledge the command request
    ack()
    # Call views_open with the built-in client
    client.views_open(
        # Pass a valid trigger_id within 3 seconds of receiving it
        trigger_id=body["trigger_id"],
        # View payload
        view={
            "type": "modal",
            # View identifier
            "callback_id": "view_1",
            "title": {"type": "plain_text", "text": "My App"},
            "submit": {"type": "plain_text", "text": "Submit"},
            "blocks": [
                {
                    "type": "section",
                    "text": {"type": "mrkdwn", "text": "Welcome to a modal with _blocks_"},
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click me!"},
                        "action_id": "button_abc"
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_c",
                    "label": {"type": "plain_text", "text": "What are your hopes and dreams?"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "dreamy_input",
                        "multiline": True
                    }
                }
            ]
        }
    )


# Start listening for commands
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    SocketModeHandler(app, config["SLACK_APP_TOKEN"]).start()
