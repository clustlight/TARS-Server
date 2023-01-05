from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

from src.download import download


class StreamManager:
    def __init__(self):
        self.executor = ProcessPoolExecutor()
        self.events = {}
        self.manager = Manager()

    def start(self, user_name):
        url = f"https://twitcasting.tv/{user_name}/metastream.m3u8?mode=source"

        if user_name not in self.events:
            event = self.manager.Event()
            event.set()
            self.events[user_name] = event

        if self.events[user_name].is_set():
            self.events[user_name].clear()
            self.executor.submit(download, self.events[user_name], url, user_name)
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
