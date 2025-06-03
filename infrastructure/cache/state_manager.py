from core.application.ports.caching import CacheInterfaceUser


class StateManager:
    def __init__(self, user_caching: CacheInterfaceUser):
        self.user_caching = user_caching

    def change_state(self, username: str, new_value: str) -> bool:
        return self.user_caching.set_user_cache(username, "state", new_value)

    def get_user_state(self, username: str) -> str:
        return self.user_caching.get_user_cache(username, "state")

    def get_user_cache(self, username: str) -> dict:
        return self.user_caching.get_user_cache_all(username)

    def get_user_current_task(self, username: str) -> str:
        return self.user_caching.get_user_cache(username, "current_task_id")

    def set_user_current_task(self, username: str, current_task_id: str) -> bool:
        return self.user_caching.set_user_cache(username, "current_task_id", current_task_id)