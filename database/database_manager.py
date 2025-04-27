from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.models_sql_alchemy.models import Base


class SQLDatabaseManager:

    def __init__(self, sql_string: str):
        self.engine = create_engine(sql_string, echo=True) #"sqlite:///database/progresser.db"
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False)

    def get_session(self):
        return self.SessionLocal()

    def get_new_session(self):
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False)

    def session_context(self) -> Session:
        """Context manager for automatic session handling"""
        session = self.SessionLocal()
        try:
            yield session
        finally:
            session.close()

