from sqlalchemy import exc

from database.database_manager import SQLDatabaseManager
from database.repositories.base_repository import BaseRepository
from core.models_sql_alchemy.models import User, UserState


class UserRepository(BaseRepository):
    def __init__(self, db_manager:SQLDatabaseManager):
        super().__init__(db_manager)
        self.model = User

    @BaseRepository.transaction_decorator
    def create_user(self, username: str):
        """Creates a new record in the database."""
        try:
            self.create(username=username, telegram_username=username)
            self.model = UserState
            self.create(telegram_username=username)
            self.model = User
        except exc.SQLAlchemyError as e:
            raise e