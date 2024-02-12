import json
import logging
import os
import base64

import dotenv
import requests

dotenv.load_dotenv()
logger = logging.getLogger(__name__)


class Twitcasting:
    def __init__(self):
        self.client_id = os.environ.get("CLIENT_ID")
        self.client_secret = os.environ.get("CLIENT_SECRET")
        self.token = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        self.headers = {
            "Accept": "application/json",
            "X-Api-Version": "2.0",
            "Authorization": f"Basic {self.token}"
        }

    def get_subscriptions(self) -> (bool, dict):
        response = requests.get('https://apiv2.twitcasting.tv/webhooks', headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            users = data["webhooks"]
            if data["all_count"] > 50:
                count = data["all_count"] - 50
                i = 1
                while count > 0:
                    response = requests.get(f'https://apiv2.twitcasting.tv/webhooks?offset={50 * i}', headers=self.headers)
                    i += 1
                    count -= 50
                    users += response.json()["webhooks"]
            return True, data
        else:
            logger.error(f"API Error: ({response.status_code}) {response.json()['error']['message']}")
            return False, response.json()

    def add_subscription(self, user_id: str) -> (bool, dict):
        payloads = {
            "user_id": user_id,
            "events": [
                "livestart"
            ]
        }
        response = requests.post('https://apiv2.twitcasting.tv/webhooks', headers=self.headers, data=json.dumps(payloads))
        if response.status_code == 200 or response.status_code == 201:
            return True, response.json()
        else:
            logger.error(f"API Error: ({response.status_code}) {response.json()['error']['message']}")
            return False, response.json()

    def remove_subscription(self, user_id: str) -> (bool, dict):
        response = requests.delete(f'https://apiv2.twitcasting.tv/webhooks?user_id={user_id}&events[]=livestart', headers=self.headers)
        if response.status_code == 200:
            return True, response.json()
        else:
            logger.error(f"API Error: ({response.status_code}) {response.json()['error']['message']}")
            return False, response.json()

    def get_user_info(self, screen_id: str) -> (bool, dict):
        response = requests.get(f"https://apiv2.twitcasting.tv/users/{screen_id}", headers=self.headers)
        if response.status_code == 200:
            return True, response.json()
        else:
            logger.error(f"API Error: ({response.status_code}) {response.json()['error']['message']}")
            return False, response.json()

    def get_movie_info(self, movie_id: str) -> (bool, dict):
        response = requests.get(f"https://apiv2.twitcasting.tv/movies/{movie_id}", headers=self.headers)
        if response.status_code == 200:
            return True, response.json()
        else:
            logger.error(f"API Error: ({response.status_code}) {response.json()['error']['message']}")
            return False, response.json()
