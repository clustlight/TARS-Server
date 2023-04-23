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


def download(event, url, screen_id, live_id, live_title, live_subtitle):
    screen_id = utils.escape_characters(screen_id)
    live_title = utils.escape_characters(live_title)
    live_subtitle = utils.escape_characters(live_subtitle)
    utils.create_user_directory(screen_id)

    title = utils.get_archive_file_name(live_id, screen_id, live_title, live_subtitle)
    utils.create_segment_directory(screen_id, live_id)

    process = Popen(
        f"exec ffmpeg -i {url} -user_agent '{user_agent}' -http_persistent 0 -c copy -f segment -segment_list_flags +live './outputs/{screen_id}/{live_id}/%05d.ts'",
        shell=True,
        stdin=PIPE,
        stderr=DEVNULL
    )

    logger.info(f"Recording started ({screen_id})")
    while True:
        sleep(1)
        logger.debug(f"Checking Recording Tasks... ({screen_id})")
        if process.poll() is None:
            logger.debug(f"The broadcast is ongoing ({screen_id})")
            if event.is_set():
                logger.info(f"Detect abort signals! ({screen_id})")
                logger.info(f"Started interruption process.... ({screen_id})")
                process.communicate(str.encode("q"))
                sleep(2)
                process.terminate()
                final_process = concatenate_segments(screen_id, live_id, title)
                final_process.wait()
                utils.delete_segment_directory(screen_id, live_id)
                logger.info(f"FFmpeg shutdown has been completed ({screen_id})")
                return
        else:
            logger.info(f"The broadcast has ended ({screen_id})")
            event.set()
            logger.info(f"Final processing has been initiated ({screen_id})")
            sleep(2)
            process.terminate()
            final_process = concatenate_segments(screen_id, live_id, title)
            final_process.wait()
            utils.delete_segment_directory(screen_id, live_id)
            logger.info(f"FFmpeg shutdown has been completed ({screen_id})")
            return


def concatenate_segments(screen_id, live_id, title):
    utils.create_segment_index(screen_id, live_id)
    process = Popen(
        f"exec ffmpeg -f concat -i './outputs/{screen_id}/{live_id}/index.txt' -c copy -movflags faststart './outputs/{screen_id}/{title}.mp4'",
        shell=True,
        stdin=PIPE,
        stderr=DEVNULL
    )
    return process


def comments(event, url, screen_id, live_id, live_title, live_subtitle):
    asyncio.run(stream_comments(event, url, screen_id, live_id, live_title, live_subtitle))


async def stream_comments(event, url, screen_id, live_id, live_title, live_subtitle):
    screen_id = utils.escape_characters(screen_id)
    live_title = utils.escape_characters(live_title)
    live_subtitle = utils.escape_characters(live_subtitle)
    utils.create_user_directory(screen_id)
    title = utils.get_archive_file_name(live_id, screen_id, live_title, live_subtitle)
    file = open(f"./outputs/{screen_id}/{title}.json", "w", encoding="utf-8")
    async with websockets.client.connect(url, user_agent_header=user_agent) as websocket:
        logger.info(f"Comment stream started ({screen_id})")
        try:
            async for data in websocket:
                if event.is_set():
                    file.close()
                    logger.info(f"Comment stream has been closed ({screen_id})")
                    return
                messages = json.loads(data)
                for message in messages:
                    text = json.dumps(message, ensure_ascii=False)
                    file.write(rf"{text}" + "\n")
        except websockets.ConnectionClosed:
            file.close()
            logger.info(f"Comment websocket connection has been closed ({screen_id})")


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
                screen_id = message['broadcaster']['screen_id']
                if message["event"] == "livestart":
                    logger.info(f"Received LIVE START Notification ({screen_id})")
                    requests.post(f"http://localhost:{port}/recordings/{screen_id}")
                elif message["event"] == "liveend":
                    logger.info(f"Received LIVE END Notification ({screen_id})")
        except websockets.ConnectionClosed:
            continue
