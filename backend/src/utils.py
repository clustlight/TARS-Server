import datetime
import os
import re
import shutil


def create_output_directory():
    if not os.path.exists("../../outputs"):
        os.mkdir("../../outputs")

def create_temp_directory():
    if not os.path.exists("../../temp"):
        os.mkdir("../../temp")


def create_user_directory(screen_id):
    if not os.path.exists(f"./outputs/{screen_id}"):
        os.mkdir(f"./outputs/{screen_id}")

    if not os.path.exists(f"./temp/{screen_id}"):
        os.mkdir(f"./temp/{screen_id}")


def create_segment_directory(screen_id, live_id):
    if not os.path.exists(f"./temp/{screen_id}/{live_id}"):
        os.mkdir(f"./temp/{screen_id}/{live_id}")


def delete_segment_directory(screen_id, live_id):
    if os.path.exists(f"./temp/{screen_id}/{live_id}"):
        shutil.rmtree(f"./temp/{screen_id}/{live_id}")


def escape_characters(text):
    if text is not None:
        return re.sub(r"%|\/|&|\s|;|:", "__", text)
    else:
        return text


def get_archive_file_name(movie_id, screen_id, live_title, live_subtitle):
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')

    screen_id = escape_characters(screen_id)
    live_title = escape_characters(live_title)
    live_subtitle = escape_characters(live_subtitle)

    return f"[{now}]-[{live_title}__{live_subtitle}]-[{screen_id}]-[{movie_id}]"
