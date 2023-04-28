from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager

from parallel import stream_video, start_stream_comments
from utils import get_comment_stream_url


class StreamManager:
    def __init__(self):
        self.executor = ProcessPoolExecutor(max_workers=256)
        self.events = {}
        self.manager = Manager()

    def start(self, screen_id, live_id, live_title, live_subtitle):
        url = f"https://twitcasting.tv/{screen_id}/metastream.m3u8?mode=source"

        if live_id not in self.events:
            event = self.manager.Event()
            event.set()
            self.events[live_id] = event

        if self.events[live_id].is_set():
            self.events[live_id].clear()
            websocket_url = get_comment_stream_url(live_id)

            self.executor.submit(stream_video, self.events[live_id], url, screen_id, live_id, live_title, live_subtitle)
            self.executor.submit(start_stream_comments, self.events[live_id], websocket_url, screen_id, live_id, live_title, live_subtitle)
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
