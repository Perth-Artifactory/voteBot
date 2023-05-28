import unittest
import jsonpickle

from pprint import pprint

from vote.poll import Poll
from vote.enums import VoteChoice, PollStatus, EventType, PollType
from vote.slackuser import SlackUser


class MyTestCase(unittest.TestCase):

    def test_something(self):
        x = 1

        su = SlackUser(slack_id="DEADBEEF")

        poll = Poll(poll_type=PollType.COMMITTEE_MOTION,
                    created_by=su,
                    status=PollStatus.OPEN,
                    public_text="public",
                    private_text="private",
                    number_of_people_who_must_vote=1,
                    people_who_can_vote=[su, ],
                    people_who_must_vote=[su, ],
                    )

        myjson = poll.to_json_dict()

        pprint(myjson)


if __name__ == '__main__':
    unittest.main()
