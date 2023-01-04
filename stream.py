from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager


class StreamManager:
    def __init__(self):
        self.executor = ProcessPoolExecutor()
        self.events = {}
        self.manager = Manager()

    def start(self, user_name):
        if user_name not in self.events:
            event = self.manager.Event()
            self.events[user_name] = event
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
