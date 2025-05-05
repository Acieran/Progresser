from abc import ABC, abstractmethod

class DatabaseInterface(ABC):
    @abstractmethod
    def get_session(self): ...

class CacheInterface(ABC):
    @abstractmethod
    def get_connection(self): ...