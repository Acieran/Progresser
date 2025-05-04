import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.models_sql_alchemy.models import Base


class SQLDatabaseManager:
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

class RedisDatabaseManager:
    def __init__(self,
                 host : str ='localhost',
                 port: int = 6379,
                 db: int = 0,
                 username: str = 'default',
                 password: str = 'null',
                 ):
        self._pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            username=username,
            password=password)
        self._username = username
        self._password = password

    def get_connection(self) -> redis.Redis:
        """Get a Redis connection from the pool."""
        return redis.Redis(
            decode_responses=True,
            connection_pool=self._pool,
        )
