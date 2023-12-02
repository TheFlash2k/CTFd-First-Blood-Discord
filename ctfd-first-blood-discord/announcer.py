import json
from typing import Any, Dict

import requests
from discord import Webhook
import aiohttp

import config

class Announcer:
    webhook_data: Dict[str, Any]
    solve_string: str
    first_blood_string: str
    rate_limit_remaining: int
    rate_limit_sleep_time: int

    def __init__(self):
        self.solve_string = config.SOLVE_ANNOUNCE_STRING
        self.first_blood_string = config.FIRST_BLOOD_ANNOUNCE_STRING
        # self.webhook_data = json.loads(
        #     requests.get(self.webhook_url, timeout=10).content.decode())
        self.rate_limit_remaining = 1
        self.rate_limit_sleep_time = 0

    async def announce(self,
        chal_name: str,
        user_name: str,
        team_name: str,
        emoji: str,
        first_blood: bool = False,
        chal_id: int = 0,
        category: str = "",
        points: int = 0
    ):

        json_data = {
            "points" : points,
            "category" : category,
            "chal_name" : chal_name,
            "team_name" : team_name,
            "solved_by" : user_name,
            "first_blood" : first_blood
        }

        async with aiohttp.ClientSession() as session:

            if first_blood:
                webhook = Webhook.from_url(url=config.FIRST_BLOOD_WEBHOOK_URL, session=session)
                await webhook.send(
                    self.first_blood_string.format(
                        user_name=user_name,
                        team_name=team_name,
                        chal_name=chal_name,
                        emojis=emoji
                    )
                )
            else:
                webhook = Webhook.from_url(url=config.SOLVE_WEBHOOK_URL, session=session)
                await webhook.send(
                    self.solve_string.format(
                        user_name=user_name,
                        team_name=team_name,
                        chal_name=chal_name,
                        emojis=emoji
                    )
                )
