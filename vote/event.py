from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from vote.enums import EventType
from vote.slackuser import SlackUser


@dataclass
class Event:
    person: SlackUser | None
    event_type: EventType
    timestamp: datetime  # i.e. datetime.utc_now().isoformat()
    details: str

    def to_json_dict(self) -> dict:
        out = {
            "person": None if self.person is None else str[self.person],
            "event_type": str(self.event_type),
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }

        return out
