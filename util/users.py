import logging as log
from typing import List, Tuple

import cachetools

import main


@cachetools.cached(cachetools.TTLCache(maxsize=1024, ttl=600))
def get_user_info(user: str) -> dict:
    """
    Wraps app.client.users_info() with a 600 second TTL cache.
    See https://api.slack.com/methods/users.info
    :param user:
    :return:
    """
    log.debug(f"get_user_info: user={user}")
    r = main.app.client.users_info(user=user)

    if r["ok"] is False:
        raise

    return r.data["user"]


@cachetools.cached(cachetools.TTLCache(maxsize=1024, ttl=600))
def get_users_in_channel(channel: str) -> List[Tuple[str, str]]:
    """
    Get the users in the given channel, excluding bots and app users.
    Results are cached for 600 seconds.
    :param channel: Channel ID
    :return: List of (User ID, user's display name).
    """
    log.debug(f"get_users_in_channel: channel={channel}")

    r = main.app.client.conversations_members(channel=channel)
    if r["ok"] is False:
        raise

    users = []

    for m in r.data["members"]:
        u = get_user_info(user=m)
        if u["is_bot"] or u["is_app_user"]:
            continue
        users.append((u["id"], u["profile"]["display_name"]))

    return users
