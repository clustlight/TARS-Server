import datetime
import logging
import os
import re

import requests
import shutil
from time import sleep

user_agent = os.environ.get("USER_AGENT")


def create_output_directory():
    if not os.path.exists("../../outputs"):
        os.mkdir("../../outputs")

def create_temp_directory():
    if not os.path.exists("../../temp"):
        os.mkdir("../../temp")


def create_user_directory(screen_id):
    if not os.path.exists(f"./outputs/{screen_id}"):
        os.mkdir(f"./outputs/{screen_id}")

    if not os.path.exists(f"./temp/{screen_id}"):
        os.mkdir(f"./temp/{screen_id}")


def create_segment_directory(screen_id, live_id):
    if not os.path.exists(f"./temp/{screen_id}/{live_id}"):
        os.mkdir(f"./temp/{screen_id}/{live_id}")


def delete_segment_directory(screen_id, live_id):
    if os.path.exists(f"./temp/{screen_id}/{live_id}"):
        shutil.rmtree(f"./temp/{screen_id}/{live_id}")


def escape_characters(text):
    if text is not None:
        return re.sub(r"%|\/|&|\s|;|:", "__", text)
    else:
        return text


def get_archive_file_name(movie_id, screen_id, live_title, live_subtitle):
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    screen_id = escape_characters(screen_id)
    live_title = escape_characters(live_title)
    live_subtitle = escape_characters(live_subtitle)

    return f"[{now}]-[{live_title}__{live_subtitle}]-[{screen_id}]-[{movie_id}]"

def get_stream_url(screen_id, event):
    logger = logging.getLogger("Video")
    response = requests.get(
            'https://twitcasting.tv/streamserver.php',
            params={
                "mode": "client",
                "target": screen_id,
                "player": "pc_web"
            }
        )

    streams = response.json().get("tc-hls", {}).get("streams", {})
    url = streams.get("high") or streams.get("medium") or streams.get("low")

    if not url:
        logger.error("No valid stream URL found.")
        return

    # A filler is streamed on the server side until the broadcast starts, but by default, it cannot adapt to resolution changes.
    # When the filler is being streamed, the segment file names include the term "preroll".
    # To start recording after the resolution changes, ensure that the term "preroll" is no longer detected.

    MAX_RETRIES = 10
    for retry_count in range(MAX_RETRIES):
        logger.debug(f"[{retry_count + 1}/{MAX_RETRIES}] Checking m3u8 playlist... ({screen_id})")
        res = requests.get(url=url, stream=True)
        if res.status_code == 200:
            logger.debug(f"[{retry_count + 1}/{MAX_RETRIES}] Successfully fetched m3u8 playlist. ({screen_id})")
            playlist_content = res.content.decode("utf-8")
            if "preroll" not in playlist_content:
                logger.debug(f"Preroll segment is no longer present in the playlist. Starting recording. ({screen_id})")
                return url
        else:
            logger.warning(f"[{retry_count + 1}/{MAX_RETRIES}] Failed to fetch m3u8 playlist. Status code: {res.status_code}")
        sleep(1)
    else:
        logger.error(f"Maximum retries reached. Unable to start recording. ({screen_id})")
        # Signal to stop all related tasks
        event.set()
        return


def get_comment_stream_url(live_id):
    headers = {
        "User-Agent": user_agent
    }
    data = {"movie_id": live_id}
    files = {(None, None)}
    response = requests.post("https://twitcasting.tv/eventpubsuburl.php", headers=headers, data=data, files=files)
    return response.json()["url"]
