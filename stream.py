from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

from download import download


class StreamManager:
    def __init__(self):
        self.executor = ProcessPoolExecutor()
        self.events = {}
        self.manager = Manager()

    def start(self, user_name):
        if user_name not in self.events:
            url = f"https://twitcasting.tv/{user_name}/metastream.m3u8?mode=source"
            event = self.manager.Event()
            self.events[user_name] = event
            self.executor.submit(download, event, url, user_name)
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
