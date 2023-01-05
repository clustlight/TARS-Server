import datetime
import os


def create_output_directory():
    if not os.path.exists("./outputs"):
        os.mkdir("./outputs")

def create_user_directory(user_name):
    if not os.path.exists(f"./outputs/{user_name}"):
        os.mkdir(f"./outputs/{user_name}")

def replace_colon(user_name):
    return user_name.replace(':', '_')

def get_archive_file_name(movie_id, user_name):
    now = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    return f"[{now}]-[{user_name}]-[{movie_id}]"