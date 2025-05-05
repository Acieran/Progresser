from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.application.ports.database import DatabaseInterface
from infrastructure.persistance.sqlalchemy.models import Base


class SQLDatabaseManager(DatabaseInterface):
    def __init__(self,
                 sql_string: str, echo: bool = True,
                 autocommit: bool = False,
                 autoflush: bool = False,
                 expire_on_commit: bool = False):
        self.engine = create_engine(sql_string, echo=echo) #"sqlite:///database/progresser.db"
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=autocommit,
                                         autoflush=autoflush,
                                         bind=self.engine,
                                         expire_on_commit=expire_on_commit)

    def get_session(self) -> Session:
        return self.SessionLocal()

    def reset_database(self) -> None:
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)