import asyncio
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor

import dotenv
import uvicorn

from server import app
import utils
from parallel import stream_notification, fetch_scheduler
from database import Base, engine
from log import setup_logging


def start_api_server():
    port = int(os.environ.get("PORT"))
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info', access_log=False)


def start_websocket_client():
    asyncio.run(stream_notification(os.environ.get("NOTIFICATION_SERVER_URL")))


def main():
    dotenv.load_dotenv()
    os.chdir(os.path.dirname(pathlib.Path(__file__).parent.resolve()))
    setup_logging()

    utils.create_output_directory()
    utils.create_temp_directory()
    Base.metadata.create_all(engine)

    with ThreadPoolExecutor() as executor:
        executor.submit(start_api_server)
        if os.environ.get("AUTO_RECORDING").lower() in ('true', 'enable', 'on'):
            executor.submit(start_websocket_client)
        executor.submit(fetch_scheduler)


if __name__ == "__main__":
    main()
