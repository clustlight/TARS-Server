import asyncio
import json
import logging
import os
import shutil
from subprocess import Popen, PIPE, DEVNULL
from time import sleep

import requests
import websockets.client

import utils
import database
from twitcasting import Twitcasting

port = os.environ.get("PORT")
user_agent = os.environ.get("USER_AGENT")
token = os.environ.get("NOTIFICATION_SERVER_TOKEN")


def stream_video(event, screen_id, live_id, live_title, live_subtitle):
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
    # When the filler is being streamed, the segment file names include the term "preroll."
    # To start recording after the resolution changes, ensure that the term "preroll" is no longer detected.
    while True:
        res = requests.get(url=url, stream=True)
        if res.status_code == 200:
            logger.debug("Successfully fetched m3u8 playlist.")
            playlist_content = res.content.decode("utf-8")
            if "preroll" not in playlist_content:
                logger.debug("Preroll segment is no longer present in the playlist.")
                break
        else:
            logger.warning(f"Failed to fetch m3u8 playlist. Status code: {res.status_code}")
        sleep(1)

    screen_id = utils.escape_characters(screen_id)
    live_title = utils.escape_characters(live_title)
    live_subtitle = utils.escape_characters(live_subtitle)

    file_title = utils.get_archive_file_name(live_id, screen_id, live_title, live_subtitle)
    utils.create_segment_directory(screen_id, live_id)

    command = [
        "ffmpeg",
        "-user_agent", user_agent,
        "-http_persistent", "0",
        "-i", f"{url}",
        "-c", "copy",
        "-f", "segment",
        "-segment_list_flags", "+live",
        f"./temp/{screen_id}/{live_id}/%05d.ts"
    ]

    process = Popen(
        command,
        shell=False,
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
                shutdown_video_stream(logger, process, screen_id, live_id, file_title)
                return
        else:
            logger.info(f"The broadcast has ended ({screen_id})")
            event.set()
            logger.info(f"Final processing has been initiated ({screen_id})")
            shutdown_video_stream(logger, process, screen_id, live_id, file_title)
            return


def shutdown_video_stream(logger, process, screen_id, live_id, file_title):
    sleep(2)
    process.terminate()
    final_process = concatenate_segments(screen_id, live_id, file_title)
    final_process.wait()
    utils.delete_segment_directory(screen_id, live_id)
    logger.info(f"FFmpeg shutdown has been completed ({screen_id})")


def concatenate_segments(screen_id, live_id, title):
    # Get all segment files in the directory
    segment_dir = f"./temp/{screen_id}/{live_id}"
    segment_files = sorted(
        [os.path.join(segment_dir, f) for f in os.listdir(segment_dir) if f.endswith(".ts")]
    )

    if not segment_files:
        raise FileNotFoundError(f"No segment files found in {segment_dir}")

    # Create the ffmpeg input string for concat filter
    input_files = "|".join(segment_files)

    command = [
        "ffmpeg",
        "-i", f"concat:{input_files}",  # Use concat filter with input files
        "-c", "copy",
        "-movflags", "faststart",
        f"./outputs/{screen_id}/{title}.mp4"
    ]

    process = Popen(
        command,
        shell=False,
        stdin=PIPE,
        stderr=DEVNULL
    )
    return process


def start_stream_comments(event, url, screen_id, live_id, live_title, live_subtitle):
    asyncio.run(stream_comments(event, url, screen_id, live_id, live_title, live_subtitle))


async def stream_comments(event, url, screen_id, live_id, live_title, live_subtitle):
    logger = logging.getLogger("Comment")

    screen_id = utils.escape_characters(screen_id)
    live_title = utils.escape_characters(live_title)
    live_subtitle = utils.escape_characters(live_subtitle)
    title = utils.get_archive_file_name(live_id, screen_id, live_title, live_subtitle)
    file = open(f"./temp/{screen_id}/{title}.json", "w", encoding="utf-8")
    async with websockets.client.connect(url, user_agent_header=user_agent) as websocket:
        logger.info(f"Comment stream started ({screen_id})")
        try:
            async for data in websocket:
                if event.is_set():
                    file.close()
                    shutil.move(f"./temp/{screen_id}/{title}.json", f"./outputs/{screen_id}/{title}.json")
                    logger.info(f"Comment stream has been closed ({screen_id})")
                    return
                messages = json.loads(data)
                for message in messages:
                    text = json.dumps(message, ensure_ascii=False)
                    file.write(rf"{text}" + "\n")
        except websockets.ConnectionClosed:
            file.close()
            shutil.move(f"./temp/{screen_id}/{title}.json", f"./outputs/{screen_id}/{title}.json")
            logger.info(f"Comment websocket connection has been closed ({screen_id})")


async def stream_notification(url):
    sleep(1)
    logger = logging.getLogger("Notification")
    logger.info(f"TARS-Outpost-Endpoint: {url}")
    logger.info(f"Connecting to Notification Server...")
    while True:
        try:
            async with websockets.client.connect(
                    url,
                    ping_interval=5,
                    ping_timeout=10,
                    extra_headers={"notification-server-access-token": token}
            ) as websocket:
                logger.info("Connected to Notification Server")
                async for data in websocket:
                    message = json.loads(data)
                    screen_id = message['broadcaster']['screen_id']
                    if message["event"] == "livestart":
                        logger.info(f"Received LIVE START Notification ({screen_id})")
                        requests.post(f"http://localhost:{port}/recordings/{screen_id}")
                    elif message["event"] == "liveend":
                        logger.info(f"Received LIVE END Notification ({screen_id})")
        except websockets.ConnectionClosedError as e:
            logger.error(f"Websocket connection has been closed")
            logger.error(f"CODE: {e.code}, Reason: {e.reason}")
            if e.code == 1008:
                logger.error(f"Notification Server authentication failed")
                logger.error(f"Please check NOTIFICATION_SERVER_TOKEN")

        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"Server rejected WebSocket connection: HTTP {e.status_code}")

        logger.info("Wait for 3 seconds...")
        await asyncio.sleep(3)
        logger.info(f"Reconnecting...")


def fetch_scheduler():
    logger = logging.getLogger("Subscriptions")
    sleep(3)
    twitcasting = Twitcasting()

    while True:
        fetch_count = 0
        logger.debug("Retrieving subscriptions...")
        response = requests.get(f"http://localhost:{port}/subscriptions")
        users = response.json()["users"]
        logger.debug(f"{len(users)} user(s) found")
        for user in users:
            database.set_subscription_user(user)

        for user in users:
            fetch_count += 1
            logger.debug(f"Retrieving user_id: [{user}]'s metadata...")
            user_data_response = twitcasting.get_user_info(user)
            if user_data_response[0]:
                logger.debug(f"{user} is {user_data_response[1]['user']['screen_id']}")
                database.update_user(user_data_response[1])

            if fetch_count == 5:
                fetch_count = 0
                sleep(60)
            else:
                sleep(1)