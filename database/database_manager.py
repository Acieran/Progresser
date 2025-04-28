from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.models_sql_alchemy.models import Base


class SQLDatabaseManager:

    def __init__(self,
                 sql_string: str, echo: bool | None = True,
                 autocommit: bool | None = False,
                 autoflush: bool | None = False,
                 expire_on_commit: bool | None = False):
        self.engine = create_engine(sql_string, echo=echo) #"sqlite:///database/progresser.db"
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=self.engine, expire_on_commit=expire_on_commit)

    def get_session(self):
        return self.SessionLocal()

    def get_new_session(self,
                        autocommit: bool | None = False,
                        autoflush: bool | None = False,
                        expire_on_commit: bool | None = False):
        return sessionmaker(autocommit=autocommit, autoflush=autoflush, bind=self.engine, expire_on_commit=expire_on_commit)

    def reset_database(self):
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)

    def session_context(self) -> Session:
        """Context manager for automatic session handling"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

