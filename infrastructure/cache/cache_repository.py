from core.application.ports.caching import CacheInterface
from core.application.ports.database import CacheDBConnectionInterface
from infrastructure.error_handler.errors import InternalRedisError
from shared.logging_decorator import log

sec_from_day = 60 * 60 * 24
sec_from_hour = 60 * 60

class CacheRepository(CacheInterface):
    def __init__(self, redis_db_manager: CacheDBConnectionInterface):
        self.redis_conn = redis_db_manager.get_connection()
        self.user_key_base = "user_cache"

    @log
    def set_hash(self, user_id: str, value_dict: dict, key: str) -> bool:
        try:
            self.redis_conn.hset(key, mapping=value_dict)
            return True
        except Exception as e:
            raise InternalRedisError(str(e), user_id)

    @log
    def get_hash(self, user_id: str, key: str) -> dict:
        try:
            result = None
            if self.redis_conn.exists(key):
                 result = self.redis_conn.hgetall(key)
            if isinstance(result, bytes):
                result = result.decode("utf-8")
            return result
        except Exception as e:
            raise InternalRedisError(str(e), user_id)

    @log
    def clear_hash(self, user_id: str, key: str) -> bool:
        try:
            self.redis_conn.hdel(key)
            return True
        except Exception as e:
            raise InternalRedisError(str(e), user_id)

    @log
    def get_user_cache_all(self, telegram_username: str) -> dict:
        try:
            key = self.user_key_base + telegram_username
            res_dict = self.redis_conn.hgetall(key)
            for key, value in res_dict.items():
                res_dict[key] = value.decode("utf-8")
            return res_dict
        except Exception as e:
            raise InternalRedisError(str(e), telegram_username)

    @log
    def get_user_cache(self, telegram_username: str, field_name: str) -> str | None:
        try:
            key = self.user_key_base + telegram_username
            if result := self.redis_conn.hget(key, field_name):
                result = result.decode("utf-8")
            return result
        except Exception as e:
            raise InternalRedisError(str(e), telegram_username)

    @log
    def set_user_cache(self, telegram_username: str, cache_name: str, cache_value: str) -> bool:
        try:
            key = self.user_key_base + telegram_username
            self.redis_conn.hset(key, cache_name, cache_value)
            return True
        except Exception as e:
            raise InternalRedisError(str(e), telegram_username)

    @log
    def set_task_progress_cache(self, task_id: int, progress: float) -> bool:
        try:
            key = f"task_progress:{task_id}"
            self.redis_conn.setex(key, 1 * sec_from_day, progress)
            return True
        except Exception as e:
            raise InternalRedisError(f"error setting task progress in task_id:{task_id}\n{str(e)}")


    @log
    def get_task_progress_cache(self, task_id: int) -> float | None:
        try:
            key = f"task_progress:{task_id}"
            if result := self.redis_conn.get(key):
                result = float(result.decode("utf-8"))
            return result
        except Exception as e:
            raise InternalRedisError(f"error getting task progress in task_id:{task_id}\n{str(e)}")

    @log
    def drop_task_progress_cache(self, task_id: int) -> bool:
        try:
            key = f"task_progress:{task_id}"
            self.redis_conn.delete(key)
            return True
        except Exception as e:
            raise InternalRedisError(f"error dropping task progress in task_id:{task_id}\n{str(e)}")