from __future__ import annotations

from dataclasses import dataclass


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
