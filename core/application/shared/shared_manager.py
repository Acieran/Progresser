from core.application.ports.caching import CacheInterface
from core.application.ports.repositories_interface import BaseRepositoryInterface
from core.application.shared.use_cases.use_case_base_class import UseCase
from core.domain.entities import Entities


class SharedManager(UseCase):
    def __init__(self, db_repository: BaseRepositoryInterface, db_model_dict: dict[type[Entities], ...],
                 cache_repo: CacheInterface):
        super().__init__(db_repository, db_model_dict, cache_repo)