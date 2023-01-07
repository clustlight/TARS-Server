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
            return True, response.json()
        else:
            logger.error(f"API Error: ({response.status_code}) {response.json()['error']['message']}")
            return False, response.json()

    def add_subscription(self, user_id: str) -> (bool, dict):
        payloads = {
            "user_id": user_id,
            "events": [
                "livestart",
                "liveend"
            ]
        }
        response = requests.post('https://apiv2.twitcasting.tv/webhooks', headers=self.headers, data=json.dumps(payloads))
        if response.status_code == 200:
            return True, response.json()
        else:
            logger.error(f"API Error: ({response.status_code}) {response.json()['error']['message']}")
            return False, response.json()


    def remove_subscription(self, user_id: str) -> (bool, dict):
        payloads = {
            "user_id": user_id,
            "events": [
                "livestart",
                "liveend"
            ]
        }
        response = requests.delete('https://apiv2.twitcasting.tv/webhooks', headers=self.headers, data=json.dumps(payloads))
        if response.status_code == 200:
            return True, response.json()
        else:
            logger.error(f"API Error: ({response.status_code}) {response.json()['error']['message']}")
            return False, response.json()

    def get_user_info(self, user_id: str) -> (bool, dict):
        response = requests.get(f"https://apiv2.twitcasting.tv/users/{user_id}", headers=self.headers)
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
            return False, response.json