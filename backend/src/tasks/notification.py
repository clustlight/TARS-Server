import asyncio
import json
import logging
import os
import requests
import websockets.client
import socket
from time import sleep


def start_websocket_client():
    asyncio.run(
        stream_notification(
            os.environ.get("NOTIFICATION_SERVER_URL"),
            os.environ.get("NOTIFICATION_SERVER_TOKEN"),
            os.environ.get("PORT"),
        )
    )

async def stream_notification(url, token, port):
    """
    Connects to the Notification Server and handles live start/end events.

    Args:
        url (str): The WebSocket URL of the Notification Server.
        token (str): The access token for authentication.
        port (str): The port number for local server communication.
    """
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