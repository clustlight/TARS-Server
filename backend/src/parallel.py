import asyncio
import json
import logging
import os
import pathlib
import shutil
import socket
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
                break
        else:
            logger.warning(f"[{retry_count + 1}/{MAX_RETRIES}] Failed to fetch m3u8 playlist. Status code: {res.status_code}")
        sleep(1)
    else:
        logger.error(f"Maximum retries reached. Unable to start recording. ({screen_id})")
        # Signal to stop all related tasks
        event.set()
        return

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

    logger.info(f"Recording has started ({screen_id})")
    while True:
        sleep(1)
        logger.debug(f"Checking recording task... ({screen_id})")
        if process.poll() is None:
            logger.debug(f"The broadcast is active ({screen_id})")
            if event.is_set():
                logger.info(f"Abort signal detected! ({screen_id})")
                logger.info(f"Starting interruption process... ({screen_id})")
                process.communicate(str.encode("q"))
                shutdown_video_stream(logger, process, screen_id, live_id, file_title)
                return
        else:
            logger.info(f"The broadcast has ended ({screen_id})")
            event.set()
            logger.info(f"Finalizing the recording process... ({screen_id})")
            shutdown_video_stream(logger, process, screen_id, live_id, file_title)
            return


def shutdown_video_stream(logger, process, screen_id, live_id, file_title):
    sleep(2)
    process.terminate()
    final_process = concatenate_segments(screen_id, live_id, file_title)
    final_process.wait()
    utils.delete_segment_directory(screen_id, live_id)
    logger.info(f"FFmpeg shutdown process completed ({screen_id})")


def concatenate_segments(screen_id, live_id, title):
    segment_dir = f"./temp/{screen_id}/{live_id}"
    path = pathlib.Path(segment_dir)
    index_file_path = f"{segment_dir}/index.txt"
    with open(index_file_path, 'w') as f:
        for item in sorted(path.glob("*.ts")):
            f.write(f"file {item.name}\n")

    command = [
        "ffmpeg",
        "-f", "concat",
        "-i", index_file_path,
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
    file_path = f"./temp/{screen_id}/{title}.json"
    output_path = f"./outputs/{screen_id}/{title}.json"

    file = open(file_path, "w", encoding="utf-8")
    received_ids = set()

    retry_count = 0
    MAX_RETRIES = 10
    RETRY_INTERVAL = 2
    MAX_RETRY_INTERVAL = 150

    while not event.is_set():
        try:
            async with websockets.client.connect(url, user_agent_header=user_agent) as websocket:
                logger.info(f"Comment stream started ({screen_id})")
                async for data in websocket:
                    if event.is_set():
                        break
                    messages = json.loads(data)
                    for message in messages:
                        message_id = message.get("id")
                        if message_id not in received_ids:
                            received_ids.add(message_id)
                            text = json.dumps(message, ensure_ascii=False)
                            file.write(rf"{text}" + "\n")
                retry_count = 0
                RETRY_INTERVAL = 2
        except websockets.ConnectionClosed:
            logger.warning(f"WebSocket connection closed. Reconnecting... ({screen_id})")
        except Exception as e:
            retry_count += 1
            logger.error(f"Unexpected error: {e}. Reconnecting... ({screen_id}) (Retry {retry_count}/{MAX_RETRIES})")
            if retry_count >= MAX_RETRIES:
                logger.error(f"Maximum retry attempts reached. Exiting comment stream... ({screen_id})")
                break
            await asyncio.sleep(RETRY_INTERVAL)
            RETRY_INTERVAL = min(RETRY_INTERVAL * 2, MAX_RETRY_INTERVAL)
        else:
            await asyncio.sleep(1)

    file.close()
    shutil.move(file_path, output_path)
    logger.info(f"Comment stream has been closed ({screen_id})")


async def stream_notification(url):
    sleep(1)
    logger = logging.getLogger("Notification")
    logger.info(f"TARS-Outpost-Endpoint: {url}")
    logger.info(f"Connecting to Notification Server...")

    max_retries = 5  # Maximum reconnection attempts
    retry_count = 0
    backoff_time = 3  # Initial wait time (seconds)

    while retry_count < max_retries:
        try:
            async with websockets.client.connect(
                url,
                ping_interval=5,
                ping_timeout=10,
                extra_headers={"notification-server-access-token": token}
            ) as websocket:
                logger.info("Connected to Notification Server")
                retry_count = 0  # Reset on successful connection
                async for data in websocket:
                    message = json.loads(data)
                    screen_id = message['broadcaster']['screen_id']
                    if message["event"] == "livestart":
                        logger.info(f"Received LIVE START Notification ({screen_id})")
                        requests.post(f"http://localhost:{port}/recordings/{screen_id}")
                    elif message["event"] == "liveend":
                        logger.info(f"Received LIVE END Notification ({screen_id})")
        except websockets.ConnectionClosedError as e:
            logger.error(f"Websocket connection has been closed. Code: {e.code}, Reason: {e.reason}")
            if e.code == 1008:
                logger.error("Notification Server authentication failed. Please check NOTIFICATION_SERVER_TOKEN.")
                break  # Exit without retrying on authentication error
        except websockets.exceptions.InvalidStatusCode as e:
            logger.error(f"Server rejected WebSocket connection: HTTP {e.status_code}")
        except Exception as e:
            if isinstance(e, OSError) and e.errno == 111:
                logger.error("Connection refused. Please check if the Notification Server is running.")
            elif isinstance(e, socket.gaierror) and e.errno == -2:
                logger.error("Name resolution failed. Please check the server URL or your network connection.")
            else:
                logger.error(f"An unexpected error occurred: {e}")
        finally:
            retry_count += 1
            if retry_count < max_retries:
                logger.info(f"Reconnecting in {backoff_time} seconds... (Attempt {retry_count}/{max_retries})")
                await asyncio.sleep(backoff_time)
                backoff_time *= 2  # Exponentially increase wait time
            else:
                logger.error("Maximum retry attempts reached. Exiting...")
                break


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