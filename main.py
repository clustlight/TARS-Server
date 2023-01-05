from concurrent.futures import ProcessPoolExecutor

import uvicorn

from server import app
import file

def start_api_server():
    uvicorn.run(app, host='0.0.0.0', port=3880, log_level='info')

def start_websocket_client():
    pass

def main():
    file.create_output_directory()
    with ProcessPoolExecutor() as executor:
        executor.submit(start_api_server)
        executor.submit(start_websocket_client)


if __name__ == "__main__":
    main()
