from typing import Literal

from sqlalchemy import exc

from core.models_sql_alchemy.models import User, UserState
from database.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository):
    @BaseRepository.transaction_decorator
    def create(self, username: str) -> Literal[True]:
        """Creates a new record in the database."""
        try:
            super().create(User, username=username, telegram_username=username)
            super().create(UserState, telegram_username=username)
            return True
        except exc.SQLAlchemyError as e:
            raise e
