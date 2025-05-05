import redis

from core.application.ports.database import CacheInterface


class CachingDatabaseManager(CacheInterface):
    def __init__(self,
                 host : str ='localhost',
                 port: int = 6379,
                 db: int = 0,
                 username: str = 'default',
                 password: str = 'null',
                 ):
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            username=username,
            password=password)
        self._username = username
        self._password = password

    def get_connection(self) -> redis.Redis:
        """Get a Redis connection from the pool."""
        return redis.Redis(
            decode_responses=True,
            connection_pool=self._pool,
        )
