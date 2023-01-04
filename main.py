import uvicorn

from server import app


def main():
    uvicorn.run(app, host='0.0.0.0', port=3880, log_level='info')


if __name__ == "__main__":
    main()
