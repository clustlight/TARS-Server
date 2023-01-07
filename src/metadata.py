class MetadataManager:
    def __init__(self):
        self.metadata = {}

    def add(self, user_name: str, live_title: str, live_subtitle: str, start_time: int):
        self.metadata[user_name] = {
            "live_title": live_title,
            "live_subtitle": live_subtitle,
            "start_time": start_time
        }

    def remove(self, user_name: str):
        self.metadata.pop(user_name)

    def get(self, user_name: str):
        return self.metadata.get(user_name)

    def update(self, non_active_users: []):
        for user_name in non_active_users:
            if user_name in self.metadata:
                self.remove(user_name)