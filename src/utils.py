import datetime
import os
import re

import requests
import pathlib
import shutil

user_agent = os.environ.get("USER_AGENT")


def create_output_directory():
    if not os.path.exists("../outputs"):
        os.mkdir("../outputs")


def create_user_directory(user_name):
    if not os.path.exists(f"./outputs/{user_name}"):
        os.mkdir(f"./outputs/{user_name}")


def create_segment_directory(user_name, live_id):
    if not os.path.exists(f"./outputs/{user_name}/{live_id}"):
        os.mkdir(f"./outputs/{user_name}/{live_id}")


def delete_segment_directory(user_name, live_id):
    if os.path.exists(f"./outputs/{user_name}/{live_id}"):
        shutil.rmtree(f"./outputs/{user_name}/{live_id}")


def create_segment_index(user_name, live_id):
    path = pathlib.Path(f"./outputs/{user_name}/{live_id}")
    with open(f"./outputs/{user_name}/{live_id}/index.txt", 'w') as f:
        for index, item in enumerate(path.glob("*.ts")):
            if index == 0:
                continue
            f.write(f"file {item.name}\n")


def escape_characters(text):
    if text is not None:
        return re.sub(r"%|\/|&|\s|;|:", "__", text)
    else:
        return text


def get_archive_file_name(movie_id, user_name, live_title, live_subtitle):
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"[{now}]-[{live_title}__{live_subtitle}]-[{user_name}]-[{movie_id}]"


def get_comment_stream_url(live_id):
    headers = {
        "User-Agent": user_agent
    }
    data = {"movie_id": live_id}
    files = {(None, None)}
    response = requests.post("https://twitcasting.tv/eventpubsuburl.php", headers=headers, data=data, files=files)
    return response.json()["url"]
