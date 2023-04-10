#!/usr/bin/python3

import json
import logging
import sys
from enum import StrEnum
from pprint import pprint

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# Local path to patched version of https://github.com/imryche/blockkit
# Patched to support NumberInput.
# See https://github.com/imryche/blockkit/pull/74
sys.path.append(r"C:\gits\blockkit")

from blockkit import (
    Section,
    MarkdownText,
    Modal,
    Header,
    Divider,
    RadioButtons,
    PlainOption,
    PlainText,
    MultiUsersSelect,
    Input,
    PlainTextInput,
    NumberInput,  # See above re patch for NumberInput.
)

# Initialise slack
with open("config.json", "r") as f:
    config = json.load(f)

app = App(token=config["SLACK_BOT_TOKEN"])


# Enumerate all the various magic strings used throughout the Slack blocks.
# Using enums eliminates the problem of changing a string constant but not changing all the places it's used.


class VoteType(StrEnum):
    ONLINE_MOTION = "online_motion"
    APPROVAL = "approval"


class BlockIds(StrEnum):
    VOTE_TEXT = "vote_text"
    VOTE_TYPE = "vote_type"
    VOTE_TYPE_LONG_DESCRIPTION = "vote_type_long_description"
    APPROVAL_NUMBER_OF_APPROVERS = "approval_number_of_approvers"
    APPROVAL_SPECIFIC_PEOPLE_REQUIRED = "approval_specific_people_required"


class ActionIds(StrEnum):
    VOTE_TEXT = "vote_text_action"
    VOTE_TYPE = "vote_type_action"


class CallbackIds(StrEnum):
    NEW_VOTE = "newvote_callback"


vote_type_definitions = {
    VoteType.ONLINE_MOTION: {
        "text": "Online Motion",
        "75_char_desc": "Passes when everyone votes `Aye`",
        "2000_char_desc": "*Online motion:*\n"
        "  - To pass, every person in the channel must vote `Aye` or `Abstain`.\n"
        "  - To pass, at least 4 people must vote `Aye`.\n"
        "  - Any `Nay` vote causes the motion to fail.\n",
    },
    VoteType.APPROVAL: {
        "text": "Approval",
        "75_char_desc": "Passes when specified people vote `Approve`",
        "2000_char_desc": "*Approval*:\n"
        "  - To pass, the specified number of people must vote `Approve`.\n"
        "  - You can specify particular people who must `Approve`, e.g. the Chairperson or the Treasurer.\n"
        "  - A person can vote `Object` to formally record their objection to the matter at hand.\n",
    },
}


