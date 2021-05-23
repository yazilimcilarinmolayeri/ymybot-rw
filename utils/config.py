# -*- coding: utf-8 -*-

from os import environ as env
from discord import Status, ActivityType


PREFIX = ["."]
TOKEN = "" or env.get("TOKEN")
STATUS_TYPE = Status.idle
ACTIVITY_TYPE = ActivityType.watching

DEFAULT_GUILD_ID = 418887354699350028  # YMY

MENTION_LOG_CHANNEL_ID = 687805076857028671
DM_LOG_CHANNEL_ID = 687804890860486762
AVATAR_LOG_CHANNEL_ID = 774377336895701042
PROFILE_CHANNEL_ID = 698479324440952923
FEEDBACK_CHANNEL_ID = 845508093134635048

PARTNER_ROLE_ID = 467348162613346304
SPONSOR_ROLE_ID = 816342065398022207
