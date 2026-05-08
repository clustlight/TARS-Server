import logging
import os
import socket
from logging.handlers import RotatingFileHandler, SysLogHandler


def _get_log_level(level_name: str | None, default: int) -> int:
    if not level_name:
        return default

    return getattr(logging, level_name.strip().upper(), default)


def setup_logging():
    log_file_path = "./logs/tars_server.log"
    log_format = os.environ.get("LOG_FORMAT", '').strip() or '%(asctime)s [%(levelname)s] (%(name)s) >> %(message)s'
    log_level = _get_log_level(os.environ.get("LOG_LEVEL"), logging.INFO)
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    file_handler = RotatingFileHandler(
        log_file_path, mode="a", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(log_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)

    logging.basicConfig(
        level=logging.NOTSET,
        format=log_format,
        handlers=[
            file_handler,
            stream_handler,
        ]
    )

    for logger_name in ("websockets", "websockets.client", "websockets.server"):
        logging.getLogger(logger_name).setLevel(logging.INFO)

    # Add SysLogHandler if syslog_address is provided
    syslog_address = os.environ.get("SYSLOG_ADDRESS", '').strip() or None
    syslog_port = int(os.environ.get("SYSLOG_PORT", 514))

    if syslog_address:
        try:
            syslog_handler = SysLogHandler(address=(syslog_address, syslog_port))
            syslog_handler.setLevel(logging.INFO)
            syslog_handler.setFormatter(logging.Formatter(log_format))
            logging.getLogger().addHandler(syslog_handler)
        except Exception as e:
            syslog_logger = logging.getLogger("Syslog")
            syslog_logger.setLevel(logging.INFO)
            if isinstance(e, OSError) and e.errno == 111:
                syslog_logger.error("Connection refused. Please check if the Syslog Server is running.")
            elif isinstance(e, socket.gaierror) and e.errno == -2:
                syslog_logger.error("Name resolution failed. Please check the Syslog Server URL or your network connection.")
            else:
                syslog_logger.error(f"An unexpected error occurred: {e}")