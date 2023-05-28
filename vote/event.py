from __future__ import annotations

from dataclasses import dataclass

from vote.enums import EventType
from vote.slackuser import SlackUser


@dataclass
class Event:
    person: SlackUser | None
    event_type: EventType
    timestamp: str  # i.e. datetime.utc_now().isoformat()
    details: str
