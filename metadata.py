class MetadataManager:
    def __init__(self):
        self.metadata = {}

    def add(self, user_name: str, start_time: int):
        self.metadata[user_name] = {"start_time": start_time}

    def remove(self, user_name: str):
        self.metadata.pop(user_name)

    def get(self, user_name: str):
        return self.metadata.get(user_name)

    def update(self, non_active_users: []):
        for user_name in non_active_users:
            if user_name in self.metadata:
                self.remove(user_name)