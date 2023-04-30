import datetime
import json
import os

import dotenv
import requests

dotenv.load_dotenv()


class Discord:

    def __init__(self):
        self.endpoint = os.environ.get("DISCORD_WEBHOOK_URL")
        self.headers = {
            "Content-Type": "application/json"
        }

    def push_start_notification(self, screen_id, user_name, profile_image, live_id, live_title, live_subtitle):
        payloads = {
            "user_name": "TARS-Server",
            "embeds": [
                {
                    "title": live_title,
                    "description": live_subtitle,
                    "url": f"https://twitcasting.tv/{screen_id}",
                    "color": 5620992,
                    "author": {
                        "name": f"{user_name}  (@{screen_id})"
                    },
                    "thumbnail": {
                        "url": profile_image
                    },
                    "image": {
                        "url": f"https://apiv2.twitcasting.tv/users/{screen_id}/live/thumbnail?size=large&position=beginning"
                    },
                    "footer": {
                        "text": datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                    },
                    "fields": [
                        {
                            "name": "Live ID",
                            "value": live_id
                        }
                    ]
                }
            ]
        }

        requests.post(self.endpoint, headers=self.headers, data=json.dumps(payloads))
