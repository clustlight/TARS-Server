class MetadataManager:
    def __init__(self):
        self.metadata = {}

    def add(self, screen_id: str, user_name: str, profile_image: str, live_id: str, live_title: str, live_subtitle: str, start_time: int):
        self.metadata[live_id] = {
            "screen_id": screen_id,
            "user_name": user_name,
            "profile_image": profile_image,
            "live_title": live_title,
            "live_subtitle": live_subtitle,
            "start_time": start_time
        }

    def remove(self, live_id: str):
        self.metadata.pop(live_id)

    def get(self, live_id: str):
        return self.metadata.get(live_id)

    def update(self, non_active_streams: []):
        for live_id in non_active_streams:
            if live_id in self.metadata:
                self.remove(live_id)
