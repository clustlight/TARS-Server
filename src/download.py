import asyncio
import json
import logging
import os
from subprocess import Popen, PIPE, DEVNULL
from time import sleep

import requests
import websockets.client

import utils

logger = logging.getLogger(__name__)

port = os.environ.get("PORT")
user_agent = os.environ.get("USER_AGENT")
token = os.environ.get("NOTIFICATION_SERVER_TOKEN")


def download(event, url, user_name, live_id, live_title, live_subtitle):
    user_name = utils.escape_characters(user_name)
    live_title = utils.escape_characters(live_title)
    live_subtitle = utils.escape_characters(live_subtitle)
    utils.create_user_directory(user_name)

    title = utils.get_archive_file_name(live_id, user_name, live_title, live_subtitle)
    utils.create_segment_directory(user_name, live_id)

    process = Popen(
        f"exec ffmpeg -i {url} -user_agent '{user_agent}' -http_persistent 0 -c copy -f segment -segment_list_flags +live './outputs/{user_name}/{live_id}/%05d.ts'",
        shell=True,
        stdin=PIPE,
        stderr=DEVNULL
    )

    logger.info(f"Recording started ({user_name})")
    while True:
        sleep(1)
        logger.debug(f"Checking Recording Tasks... ({user_name})")
        if process.poll() is None:
            logger.debug(f"The broadcast is ongoing ({user_name})")
            if event.is_set():
                logger.info(f"Detect abort signals! ({user_name})")
                logger.info(f"Started interruption process.... ({user_name})")
                process.communicate(str.encode("q"))
                sleep(2)
                process.terminate()
                final_process = concatenate_segments(user_name, live_id, title)
                final_process.wait()
                utils.delete_segment_directory(user_name, live_id)
                logger.info(f"FFmpeg shutdown has been completed ({user_name})")
                return
        else:
            logger.info(f"The broadcast has ended ({user_name})")
            event.set()
            logger.info(f"Final processing has been initiated ({user_name})")
            sleep(2)
            process.terminate()
            final_process = concatenate_segments(user_name, live_id, title)
            final_process.wait()
            utils.delete_segment_directory(user_name, live_id)
            logger.info(f"FFmpeg shutdown has been completed ({user_name})")
            return


def concatenate_segments(user_name, live_id, title):
    utils.create_segment_index(user_name, live_id)
    process = Popen(
        f"exec ffmpeg -f concat -i './outputs/{user_name}/{live_id}/index.txt' -c copy -movflags faststart './outputs/{user_name}/{title}.mp4'",
        shell=True,
        stdin=PIPE,
        stderr=DEVNULL
    )
    return process


def comments(event, url, user_name, live_id, live_title, live_subtitle):
    asyncio.run(stream_comments(event, url, user_name, live_id, live_title, live_subtitle))


async def stream_comments(event, url, user_name, live_id, live_title, live_subtitle):
    user_name = utils.escape_characters(user_name)
    live_title = utils.escape_characters(live_title)
    live_subtitle = utils.escape_characters(live_subtitle)
    title = utils.get_archive_file_name(live_id, user_name, live_title, live_subtitle)
    file = open(f"./outputs/{user_name}/{title}.json", "x", encoding="utf-8")
    async with websockets.client.connect(url, user_agent_header=user_agent) as websocket:
        logger.info(f"Comment stream started ({user_name})")
        try:
            async for data in websocket:
                if event.is_set():
                    file.close()
                    logger.info(f"Comment stream has been closed ({user_name})")
                    return
                messages = json.loads(data)
                for message in messages:
                    text = json.dumps(message, ensure_ascii=False)
                    file.write(rf"{text}" + "\n")
        except websockets.ConnectionClosed:
            file.close()
            logger.info(f"Comment websocket connection has been closed ({user_name})")


async def stream_notification(url):
    async for websocket in websockets.client.connect(
            url,
            ping_interval=5,
            ping_timeout=7,
            close_timeout=3,
            extra_headers={"notification-server-access-token": token}
    ):
        logger.info("Connected to Notification Server")
        try:
            async for data in websocket:
                message = json.loads(data)
                user_name = message['broadcaster']['screen_id']
                if message["event"] == "livestart":
                    logger.info(f"Received LIVE START Notification ({user_name})")
                    requests.post(f"http://localhost:{port}/recordings/{user_name}")
                elif message["event"] == "liveend":
                    logger.info(f"Received LIVE END Notification ({user_name})")
        except websockets.ConnectionClosed:
            continue
