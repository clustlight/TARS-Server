import asyncio
import json
import os
import shutil
import logging
import requests
import websockets.client

from utils import escape_characters


def get_comment_stream_url(live_id):
    headers = {
        "User-Agent": os.environ.get("USER_AGENT")
    }
    data = {"movie_id": live_id}
    files = {(None, None)}
    response = requests.post("https://twitcasting.tv/eventpubsuburl.php", headers=headers, data=data, files=files)
    return response.json()["url"]

def start_stream_comments(event, screen_id, websocket_url, file_title):
    asyncio.run(stream_comments(event, screen_id, websocket_url, file_title))


async def stream_comments(event, screen_id, websocket_url, file_title):
    logger = logging.getLogger("Comments")

    screen_id = escape_characters(screen_id)
    file_path = f"./temp/{screen_id}/{file_title}.json"
    output_path = f"./outputs/{screen_id}/{file_title}.json"

    file = open(file_path, "w", encoding="utf-8")
    received_ids = set()

    retry_count = 0
    MAX_RETRIES = 10
    RETRY_INTERVAL = 2
    MAX_RETRY_INTERVAL = 150

    while not event.is_set():
        try:
            async with websockets.client.connect(websocket_url, user_agent_header=os.environ.get("USER_AGENT")) as websocket:
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