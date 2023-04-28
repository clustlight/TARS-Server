import asyncio
import logging
import os
import pathlib
from concurrent.futures import ProcessPoolExecutor

import dotenv
import uvicorn

from server import app
import utils
from parallel import stream_notification, fetch_scheduler
from database import Base, engine


def start_api_server():
    port = int(os.environ.get("PORT"))
    uvicorn.run(app, host='0.0.0.0', port=port, log_level='info', access_log=False)


def start_websocket_client():
    asyncio.run(stream_notification(os.environ.get("NOTIFICATION_SERVER_URL")))


def main():
    dotenv.load_dotenv()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s  [%(levelname)s] (%(name)s) >> %(message)s')

    os.chdir(os.path.dirname(pathlib.Path(__file__).parent.resolve()))

    utils.create_output_directory()
    Base.metadata.create_all(engine)

    with ProcessPoolExecutor() as executor:
        executor.submit(start_api_server)
        executor.submit(start_websocket_client)
        executor.submit(fetch_scheduler)


if __name__ == "__main__":
    main()
