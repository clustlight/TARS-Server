import os
import pathlib
from concurrent.futures import ThreadPoolExecutor

import dotenv
import uvicorn

from tasks.notification import start_websocket_client
from tasks.scheduler import fetch_scheduler
from server import app
import utils
from database import Base, engine
from log import setup_logging


def start_api_server():
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get("PORT")), log_level='info', access_log=False)


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
        executor.submit(fetch_scheduler, os.environ.get("PORT"))


if __name__ == "__main__":
    main()
