from core.application.shared.shared_manager import SharedManager
from core.domain.entities import User
from shared.logging_decorator import log
from core.application.shared.use_cases.shared_use_cases import user_check_existence_or_create


@log
def get_user_or_create_use_case(
        user_use_case: SharedManager,
        user_id: str
) -> User:
    return user_check_existence_or_create(user_use_case, user_id)