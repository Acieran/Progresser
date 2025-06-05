from core.application.ports.repositories import BaseRepositoryInterface
from core.application.tasks.shared import user_check_existence_and_return
from core.domain.entities import Entities
from shared.logging_decorator import log


@log
def get_user_use_case(
        db_repository: BaseRepositoryInterface,
        bd_model_dict: dict[type[Entities], ...],
        user_id: str
) -> dict:
    return user_check_existence_and_return(db_repository, bd_model_dict, user_id).__dict__

