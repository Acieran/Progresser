from abc import ABC, abstractmethod

from redis import Redis


class DatabaseInterface(ABC):
    @abstractmethod
    def get_session(self): ...

class CacheDBConnectionInterface(ABC):
    @abstractmethod
    def get_connection(self) -> Redis: ...