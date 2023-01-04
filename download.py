from subprocess import Popen, PIPE, DEVNULL
from time import sleep


def download(event, url, name):
    process = Popen(
        f"exec ffmpeg -i {url} -movflags faststart -c copy -bsf:a aac_adtstoasc {name}.mp4",
        shell=True,
        stdin=PIPE
    )

    while True:
        sleep(3)
        if event.is_set():
            process.communicate(str.encode("q"))
            sleep(3)
            process.terminate()
            return