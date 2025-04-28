import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import database_manager
from database.database_manager import SQLDatabaseManager
from core.models_sql_alchemy.models import User, Base
from database.repositories.base_repository import BaseRepository

sql_string = "sqlite:///:memory:"

@pytest.fixture
def repository():
    manager = SQLDatabaseManager(sql_string)
    repository = BaseRepository(manager)
    yield repository
    Base.metadata.drop_all(manager.engine)

def test_create_base_repository_success(repository):
    session = repository.get_session()
    user = User(username="Acie", active=True, telegram_username="Acie")

    repository.create(User, **user.object_to_dict())

    created_user = session.get(User, user.username)
    assert user.object_to_dict() == created_user.object_to_dict()

def test_create_user_repository_failure(db_user_setup):
    rep, session, user = db_user_setup

    with pytest.raises(IntegrityError):
        rep.create(User, **user.object_to_dict())
        rep.create(User, **user.object_to_dict())

def test_transaction_create_base_repository_success(repository):
    session = repository.get_session()
    user1 = User(username="Acie1", active=True, telegram_username="Acie1")
    user2 = User(username="Acie2", active=True, telegram_username="Acie2")

    with repository.transaction():
        repository.create(User, **user1.object_to_dict())
        created_user = session.get(User, user1.username)
        assert created_user is None
        repository.create(User, **user2.object_to_dict())
        created_user = session.get(User, user2.username)
        assert created_user is None

    created_user1 = session.get(User, user1.username)
    assert user1.object_to_dict() == created_user1.object_to_dict()
    created_user = session.get(User, user2.username)
    assert created_user.object_to_dict() == user2.object_to_dict()


def delete_created_user(session: Session):
    created_user = session.get(User, "Rol")
    session.delete(created_user)
    session.commit()