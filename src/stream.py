from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

from download import download, comments
from utils import get_comment_stream_url


class StreamManager:
    def __init__(self):
        self.executor = ProcessPoolExecutor()
        self.events = {}
        self.manager = Manager()

    def start(self, user_name, live_id, live_title, live_subtitle):
        url = f"https://twitcasting.tv/{user_name}/metastream.m3u8?mode=source"

        if user_name not in self.events:
            event = self.manager.Event()
            event.set()
            self.events[user_name] = event

        if self.events[user_name].is_set():
            self.events[user_name].clear()
            websocket_url = get_comment_stream_url(live_id)

            self.executor.submit(download, self.events[user_name], url, user_name, live_id, live_title, live_subtitle)
            self.executor.submit(comments, self.events[user_name], websocket_url, user_name, live_id, live_title, live_subtitle)
            return True
        else:
            return False

    def stop(self, user_name):
        if user_name in self.events:
            self.events[user_name].set()
            self.events.pop(user_name)
            return True
        else:
            return False
