# Required for some type hints to work
# https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

import jsonpickle
import jsonpickle.util

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum, auto
from typing import List, Dict


class VoteChoice(StrEnum):
    AYE = auto()
    NAY = auto()
    ABSTAIN = auto()


class PollType(StrEnum):
    COMMITTEE_MOTION = auto()
    COMMITTEE_APPROVAL = auto()


class PollStatus(StrEnum):
    OPEN = auto()
    PASSED = auto()
    REJECTED = auto()
    CLOSED_EARLY = auto()
    LAPSED = auto()


class EventType(StrEnum):
    CREATED = auto()
    EDITED = auto()
    VOTED = auto()
    CHANGED_VOTE = auto()
    MANUALLY_CLOSED = auto()
    MANUALLY_REOPENED = auto()
    AUTO_CLOSED = auto()
    SENT_REMINDER_TO_VOTE = auto()


@dataclass
class Event:
    person: SlackUser | None
    event_type: EventType
    timestamp: str  # i.e. datetime.utc_now().isoformat()
    details: str


@dataclass
class SlackUser:
    slack_id: str

    def lookup(self):
        """
        Looks up a Slack user's details (e.g. display name).
        Uses cached results where available.
        :return:
        """
    def __format__(self, format_spec) -> str:
        """
        :param format_spec:
        :return: Slack user's name and ID in a human-readable format, e.g. "Jane Doe (DEADBEEF01)".
        """
        pass


@dataclass
class Poll:
    """
    Note: @dataclass automatically generates __init__(), __repr__() and __eq__().
    """
    poll_type: PollType
    created_by: SlackUser
    status: PollStatus
    public_text: str
    private_text: str
    number_of_people_who_must_vote: int
    people_eligible_to_vote: List[SlackUser]
    people_who_must_vote: List[SlackUser]
    votes: Dict[SlackUser, VoteChoice]
    events: List[Event]
    version: int = 1

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