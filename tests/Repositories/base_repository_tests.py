import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database import database_manager
from database.repositories import base_repository
from core.models_sql_alchemy.models import User

sql_string = "sqlite:///test.db"


def test_create_base_repository(transactional_session: bool = False):
    db = database_manager.SQLDatabaseManager(sql_string)
    session = db.get_session()
    rep = base_repository.BaseRepository(db)
    user = User(username="Rol", active=True, telegram_username="Rol")
    try:
        if transactional_session:
            rep.transaction()
        rep.create(User, **user.object_to_dict())

        created_user = session.get(User, "Rol")
        assert user.object_to_dict() == created_user.object_to_dict()
    except IntegrityError as e:
        delete_created_user(session)
        test_create_base_repository()
    else:
        delete_created_user(session)
    finally:
        session.close()

def test_transaction_create_base_repository():
    test_create_base_repository(True)

def delete_created_user(session: Session):
    created_user = session.get(User, "Rol")
    session.delete(created_user)
    session.commit()