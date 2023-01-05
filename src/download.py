import logging
from subprocess import Popen, PIPE, DEVNULL
from time import sleep

import utils

logger = logging.getLogger(__name__)

def download(event, url, user_name):
    user_name = utils.replace_colon(user_name)
    utils.create_user_directory(user_name)

    title = utils.get_archive_file_name("ID_INSERT_HERE", user_name)
    process = Popen(
        f"exec ffmpeg -i {url} -movflags faststart -c copy -bsf:a aac_adtstoasc ./outputs/{user_name}/{title}.mp4",
        shell=True,
        stdin=PIPE,
        stderr=DEVNULL
    )

    while True:
        sleep(1)
        logger.debug(f"Checking Recording Tasks... ({user_name})")
        if process.poll() is None:
            logger.debug(f"The broadcast is ongoing ({user_name})")
            if event.is_set():
                logger.debug(f"Detect abort signals! ({user_name})")
                logger.debug(f"Started interruption process.... ({user_name})")
                process.communicate(str.encode("q"))
                sleep(3)
                process.terminate()
                logger.debug(f"FFmpeg shutdown has been completed ({user_name})")
                return
        else:
            logger.debug(f"The broadcast has ended ({user_name})")
            event.set()
            logger.debug(f"Final processing has been initiated ({user_name})")
            sleep(3)
            process.terminate()
            logger.debug(f"FFmpeg shutdown has been completed ({user_name})")
            return