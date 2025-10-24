from core.domain.entities import Task
from infrastructure.cache.cache_repository import CacheRepository
from shared.logging_decorator import log


class TelegramUserState:
    def __init__(self, user_id: str, cache_repository: CacheRepository):
        self.user_id = user_id
        self.task = Task
        self.breadcrumbs = []
        self.pagination_page = 0
        self._cache_repository = cache_repository
        self._key = "telegram_user_state:" + self.user_id + ":"

    @log
    def get_task(self) -> bool:
        self.task = Task(**self._cache_repository.get_hash(self.user_id, f"user_cache:{self.user_id}"))
        return True

    def set_task(self):
        self._cache_repository.set_hash(self.user_id, self.current_task_id)