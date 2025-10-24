from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Any

from core.application.ports.database import CacheDBConnectionInterface

F = TypeVar('F', bound=Callable[..., Any])

class CachingInterface(ABC):
    @staticmethod
    @abstractmethod
    def cache(func: F) -> F: ...

    @abstractmethod
    def _invalidate_cache(
            self,
            model: str,
            *cache_names: str,
            item_id: str | int | None = None
    ) -> None: ...

    @abstractmethod
    def _get_by_id_cache_invalidation(self, model: str, item_id: str | int) -> None: ...

    @abstractmethod
    def _get_by_custom_fields_cache_invalidation(self, model: str) -> None: ...

    @abstractmethod
    def _get_all_cache_invalidation(self, model: str) -> None: ...

class CacheInterface(ABC):
    @abstractmethod
    def get_user_cache(self, telegram_username: str, field_name: str) -> str: ...

    @abstractmethod
    def get_user_cache_all(self, telegram_username: str) -> dict: ...

    @abstractmethod
    def set_user_cache(self, telegram_username: str, cache_name: str, cache_value: str) -> bool: ...

    @abstractmethod
    def set_task_progress_cache(self, task_id: int, progress: float) -> bool: ...

    @abstractmethod
    def get_task_progress_cache(self, task_id: int) -> float | None: ...

    @abstractmethod
    def drop_task_progress_cache(self, task_id: int) -> bool: ...



