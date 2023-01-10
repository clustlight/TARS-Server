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
    process = Popen(
        f"exec ffmpeg -i {url} -movflags faststart -user_agent '{user_agent}' -c copy -bsf:a aac_adtstoasc ./outputs/{user_name}/{title}.mp4",
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
                sleep(3)
                process.terminate()
                logger.info(f"FFmpeg shutdown has been completed ({user_name})")
                return
        else:
            logger.info(f"The broadcast has ended ({user_name})")
            event.set()
            logger.info(f"Final processing has been initiated ({user_name})")
            sleep(3)
            process.terminate()
            logger.info(f"FFmpeg shutdown has been completed ({user_name})")
            return

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
                    file.write(rf"{message}" + "\n")
        except websockets.ConnectionClosed:
            file.close()
            logger.info(f"Comment stream has been closed ({user_name})")

async def stream_notification(url):
    async for websocket in websockets.client.connect(url, extra_headers={"notification-server-access-token": token}):
        logger.info("Connected to Notification Server")
        try:
            async for data in websocket:
                message = json.loads(data)
                user_name = message['broadcaster']['screen_id']
                if message["event"] == "livestart":
                    logger.info(f"Received LIVE START Notification ({user_name})")
                    requests.post(f"http://localhost:{port}/records/{user_name}")
                elif message["event"] == "liveend":
                    logger.info(f"Received LIVE END Notification ({user_name})")
        except websockets.ConnectionClosed as exception:
            close_code = exception.rcvd.code
            if close_code == 1011:
                logger.error("Websocket Authentication Failed")
                logger.warning("Auto Recording has been DISABLED!")
                logger.warning("If you want to use the automatic recording function, "
                               "please make sure that the notification server is working properly "
                               "and that the connection destination and token settings are correct "
                               "before restarting the system.")
                return
            else:
                logger.info("Notification Stream has been closed")
                continue
