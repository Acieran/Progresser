import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import database_manager
from database.database_manager import SQLDatabaseManager
from core.models_sql_alchemy.models import User, Base
from database.repositories.base_repository import BaseRepository

sql_string = "sqlite:///:memory:"

@pytest.fixture
def db_user_setup():
    manager = SQLDatabaseManager(sql_string)
    repository = BaseRepository(manager)
    yield repository
    Base.metadata.drop_all(manager.engine)

def test_create_user_repository_success(db_user_setup):
    db = database_manager.SQLDatabaseManager(sql_string)
    session = db.get_session()
    if session.get()

    rep.create(User, **user.object_to_dict())

    created_user = session.get(User, user.username)
    assert user.object_to_dict() == created_user.object_to_dict()

    session.rollback()
    assert session.get(User, user.username) is None

def test_create_user_repository_failure(db_user_setup):
    rep, session, user = db_user_setup

    with pytest.raises(IntegrityError):
        rep.create(User, **user.object_to_dict())
        rep.create(User, **user.object_to_dict())

def test_transaction_create_base_repository():
    test_create_base_repository(True)

def delete_created_user(session: Session):
    created_user = session.get(User, "Rol")
    session.delete(created_user)
    session.commit()