def make_newvote_modal(current_state=None):
    """
    Construct a view for the "New Vote" modal dialog.

    This gets called a) upon first creation of the modal, and b) each time the view needs to be updated.

    E.g. when the radio button for "type of vote" changes, we need to display different input fields and information.

    :param current_state: Pass in the `body` parameter from the callback.
    Current state is pulled from body["view"]["state"].

    :return: A Modal object, to use client.views_open() or views_update().
    Note you must call the Method.build() method before passing to Slack API.
    e.g.
    my_modal = make_newvote_modal()
    client.views_open(view=my_modal.build()).
    """
    print("Current state:")
    pprint(current_state)
    print("\n\n\n")

    if current_state is None:
        current_vote_type = VoteType.ONLINE_MOTION

    else:
        current_values = current_state["view"]["state"]["values"]
        current_vote_type = current_values[BlockIds.VOTE_TYPE][ActionIds.VOTE_TYPE][
            "selected_option"
        ]["value"]

    vote_text_input = Input(
        block_id=BlockIds.VOTE_TEXT,
        dispatch_action=False,
        label="Vote text",
        element=PlainTextInput(
            action_id=ActionIds.VOTE_TEXT,
            placeholder=PlainText(
                text="e.g. MOTION: Approve Jane Doe's application for concession membership"
            ),
            multiline=True,
        ),
    )

    def vote_type_option(vt):
        # Convenience function to manufacture Option blocks
        return PlainOption(
            text=PlainText(text=vote_type_definitions[vt]["text"]),
            value=vt,
            description=vote_type_definitions[vt]["75_char_desc"],
        )

    # Radio button input for vote type
    vote_type_input = Input(
        block_id=BlockIds.VOTE_TYPE,
        dispatch_action=True,
        label=PlainText(text="Type of vote:"),
        element=RadioButtons(
            action_id=ActionIds.VOTE_TYPE,
            initial_option=vote_type_option(current_vote_type),
            options=[vote_type_option(vt) for vt, _ in vote_type_definitions.items()],
        ),
    )

    # Detailed description of vote type
    vote_type_long_description = Section(
        block_id=BlockIds.VOTE_TYPE_LONG_DESCRIPTION,
        text=MarkdownText(
            text=vote_type_definitions[current_vote_type]["2000_char_desc"]
        ),
    )

    # When the vote type is APPROVAL - input to specify how many approvers are required
    approval_number_of_approvers_input = Input(
        block_id=BlockIds.APPROVAL_NUMBER_OF_APPROVERS,
        label="Number of approvers",
        element=NumberInput(is_decimal_allowed=False, min_value="1", max_value="10"),
    )

    # When the vote type is APPROVAL - input to select specific people who must approve.
    approval_specific_people_required_input = Input(
        block_id=BlockIds.APPROVAL_SPECIFIC_PEOPLE_REQUIRED,
        label="Required",
        element=MultiUsersSelect(placeholder="Who must vote", action_id="no_action"),
    )

    blocks = [
        Header(text="New vote"),
        Divider(),
        vote_text_input,
        Divider(),
        vote_type_input,
        vote_type_long_description,
        Divider(),
    ]

    if current_vote_type == VoteType.APPROVAL:
        # Only show these blocks when relevant
        blocks.extend(
            [
                approval_specific_people_required_input,
                approval_number_of_approvers_input,
            ]
        )

    my_modal = Modal(
        title="New vote",
        blocks=blocks,
        close="Close",
        submit="Submit",
        callback_id=CallbackIds.NEW_VOTE,
    )

    return my_modal


@app.command("/newvote")
def handle_newvote(ack, body, logger):
    ack()
    my_modal = make_newvote_modal()
    app.client.views_open(trigger_id=body["trigger_id"], view=my_modal.build())


@app.action(ActionIds.VOTE_TYPE)
def handle_action_id(ack, body, logger):
    ack()
    my_modal = make_newvote_modal(body)
    app.client.views_update(
        # Pass the view_id
        view_id=body["view"]["id"],
        # String that represents view state to protect against race conditions
        hash=body["view"]["hash"],
        # View payload with updated blocks
        view=my_modal.build(),
    )


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
                    "text": {
                        "type": "mrkdwn",
                        "text": "Welcome to a modal with _blocks_",
                    },
                    "accessory": {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Click me!"},
                        "action_id": "button_abc",
                    },
                },
                {
                    "type": "input",
                    "block_id": "input_c",
                    "label": {
                        "type": "plain_text",
                        "text": "What are your hopes and dreams?",
                    },
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "dreamy_input",
                        "multiline": True,
                    },
                },
            ],
        },
    )


# # Listens to incoming messages that contain "hello"
# # To learn available listener method arguments,
# # visit https://slack.dev/bolt-python/api-docs/slack_bolt/kwargs_injection/args.html
# @app.message("list_users")
# def message_list_users(message, say):
#     channel = message["channel"]
#     users = util.users.get_users_in_channel(channel)
#     all_users = "\n".join([u_real_name for u_id, u_real_name in users])
#     msg_text = f"Hello to:\n{all_users}"
#     my_header = HeaderBlock(text="Foo Header", block_id=None)
#     my_divider = DividerBlock(block_id=None)
#     my_section = SectionBlock(text=msg_text, block_id=None, fields=None, accessory=my_button)
#     my_message = Message(channel=message["channel"], text="No text?", blocks=[my_header, my_divider, my_section])
#     say(**my_message)

# Start listening for commands
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    SocketModeHandler(app, config["SLACK_APP_TOKEN"]).start()
