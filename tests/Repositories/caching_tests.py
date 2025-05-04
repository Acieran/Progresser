import json

import pytest
from sqlalchemy.orm import Session

from core.models_sql_alchemy.models import Base, User
from database.database_manager import RedisDatabaseManager, SQLDatabaseManager
from database.repositories.base_repository import BaseRepository


@pytest.fixture
def repository():
    """Repository with mocked SQL methods"""
    manager = SQLDatabaseManager("sqlite:///:memory:")
    repo = BaseRepository(
        db_manager=manager,
        redis_db_manager=RedisDatabaseManager(
            host='redis-11535.c328.europe-west3-1.gce.redns.redis-cloud.com',
            port=11535,
            username="default",
            password="fLD2Xy30tvitpF9KfUPTCpzvEGdkTL7r",
            )
    )

    yield repo

    repo.redis_db_manager.get_connection().flushdb()
    Base.metadata.drop_all(manager.engine)

def test_get_by_id_cache(repository, mocker):
    user = User(username="1", active=True, telegram_username="1")
    repository.create(User, **user.to_dict())
    spy = mocker.spy(Session, "get")
    user_from_db = repository.get_by_id(User, "1")
    spy.assert_called_once()

    redis_key = f"get_by_id:user:item_id:{user.username}"
    cached_data = repository.redis_db_manager.get_connection().get(redis_key)
    assert json.loads(cached_data) == user_from_db

    user_from_db_cached = repository.get_by_id(User, "1")
    spy.assert_called_once()
    assert user_from_db_cached == user_from_db

def test_get_by_custom_fields_cache_one_record(repository, mocker):
    user = User(username="1", active=True, telegram_username="1")
    repository.create(User, **user.to_dict())
    spy = mocker.spy(Session, "execute")
    user_from_db = repository.get_by_custom_fields(User, telegram_username="1")
    spy.assert_called_once()

    redis_key = f"get_by_custom_fields:user:telegram_username:{user.telegram_username}"
    cached_data = repository.redis_db_manager.get_connection().get(redis_key)
    assert json.loads(cached_data) == user_from_db

    user_from_db_cached = repository.get_by_custom_fields(User, telegram_username="1")
    spy.assert_called_once()
    assert user_from_db_cached == user_from_db

def test_get_by_custom_fields_cache_multiple_records(repository, mocker):
    user1 = User(username="1", active=True, telegram_username="1")
    user2 = User(username="2", active=True, telegram_username="2")
    repository.create(User, **user1.to_dict())
    repository.create(User, **user2.to_dict())
    spy = mocker.spy(Session, "execute")
    user_from_db = repository.get_by_custom_fields(User, active=True)
    spy.assert_called_once()

    redis_key = f"get_by_custom_fields:user:active:{user1.active}"
    cached_data = repository.redis_db_manager.get_connection().get(redis_key)
    assert json.loads(cached_data) == user_from_db

    user_from_db_cached = repository.get_by_custom_fields(User, active=True)
    spy.assert_called_once()
    assert user_from_db_cached == user_from_db

def test_get_all_cache(repository, mocker):
    users = []
    for i in range(5):
        users.append(User(username=str(i), active=True, telegram_username=str(i)))
        repository.create(User, **users[i].to_dict())
    spy = mocker.spy(Session, "execute")
    user_from_db = repository.get_all(User)
    spy.assert_called_once()

    redis_key = "get_all:user"
    cached_data = repository.redis_db_manager.get_connection().get(redis_key)
    assert json.loads(cached_data) == user_from_db

    user_from_db_cached = repository.get_all(User)
    spy.assert_called_once()
    assert user_from_db_cached == user_from_db

def test_create_cache_invalidation(repository, mocker):
    redis_conn = repository.redis_db_manager.get_connection()
    redis_get_all_key = "get_all:user"
    redis_get_by_custom_fields_key = "get_by_custom_fields:user"
    redis_conn.set(redis_get_all_key, json.dumps([1, 2, 3]))
    redis_conn.set(redis_get_by_custom_fields_key, json.dumps([1, 2, 3]))

    user = User(username="1", active=True, telegram_username="1")
    repository.create(User, **user.to_dict())

    assert len(redis_conn.keys(redis_get_all_key)) == 0
    assert len(redis_conn.keys(f"{redis_get_by_custom_fields_key}*")) == 0

def test_update_cache_invalidation(repository):
    redis_conn = repository.redis_db_manager.get_connection()
    redis_get_all_key = "get_all:user"
    redis_get_by_custom_fields_key = "get_by_custom_fields:user"
    redis_get_by_id_key_1 = "get_by_id:user:item_id:1"
    redis_get_by_id_key_2 = "get_by_id:user:item_id:2"
    redis_conn.set(redis_get_all_key, json.dumps([1, 2, 3]))
    redis_conn.set(redis_get_by_custom_fields_key, json.dumps([1, 2, 3]))
    redis_conn.set(redis_get_by_id_key_1, json.dumps([1, 2, 3]))
    redis_conn.set(redis_get_by_id_key_2, json.dumps([1, 2, 3]))


    user = User(username="1", active=True, telegram_username="1")
    repository.create(User, **user.to_dict())
    updated_user = User(username="1", active=True, telegram_username="2")
    repository.update(User, user.username, **updated_user.to_dict())

    assert len(redis_conn.keys(redis_get_all_key)) == 0
    assert len(redis_conn.keys(f"{redis_get_by_custom_fields_key}*")) == 0
    assert len(redis_conn.keys(f"{redis_get_by_id_key_1}*")) == 0
    assert len(redis_conn.keys(f"{redis_get_by_id_key_2}*")) == 1

def test_delete_cache_invalidation(repository):
    user = User(username="1", active=True, telegram_username="1")
    repository.create(User, **user.to_dict())

    redis_conn = repository.redis_db_manager.get_connection()
    redis_get_all_key = "get_all:user"
    redis_get_by_custom_fields_key = "get_by_custom_fields:user"
    redis_get_by_id_key_1 = "get_by_id:user:item_id:1"
    redis_get_by_id_key_2 = "get_by_id:user:item_id:2"
    redis_conn.set(redis_get_all_key, json.dumps([1, 2, 3]))
    redis_conn.set(redis_get_by_custom_fields_key, json.dumps([1, 2, 3]))
    redis_conn.set(redis_get_by_id_key_1, json.dumps([1, 2, 3]))
    redis_conn.set(redis_get_by_id_key_2, json.dumps([1, 2, 3]))

    repository.delete(User, user.username)

    assert len(redis_conn.keys(redis_get_all_key)) == 0
    assert len(redis_conn.keys(f"{redis_get_by_custom_fields_key}*")) == 0
    assert len(redis_conn.keys(f"{redis_get_by_id_key_1}*")) == 0
    assert len(redis_conn.keys(f"{redis_get_by_id_key_2}*")) == 1
