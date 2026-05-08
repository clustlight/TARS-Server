import os
import pathlib
import re
from subprocess import Popen, PIPE, DEVNULL
from time import sleep

import utils
import logging

from twitcasting_stream import TwitcastingStreamClient


stream_client = TwitcastingStreamClient()


def has_filler_init_map(playlist_content):
    current_init_number = None

    for line in playlist_content.splitlines():
        stripped_line = line.strip()
        if not stripped_line:
            continue

        init_match = re.search(r'init\.(-?\d+)\.mp4', stripped_line)
        if init_match:
            current_init_number = init_match.group(1)
            continue

        if stripped_line.startswith("#"):
            continue

        return current_init_number == "-1"

    return True


def get_video_stream_url(screen_id, event):
    logger = logging.getLogger("Video")
    response = stream_client.get_stream_server(screen_id)

    streams = response.get("tc-hls", {}).get("streams", {})
    url = streams.get("high") or streams.get("medium") or streams.get("low")

    if not url:
        logger.error("No valid stream URL found.")
        return

    # A filler is streamed on the server side until the broadcast starts.
    # Wait until the playlist switches away from init.-1.mp4 before starting the recording.

    MAX_RETRIES = 60
    for retry_count in range(MAX_RETRIES):
        logger.debug(f"[{retry_count + 1}/{MAX_RETRIES}] Checking m3u8 playlist... ({screen_id})")
        res = stream_client.get_playlist(url)
        if res.status_code == 200:
            logger.debug(f"[{retry_count + 1}/{MAX_RETRIES}] Successfully fetched m3u8 playlist. ({screen_id})")
            playlist_content = res.content.decode("utf-8")
            if not has_filler_init_map(playlist_content):
                logger.debug(f"Playlist switched away from init.-1.mp4. Starting recording. ({screen_id})")
                return url
        else:
            logger.warning(f"[{retry_count + 1}/{MAX_RETRIES}] Failed to fetch m3u8 playlist. Status code: {res.status_code}")
        sleep(1)
    else:
        logger.error(f"Maximum retries reached. Unable to start recording. ({screen_id})")
        # Signal to stop all related tasks
        event.set()
        return


def stream_video(event, screen_id, live_id, stream_url, file_title):
    logger = logging.getLogger("Video")

    screen_id = utils.escape_characters(screen_id)
    utils.create_segment_directory(screen_id, live_id)

    command = [
        "ffmpeg",
        "-user_agent", os.environ.get("USER_AGENT"),
        "-http_persistent", "0",
        "-i", stream_url,
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