import logging
from json.decoder import JSONDecodeError
from typing import Dict, Optional, cast

import requests
from dateutil.parser import isoparser

from api_session import session as s
from user import User

category_cache: Dict[int, str] = {}


class Challenge():
    chal_id: int
    name: str
    category: Optional[str] = None
    num_solves: int

    def __init__(self, chal_id: int, name: str, num_solves: int):
        self.chal_id = chal_id
        self.name = name
        self.num_solves = num_solves

        self._set_category()

    def get_solved_users(self):
        try:
            res = s.get(f"challenges/{self.chal_id}/solves")
        except requests.RequestException as error:
            logging.error(error)
            return None

        try:
            data = res.json()["data"]
        except (ValueError, JSONDecodeError, KeyError) as error:
            logging.error(error)
            return None

        for i in range(len(data)):
            res = s.get(f"teams/{data[i]['account_id']}/solves")
            buf = res.json()["data"]
            chal = None
            for item in buf:
                if item["challenge_id"] == self.chal_id:
                    chal = item
                    break
            if not chal:
                return None

            data[i]["user_name"] = chal["user"]["name"]

        solved_users = [User(solve["account_id"], user_name=solve["user_name"], team_name=solve["name"]) for solve in data]

        return solved_users

    def _set_category(self):
        if self.category is None:
            category = category_cache.get(self.chal_id, None)

            if category is None:
                try:
                    res = s.get(f"challenges/{self.chal_id}")
                    self.category = res.json()["data"]["category"]

                    category_cache[self.chal_id] = self.category
                except requests.RequestException as error:
                    logging.error(error)

    def get_first_blood_user(self) -> Optional[User]:
        try:
            res = s.get(f"challenges/{self.chal_id}/solves")
        except requests.RequestException as error:
            logging.error(error)
            return None

        try:
            data = res.json()["data"]
        except (ValueError, JSONDecodeError, KeyError) as error:
            logging.error(error)
            return None

        # Getting the solves by solve["account_id"]
        for i in range(len(data)):
            res = s.get(f"teams/{data[i]['account_id']}/solves")
            buf = res.json()["data"]
            chal = None
            # Getting only the solve for self.chal_id
            for item in buf:
                if item["challenge_id"] == self.chal_id:
                    chal = item
                    break
            if not chal:
                return None

            data[i]["user_name"] = chal["user"]["name"]

        solves = [{
            "user_id": solve["account_id"],
            "user_name": solve["user_name"],
            "team_name": solve["name"],
            "solve_time": isoparser().isoparse(solve["date"])
        } for solve in data]

        solves.sort(key=lambda x: x["solve_time"].timestamp())

        user_name = cast(str, solves[0]["user_name"])
        team_name = cast(str, solves[0]["team_name"])
        user_id = cast(int, solves[0]["user_id"])
        logging.info("First Blood: %s of %s - %s", user_name, team_name, user_id)

        return User(user_id, user_name, team_name)
