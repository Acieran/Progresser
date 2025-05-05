import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from infrastructure.persistance.sqlalchemy.models import Base, User
from infrastructure.persistance.redis.caching_database_manager import RedisDatabaseManager, SQLDatabaseManager
from infrastructure.persistance.sqlalchemy.base_repository import BaseRepository

sql_string = "sqlite:///:memory:"

@pytest.fixture
def repository():
    manager = SQLDatabaseManager(sql_string)
    repository = BaseRepository(manager, RedisDatabaseManager())
    yield repository
    Base.metadata.drop_all(manager.engine)

def test_create_success(repository):
    session = repository.db_manager.get_session()
    user = User(username="Acie", active=True, telegram_username="Acie")

    repository.create(User, **user.to_dict())

    created_user = session.get(User, user.username)  #get(User, user.username)
    assert isinstance(created_user, User)
    assert user.to_dict() == created_user.to_dict()

def test_create_failure(repository):
    user = User(username="Acie", active=True, telegram_username="Acie")

    with pytest.raises(IntegrityError):
        repository.create(User, **user.to_dict())
        repository.create(User, **user.to_dict())

def test_create_transactional_success(repository):
    session = repository.db_manager.get_session()
    user1 = User(username="Acie1", active=True, telegram_username="Acie1")
    user2 = User(username="Acie2", active=True, telegram_username="Acie2")

    with repository.transaction():
        repository.create(User, **user1.to_dict())
        created_user = session.get(User, user1.username)
        assert created_user is None
        repository.create(User, **user2.to_dict())
        created_user = session.get(User, user2.username)
        assert created_user is None

    created_user = session.get(User, user1.username)
    assert isinstance(created_user, User)
    assert user1.to_dict() == created_user.to_dict()
    created_user = session.get(User, user2.username)
    assert isinstance(created_user, User)
    assert created_user.to_dict() == user2.to_dict()

def test_update_success(repository):
    session = repository.db_manager.get_session()
    user = User(username="Acie1", active=True, telegram_username="Acie1")

    repository.create(User, **user.to_dict())
    user.telegram_username = "Acie2"
    result = repository.update(User, user.username, **user.to_dict())
    assert result is True

    created_user = session.get(User, user.username)

    assert isinstance(created_user, User)
    assert user.to_dict() == created_user.to_dict()

def test_update_user_not_found(repository):
    user = User(username="Acie1", active=True, telegram_username="Acie1")

    result = repository.update(User, user.username, **user.to_dict())
    assert result is False

def test_update_transactional_success(repository):
    user = User(username="Acie1", active=True, telegram_username="Acie1")
    updated_user = User(username="Acie1", active=True, telegram_username="Acie2")
    repository.create(User, **user.to_dict())

    with repository.transaction():
        result = repository.update(User, user.username, **updated_user.to_dict())
        created_user = repository.db_manager.get_session().get(User, user.username)
        assert result is True
        assert isinstance(created_user, User)
        assert created_user.to_dict() == user.to_dict()

    created_user = repository.db_manager.get_session().get(User, user.username)
    assert isinstance(created_user, User)
    assert updated_user.to_dict() == created_user.to_dict()

def test_get_by_id_success(repository):
    user = User(username="Acie1", active=True, telegram_username="Acie1")

    repository.create(User, **user.to_dict())
    user_from_db = repository.get_by_id(User, user.username)

    assert user.to_dict() == user_from_db


def test_get_by_id_not_exists(repository):
    user_from_db = repository.get_by_id(User, 123)

    assert user_from_db is None


def test_get_by_id_transactional_success(repository):
    user = User(username="Acie1", active=True, telegram_username="Acie1")

    with repository.transaction():
        repository.create(User, **user.to_dict())
        user_from_db = repository.get_by_id(User, user.username)
        assert user_from_db is None

    user_from_db = repository.get_by_id(User, user.username)
    assert user.to_dict() == user_from_db

def test_get_by_custom_fields_success(repository):
    user = User(username="Acie1", active=True, telegram_username="Acie1")

    repository.create(User, **user.to_dict())
    user_from_db = repository.get_by_custom_fields(User, telegram_username = "Acie1")

    assert [user.to_dict()] == user_from_db

    user_from_db = repository.get_by_custom_fields(User, telegram_username="Acie1", active = True)
    assert [user.to_dict()] == user_from_db

def test_get_by_custom_fields_failure(repository):
    with pytest.raises(SQLAlchemyError):
        repository.get_by_custom_fields(User, non_existent_field="Acie1")

def test_delete_success(repository):
    user = User(username="Acie", active=True, telegram_username="Acie")
    repository.create(User, **user.to_dict())
    session = repository.db_manager.get_session()

    result = repository.delete(User, item_id="Acie")
    assert result is True

    created_user = session.get(User, "Acie")
    assert created_user is None

def test_delete_failure(repository):
    result = repository.delete(User, item_id="Acie")
    assert result is False

def test_delete_transactional_success(repository):
    user = User(username="Acie", active=True, telegram_username="Acie")
    repository.create(User, **user.to_dict())

    with repository.transaction():
        result = repository.delete(User, item_id="Acie")
        assert result is True

        created_user = repository.db_manager.get_session().get(User, "Acie")
        assert isinstance(created_user, User)
        assert created_user.to_dict() == user.to_dict()

    created_user = repository.db_manager.get_session().get(User, "Acie")
    assert created_user is None

def test_get_all_success(repository):
    user1 = User(username="Acie1", active=True, telegram_username="Acie1")
    user2 = User(username="Acie2", active=True, telegram_username="Acie2")

    repository.create(User, **user1.to_dict())
    repository.create(User, **user2.to_dict())
    users_from_db = repository.get_all(User)

    assert [user1.to_dict(), user2.to_dict()] == users_from_db

def test_get_all_failure(repository):
    users_from_db = repository.get_all(User)

    assert [] == users_from_db
