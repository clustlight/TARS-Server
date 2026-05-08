import os

import requests


class TwitcastingStreamClient:
    def __init__(self):
        self.timeout = float(os.environ.get("TWITCASTING_STREAM_TIMEOUT", "10"))
        self.session = requests.Session()
        self.user_agent = os.environ.get("USER_AGENT")

    def get_stream_server(self, screen_id: str):
        response = self.session.get(
            "https://twitcasting.tv/streamserver.php",
            params={
                "mode": "client",
                "target": screen_id,
                "player": "pc_web"
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_playlist(self, playlist_url: str):
        return self.session.get(playlist_url, stream=True, timeout=self.timeout)

    def get_comment_stream_url(self, live_id: str) -> str:
        response = self.session.post(
            "https://twitcasting.tv/eventpubsuburl.php",
            headers={"User-Agent": self.user_agent},
            data={"movie_id": live_id},
            files={(None, None)},
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()["url"]