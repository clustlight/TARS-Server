import logging
import os
import pathlib
from concurrent.futures import ProcessPoolExecutor

import uvicorn

from server import app
import utils

def start_api_server():
    uvicorn.run(app, host='0.0.0.0', port=3880, log_level='info')

def start_websocket_client():
    pass

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s  [%(levelname)s] (%(name)s) >> %(message)s')
    os.chdir(os.path.dirname(pathlib.Path(__file__).parent.resolve()))
    utils.create_output_directory()
    with ProcessPoolExecutor() as executor:
        executor.submit(start_api_server)
        executor.submit(start_websocket_client)


if __name__ == "__main__":
    main()
