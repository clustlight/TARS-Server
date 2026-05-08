from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Manager
from typing import Any

from tasks.comments import get_comment_stream_url, start_stream_comments
from tasks.video import get_video_stream_url, stream_video
from utils import get_archive_file_name


@dataclass(slots=True)
class RecordingSession:
    screen_id: str
    user_name: str
    profile_image: str
    live_id: str
    live_title: str
    live_subtitle: str
    start_time: int
    event: Any


class StreamManager:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=64)
        self.manager = Manager()
        self.sessions = {}

    def _create_session(
        self,
        screen_id,
        user_name,
        profile_image,
        live_id,
        live_title,
        live_subtitle,
        start_time,
    ):
        event = self.manager.Event()
        event.set()
        return RecordingSession(
            screen_id=screen_id,
            user_name=user_name,
            profile_image=profile_image,
            live_id=live_id,
            live_title=live_title,
            live_subtitle=live_subtitle,
            start_time=start_time,
            event=event,
        )

    def _start_session_workers(self, session):
        stream_url = get_video_stream_url(session.screen_id, session.event)
        websocket_url = get_comment_stream_url(session.live_id)
        file_title = get_archive_file_name(
            session.live_id,
            session.screen_id,
            session.live_title,
            session.live_subtitle,
        )

        self.executor.submit(
            stream_video,
            session.event,
            session.screen_id,
            session.live_id,
            stream_url,
            file_title,
        )
        self.executor.submit(
            start_stream_comments,
            session.event,
            session.screen_id,
            websocket_url,
            file_title,
        )

    def _remove_inactive_sessions(self):
        inactive_live_ids = [
            live_id for live_id, session in self.sessions.items() if session.event.is_set()
        ]
        for live_id in inactive_live_ids:
            self.sessions.pop(live_id, None)

    def list_active_sessions(self):
        self._remove_inactive_sessions()
        return list(self.sessions.values())

    def get_session(self, live_id):
        self._remove_inactive_sessions()
        return self.sessions.get(live_id)

    def start(self, screen_id, user_name, profile_image, live_id, live_title, live_subtitle, start_time):
        session = self.sessions.get(live_id)
        if session is None:
            session = self._create_session(
                screen_id,
                user_name,
                profile_image,
                live_id,
                live_title,
                live_subtitle,
                start_time,
            )
            self.sessions[live_id] = session

        if not session.event.is_set():
            return False

        session.event.clear()
        self._start_session_workers(session)
        return True

    def stop(self, live_id):
        session = self.sessions.get(live_id)
        if session is None:
            return False

        session.event.set()
        self.sessions.pop(live_id, None)
        return True
