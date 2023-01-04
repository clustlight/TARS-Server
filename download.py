from subprocess import Popen, PIPE, DEVNULL
from time import sleep


def download(event, url, name):
    process = Popen(
        ['ffmpeg', '-i', url, '-movflags', 'faststart', '-c', 'copy', '-bsf:a', 'aac_adtstoasc', f"{name}.mp4"],
        shell=True,
        stdin=PIPE,
        stderr=DEVNULL
    )

    while True:
        sleep(5)
        if event.is_set():
            process.communicate(str.encode("q"))
            sleep(5)
            process.terminate()
            return
