from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Any

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
