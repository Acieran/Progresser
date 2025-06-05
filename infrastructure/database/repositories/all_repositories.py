from typing import Literal

from sqlalchemy import exc

from infrastructure.database_access_managers.sqlalchemy.models import User
from infrastructure.database.repositories.base_repository import BaseRepository
from shared.logging_decorator import log


# class UserRepository(BaseRepository):
#     @BaseRepository.transaction_decorator
#     @log
#     def create(self, username: str) -> Literal[True]:
#         """Creates a new record in the database."""
#         try:
#             super().create(User, username=username, telegram_username=username)
#             super().create(UserState, telegram_username=username)
#             return True
#         except exc.SQLAlchemyError as e:
#             raise e
