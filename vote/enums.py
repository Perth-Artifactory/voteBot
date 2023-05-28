from __future__ import annotations

from enum import StrEnum, auto


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
