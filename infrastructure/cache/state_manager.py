from infrastructure.cache.cache_repository import CacheRepository
from shared.logging_decorator import log


class StateManager:
    def __init__(self, user_caching: CacheRepository):
        self.user_caching = user_caching

    @log
    def change_state(self, username: str, new_value: str) -> bool:
        return self.user_caching.set_user_cache(username, "state", new_value)

    @log
    def get_user_state(self, username: str) -> str | None:
        return self.user_caching.get_user_cache(username, "state")

    @log
    def get_user_cache(self, username: str) -> dict:
        return self.user_caching.get_user_cache_all(username)

    @log
    def get_user_current_task(self, username: str) -> str:
        return self.user_caching.get_user_cache(username, "current_task_id")

    @log
    def set_user_current_task(self, username: str, current_task_id: str) -> bool:
        return self.user_caching.set_user_cache(username, "current_task_id", current_task_id)

    @log
    def get_user_current_task_fields(self, telegram_username: str) -> dict:
        return self.user_caching.get_user_task_fields_cache(telegram_username=telegram_username)

    @log
    def set_user_current_task_fields(self, username: str, **fields: dict) -> bool:
        return self.user_caching.set_user_task_fields_cache(telegram_username=username, cache_dict=fields)

    @log
    def clear_user_current_task(self, username: str) -> bool:
        return self.user_caching.clear_user_task_fields_cache(telegram_username=username)