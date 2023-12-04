import asyncio
import logging
import random
from json.decoder import JSONDecodeError
from typing import Any, Dict

import requests

import config
from announcer import Announcer
from api_session import session as s
from challenge import Challenge
from db import DB


class SolveHandler:
    host: str

    def __init__(self):
        super().__init__()
        self.announcer = Announcer()

    async def handle_past_solves(self):
        logging.log(logging.WARN, "HANDLING PAST SOLVES")

        try:
            res = s.get("statistics/challenges/solves")
        except requests.RequestException as error:
            logging.error(error)
            asyncio.create_task(self.handle_solves())
            return

        try:
            chals: list[Dict[str, Any]] = res.json()["data"]
        except (ValueError, JSONDecodeError, KeyError) as error:
            print(error)
            chals = []

        for chal_data in chals:
            print(f"Got challenge data: {chal_data}")
            chal = Challenge(chal_data["id"], chal_data["name"],
                             chal_data["solves"])

            users = chal.get_solved_users()
            if users:
                DB.add_to_db(chal, users)

        asyncio.create_task(self.handle_solves())

    async def handle_solves(self):
        await asyncio.sleep(config.POLL_PERIOD)

        logging.log(logging.WARN, "NEW ROUND")
        try:
            res = s.get("statistics/challenges/solves")
        except requests.RequestException as error:
            logging.error(error)
            asyncio.create_task(self.handle_solves())
            return

        try:
            chals: list[Dict[str, Any]] = res.json()["data"]
        except (ValueError, JSONDecodeError, KeyError) as error:
            print(error)
            chals = []

        for chal_data in chals:
            print(f"Got challenge data: {chal_data}")
            chal = Challenge(chal_data["id"], chal_data["name"],
                             chal_data["solves"])

            if chal.num_solves > 0:
                DB.cursor.execute(
                    "SELECT user_id FROM announced_solves WHERE chal_id = ?",
                    (chal.chal_id, ))
                res = DB.cursor.fetchall()
                logging.debug("Solvers id's: %s", res)

                # If there are no announced solves then announce the first blood
                if not res:
                    await self.handle_first_blood(chal)
                else:
                    logging.debug("Already announced first blood for %s",
                                  chal.name)

            if config.ANNOUNCE_ALL_SOLVES and chal.num_solves > 0:
                try:
                    DB.cursor.execute(
                        "SELECT chal_id FROM announced_solves WHERE chal_id = ?",
                        (chal.chal_id, ))
                    res = DB.cursor.fetchone()
                    assert res != []
                except AssertionError:
                    logging.error(
                        "Challenge already solved but wasn't announced. Skipping"
                    )
                    break

                await self.handle_new_solves(chal)

        asyncio.create_task(self.handle_solves())

    async def handle_first_blood(self, chal: Challenge):
        logging.info("Challenge: %s - %s", chal.name, chal.chal_id)

        user = chal.get_first_blood_user()
        if not user:
            return

        DB.cursor.execute("INSERT INTO announced_solves VALUES (?, ?)",
                          (chal.chal_id, user.user_id))
        DB.conn.commit()

        r = s.get(f"/challenges/{chal.chal_id}")
        __ = r.json()["data"]
        chal.category = __["category"]
        challenge_points = __["value"]

        if chal.category:
            emojis = config.CATEGORY_EMOJIS.get(chal.category.lower(), [])
        else:
            emojis = []

        if emojis:
            emoji_string = random.choice(emojis)
        else:
            emoji_string = ""

        await self.announcer.announce(chal.name,
            user.user_name,
            user.team_name,
            emoji_string,
            first_blood=True,
            chal_id=chal.chal_id,
            category=chal.category,
            points=challenge_points,
            s=s
        )

    async def handle_new_solves(self, chal: Challenge):
        users = chal.get_solved_users()

        if not users:
            return

        DB.cursor.execute(
            "SELECT user_id FROM announced_solves WHERE chal_id = ?",
            (chal.chal_id, ))
        res = DB.cursor.fetchall()

        for user in users:
            if (user.user_id, ) not in res:
                logging.info("New Solve - Challenge: %s - User: %s - Team: %s", chal.name,
                             user.user_name, user.team_name)

                DB.cursor.execute("INSERT INTO announced_solves VALUES (?, ?)",
                                  (chal.chal_id, user.user_id))
                DB.conn.commit()
                
                r = s.get(f"/challenges/{chal.chal_id}")
                __ = r.json()["data"]
                chal.category = __["category"]
                challenge_points = __["value"]

                if chal.category:
                    emojis = config.CATEGORY_EMOJIS.get(chal.category.lower(), [])
                else:
                    emojis = []

                if emojis:
                    emoji_string = random.choice(emojis)
                else:
                    emoji_string = ""

                await self.announcer.announce(
                    chal.name,
                    user.user_name,
                    user.team_name,
                    emoji_string,
                    first_blood=False,
                    chal_id=chal.chal_id,
                    category=chal.category,
                    points=challenge_points,
                    s=s
                )
            else:
                logging.debug("Already announced solve on %s by %s - %s",
                              chal.name, user.user_name, user.user_id)
