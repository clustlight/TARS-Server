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

        if live_id not in self.events:
            event = self.manager.Event()
            event.set()
            self.events[live_id] = event

        if self.events[live_id].is_set():
            self.events[live_id].clear()
            websocket_url = get_comment_stream_url(live_id)

            self.executor.submit(download, self.events[live_id], url, user_name, live_id, live_title, live_subtitle)
            self.executor.submit(comments, self.events[live_id], websocket_url, user_name, live_id, live_title, live_subtitle)
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
