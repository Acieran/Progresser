from abc import ABC, abstractmethod
from typing import Any


class BaseRepositoryInterface(ABC):
    @abstractmethod
    def transaction(self): ...

    @abstractmethod
    def create(self, model: type, **kwargs) -> str | int | None: ...

    @abstractmethod
    def update(self, model: type, item_id: str | int, **data) -> bool: ...

    @abstractmethod
    def delete(self, model: type, item_id: str | int) -> bool: ...

    @abstractmethod
    def get_by_id(self, model: type, item_id: str | int) -> dict[str,Any] | None: ...

    @abstractmethod
    def get_by_custom_fields(self, model: type, **kwargs) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_all(self, model: type) -> list[dict[str, Any]]: ...