from core.application.ports.caching import CacheInterfaceUser
from core.application.ports.database import CacheDBConnectionInterface
from infrastructure.error_handler.errors import InternalRedisError


class CacheRepositoryUser(CacheInterfaceUser):
    def __init__(self, redis_db_manager: CacheDBConnectionInterface):
        self.redis_conn = redis_db_manager.get_connection()
        self.key_base = "user_cache:"

    def get_user_cache_all(self, telegram_username: str) -> dict:
        try:
            key = self.key_base + telegram_username
            return self.redis_conn.hgetall(key)
        except Exception as e:
            raise InternalRedisError(str(e), telegram_username)

    def get_user_cache(self, telegram_username: str, field_name: str) -> str:
        try:
            key = self.key_base + telegram_username
            return self.redis_conn.hget(key, field_name)
        except Exception as e:
            raise InternalRedisError(str(e), telegram_username)


    def set_user_cache(self, telegram_username: str, cache_name: str, cache_value: str) -> bool:
        try:
            key = self.key_base + telegram_username
            self.redis_conn.hset(key, cache_name, cache_value)
            return True
        except Exception as e:
            raise InternalRedisError(str(e), telegram_username)
