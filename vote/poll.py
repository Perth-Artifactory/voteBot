# Required for some type hints to work
# https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

import json

from datetime import datetime
from typing import List, Dict, Optional

from vote.enums import VoteChoice, PollType, PollStatus, EventType
from vote.event import Event
from vote.slackuser import SlackUser


class Poll:
    version: int = 1

    def __init__(self,
                 poll_type: PollType,
                 created_by: SlackUser,
                 status: PollStatus = PollStatus.OPEN,
                 public_text: str = "",
                 private_text: str = "",
                 number_of_people_who_must_vote: int = 0,
                 people_who_can_vote: Optional[List[SlackUser]] = None,
                 people_who_must_vote: Optional[List[SlackUser]] = None,
                 ) -> None:

        self.poll_type = poll_type
        self.created_by = created_by
        self.status = status
        self.public_text = public_text
        self.private_text = private_text
        self.number_of_people_who_must_vote = number_of_people_who_must_vote

        self.people_eligible_to_vote: List[SlackUser] = [] if people_who_can_vote is None else people_who_can_vote
        self.people_who_must_vote: List[SlackUser] = [] if people_who_must_vote is None else people_who_must_vote

        self.votes: Dict[SlackUser, VoteChoice] = dict()
        self.events: List[Event] = list()

    def to_json_dict(self) -> str:
        out = dict()

        # out["poll_type"] = str(self.poll_type)

        for attr in ["poll_type", "status", "created_by"]:
            out[attr] = str(self.__dict__[attr])

        for attr in ["public_text", "private_text", "number_of_people_who_must_vote"]:
            out[attr] = self.__dict__[attr]

        out["votes"] = {str(slack_user): str(vote_choice) for slack_user, vote_choice in self.votes.items()}

        out["events"] = [event.to_json_dict() for event in self.events]

        return out

    def cast_vote(self, voter: SlackUser, choice: VoteChoice) -> None:
        """
        Records a person's vote in a Poll.
        If the person had already voted, their existing vote is changed.
        The person's action is recorded as an Event.
        :param voter:
        :param choice:
        :return:
        """
        if self.status is not PollStatus.OPEN:
            raise ValueError(f"Can't vote on a poll whose status is {self.status}.")

        if voter not in self.people_eligible_to_vote:
            raise ValueError(f"Voter {voter} is not eligible to vote in this poll.")

        if voter not in self.votes:
            event_type = EventType.VOTED
        else:
            event_type = EventType.CHANGED_VOTE

        self.votes[voter] = choice

        event = Event(person=voter,
                      event_type=event_type,
                      timestamp=datetime.utcnow().isoformat(),
                      details=f"Cast vote of {choice}"
                      )

    def edit(self, person: SlackUser, **changes) -> None:
        """
        Records an edit made to any of the parameters of a Poll.
        The edit is recorded as an Event.
        The event is advertised as a thread reply to the poll message.
        :return:
        """
        if self.status is not PollStatus.OPEN:
            raise ValueError(f"Can't edit a poll whose status is {self.status}.")

        if person != self.created_by:
            raise ValueError(f"Person {person} can't edit this poll. "
                             f"Only the creator, {self.created_by}, can edit this poll.")

        for k, new_v in changes.items():
            assert k in self.__dict__

            old_v = self.__dict__[k]

            event = Event(person=person,
                          event_type=EventType.EDITED,
                          timestamp=datetime.utcnow().isoformat(),
                          details=f"{k} changed.\n\n"
                                  f"From:\n\n"
                                  f"{old_v}\n\n"
                                  f"To:\n\n"
                                  f"{new_v}",
                          )
            self.events.append(event)

            # FIXME: Advertise change as a threaded reply to the poll message

            self.__dict__[k] = new_v

    def cron(self) -> None:
        """
        Perform regular scheduled actions.

        * Check if the poll has met the criteria to be closed automatically.

        * Remind people to vote if they haven't voted yet.

        :return: None.
        """
        pass

    def close(self, person: SlackUser):
        """
        Closes a Poll so that:

        * The Poll can no longer be voted on

        * The Poll can no longer be edited

        * The result of the Poll (e.g. pass, fail) is determined.

        Closing a Poll is recorded as an Event.

        The event is advertised as a thread reply to the poll message.
        :return:
        """
        pass

    # @staticmethod
    # def from_json(json_str: str) -> Poll:
    #     """
    #     Deserialise.
    #     (Or will jsonpickle do this for us??)
    #     :param json_str:
    #     :return:
    #     """
    #     return Poll(poll_type=None,
    #                 public_text=None,
    #                 private_text=None,
    #                 number_of_people_who_must_vote=None,
    #                 people_eligible_to_vote=None,
    #                 people_who_must_vote=None,
    #                 votes=None,
    #                 events=None,
    #                 version=None,
    #                 )
    #     pass

# a = Vote(vote_type="a",
#          vote_public_text="b",
#          vote_private_text="c",
#          number_of_people_who_must_vote=9,
#          people_eligible_to_vote=["DEADBEEF03", "DEADBEEF04"],
#          people_who_must_vote=["DEADBEEF01", "DEADBEEF02"],
#          votes=[],
#          )
