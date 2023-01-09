import datetime
import os

import requests

user_agent = os.environ.get("USER_AGENT")

def create_output_directory():
    if not os.path.exists("../outputs"):
        os.mkdir("../outputs")

def create_user_directory(user_name):
    if not os.path.exists(f"./outputs/{user_name}"):
        os.mkdir(f"./outputs/{user_name}")

def replace_colon(user_name):
    return user_name.replace(':', '__')

def get_archive_file_name(movie_id, user_name, live_title, live_subtitle):
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"[{now}]-[{live_title}__{live_subtitle}]-[{user_name}]-[{movie_id}]"

def get_comment_stream_url(live_id):
    headers= {
        "User-Agent": user_agent
    }
    data = {"movie_id": live_id}
    files = {(None, None)}
    response = requests.post("https://twitcasting.tv/eventpubsuburl.php", headers=headers, data=data, files=files)
    return response.json()["url"]