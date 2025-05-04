import logging
import os
import socket
from logging.handlers import RotatingFileHandler, SysLogHandler


def setup_logging():
    log_file_path = "./logs/tars_server.log"
    log_format = os.environ.get("LOG_FORMAT", '').strip() or '%(asctime)s [%(levelname)s] (%(name)s) >> %(message)s'
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            RotatingFileHandler(
                log_file_path, mode="a", maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
            ),
            logging.StreamHandler()
        ]
    )

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