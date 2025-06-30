from core.application.ports.caching import CacheInterface
from core.application.ports.repositories import BaseRepositoryInterface
from core.application.shared.shared_manager import SharedManager
from core.application.users.use_cases.get_user_use_case import get_user_use_case
from core.application.users.use_cases.get_user_or_create_use_case import get_user_or_create_use_case
from core.domain.entities import Entities


class UserManager(SharedManager):
    get_user_use_case = get_user_use_case
    get_user_or_create_use_case = get_user_or_create_use_case

    def __init__(self, db_repository: BaseRepositoryInterface, db_model_dict: dict[type[Entities], ...],
                 cache_repo: CacheInterface):
        super().__init__(db_repository, db_model_dict, cache_repo)