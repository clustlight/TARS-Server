from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Manager

from parallel import stream_video, start_stream_comments
from utils import get_stream_url, get_comment_stream_url, get_archive_file_name


class StreamManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=64)
        self.events = {}
        self.manager = Manager()

    def start(self, screen_id, live_id, live_title, live_subtitle):

        if live_id not in self.events:
            event = self.manager.Event()
            event.set()
            self.events[live_id] = event

        if self.events[live_id].is_set():
            self.events[live_id].clear()
            stream_url = get_stream_url(screen_id, self.events[live_id])
            websocket_url = get_comment_stream_url(live_id)

            file_title = get_archive_file_name(live_id, screen_id, live_title, live_subtitle)

            self.executor.submit(stream_video, self.events[live_id], screen_id, live_id, stream_url, file_title)
            self.executor.submit(start_stream_comments, self.events[live_id], screen_id, websocket_url, file_title)
            return True
        else:
            return False

    def stop(self, screen_id):
        if screen_id in self.events:
            self.events[screen_id].set()
            self.events.pop(screen_id)
            return True
        else:
            return False
