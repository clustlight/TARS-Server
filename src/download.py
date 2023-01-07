import asyncio
import json
import logging
from subprocess import Popen, PIPE, DEVNULL
from time import sleep

import websockets.client

import utils

logger = logging.getLogger(__name__)

def download(event, url, user_name, live_id, live_title, live_subtitle):
    user_name = utils.replace_colon(user_name)
    utils.create_user_directory(user_name)

    title = utils.get_archive_file_name(live_id, user_name, live_title, live_subtitle)
    process = Popen(
        f"exec ffmpeg -i {url} -movflags faststart -c copy -bsf:a aac_adtstoasc ./outputs/{user_name}/{title}.mp4",
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
    title = utils.get_archive_file_name(live_id, user_name, live_title, live_subtitle)
    file = open(f"./outputs/{user_name}/{title}.json", "x", encoding="utf-8")
    async with websockets.client.connect(url) as websocket:
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
