import datetime
from subprocess import Popen, PIPE, DEVNULL
from time import sleep


def download(event, url, name):
    process = Popen(
        f"exec ffmpeg -i {url} -movflags faststart -c copy -bsf:a aac_adtstoasc {name}.mp4",
        shell=True,
        stdin=PIPE,
        stderr=DEVNULL
    )

    while True:
        sleep(3)
        print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')}:{name}: checking...")
        if process.poll() is None:
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')}:{name}: Stream is Ongoing")
            if event.is_set():
                print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')}:{name}: Detect Abort Signal!")
                print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')}:{name}: Initialize ending process....")
                process.communicate(str.encode("q"))
                sleep(3)
                process.terminate()
                print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')}:{name}: FFmpeg shutdown complete")
                return
        else:
            print(f"{datetime.datetime.now().strftime('%H:%M:%S.%f')}:{name}: Stream is Closed")
            event.set()
            sleep(3)
            process.terminate()
            return