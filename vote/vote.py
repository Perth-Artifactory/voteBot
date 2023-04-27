# Required for some type hints to work
# https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum, auto
from typing import List, Dict


class VoteChoice(StrEnum):
    AYE = auto()
    NAY = auto()
    ABSTAIN = auto()


class VoteType(StrEnum):
    COMMITTEE_MOTION = auto()
    COMMITTEE_APPROVAL = auto()


class VoteStatus(StrEnum):
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
class SlackUser:
    slack_id: str


@dataclass
class Vote:
    vote_type: VoteType
    vote_public_text: str
    vote_private_text: str
    number_of_people_who_must_vote: int
    people_eligible_to_vote: List[SlackUser]
    people_who_must_vote: List[SlackUser]
    votes: Dict[SlackUser, VoteChoice]
    events: List[Event]
    version: int = 1

    def cast_vote(self, voter: SlackUser, choice: VoteChoice):
        pass

    def edit(self):
        pass

    def cron(self) -> None:
        """
        Perform regular scheduled actions.

        * Check if the vote has met the criteria to be closed automatically.

        * Remind people to vote if they haven't voted yet.

        :return: None.
        """
        pass

    def close(self):
        """

        :return:
        """
        pass

    @staticmethod
    def from_json(json_str: str) -> Vote:
        """
        Deserialise.
        (Or will jsonpickle do this for us??)
        :param json_str:
        :return:
        """
        return Vote(vote_type=None,
                    vote_public_text=None,
                    vote_private_text=None,
                    number_of_people_who_must_vote=None,
                    people_eligible_to_vote=None,
                    people_who_must_vote=None,
                    votes=None,
                    events=None,
                    version=None,
                    )
        pass


@dataclass
class Event:
    person: SlackUser | None
    event_type: EventType
    datetime_utc: datetime
    details: str


# a = Vote(vote_type="a",
#          vote_public_text="b",
#          vote_private_text="c",
#          number_of_people_who_must_vote=9,
#          people_eligible_to_vote=["DEADBEEF03", "DEADBEEF04"],
#          people_who_must_vote=["DEADBEEF01", "DEADBEEF02"],
#          votes=[],
#          )
