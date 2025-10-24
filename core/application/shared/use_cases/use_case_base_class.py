from core.application.ports.caching import CacheInterface
from core.application.ports.repositories_interface import BaseRepositoryInterface
from core.domain.entities import Entities


class UseCase:
    def __init__(
            self,
            db_repository: BaseRepositoryInterface,
            db_model_dict: dict[type[Entities], ...],
            cache_repo: CacheInterface,
    ):
        self.db_repository = db_repository
        self.db_model_dict = db_model_dict
        self.cache_repo = cache_repo