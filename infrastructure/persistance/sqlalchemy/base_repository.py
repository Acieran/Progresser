import json
from functools import wraps
from typing import Any, Callable, Literal, TypeVar, cast, get_type_hints

from sqlalchemy import exc, select
from sqlalchemy import inspect as sqlalchemy_inspect
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from core.application.ports.caching import CachingInterface
from core.application.ports.database import DatabaseInterface
from core.application.ports.repositories import BaseRepositoryInterface
from infrastructure.persistance.sqlalchemy.models import Base

T = TypeVar('T', bound=Base)
F = TypeVar('F', bound=Callable[..., Any])

class BaseRepository(BaseRepositoryInterface, CachingInterface):
    """
    Repository that initialized basic database operations(CRUD)
    and transaction handling.
    """
    def __init__(self, db_manager: DatabaseInterface, redis_db_manager: CachingInterface):
        self.db_manager = db_manager
        self._session: Session | None = None
        self.redis_db_manager = redis_db_manager

    def transaction(self) -> '_TransactionHelper':
        """Use this when you need multi-operation transactions"""
        return self._TransactionHelper(self)

    def get_session(self) -> Session | None:
        """Return the current session"""
        return self._session

    def _ensure_session(self) -> Session:
        if self._session is None:
            raise RuntimeError("Session is not available")
        return self._session

    @staticmethod
    def transaction_decorator(func: F) -> F:
        """
        Decorator of all database methods that allows to run methods
        without explicitly managing transactions
        """
        @wraps(func)
        def wrapper(self: 'BaseRepository', model: type[Base], *args: Any, **kwargs: Any) -> Any:
            if self.get_session() is None:
                with self.transaction():
                    session = self.get_session()
                    assert session is not None
                    return func(self, model, *args, **kwargs)
            else:
                return func(self, model, *args, **kwargs)
        return cast(F, wrapper)

    @staticmethod
    def cache(func: F) -> F:
        """
        decorator for caching on methods that return data
        """
        @wraps(func)
        def wrapper(
                self: 'BaseRepository',
                model: type,
                item_id: str | int | None = None,
                **kwargs: Any) -> Any:
            key = f"{func.__name__}:{model.__name__.lower()}"
            if item_id:
                key += f':item_id:{item_id}'
            for name, value in kwargs.items():
                key += f":{name}:{value}"

            redis_conn = self.redis_db_manager.get_connection()
            if redis_conn.exists(key):
                return json.loads(redis_conn.get(key))

            if item_id:
                result = func(self, model, item_id, **kwargs)
            else:
                result = func(self, model, **kwargs)
            redis_conn.set(key,json.dumps(result))
            return result
        return cast(F, wrapper)

    class _TransactionHelper:
        def __init__(self, repository: 'BaseRepository') -> None:
            self.repository = repository

        def __enter__(self) -> 'BaseRepository':
            # Start a new session if none exists
            if self.repository._session is None:
                self.repository._session = self.repository.db_manager.get_session()
            return self.repository

        def __exit__(self,
                     exc_type: type[BaseException] | None,
                     exc_val: BaseException | None,
                     exc_tb: Any | None) -> None:
            session = self.repository._ensure_session()

            if exc_type is None:
                session.commit()
            else:
                session.rollback()
            session.close()
            self.repository._session = None

    def _invalidate_cache(
            self,
            model: str,
            *cache_names: str,
            item_id: str | int | None = None
    ) -> None:
        for name in cache_names:
            func = getattr(self, f"_{name}_cache_invalidation")
            func(model, item_id) if name == "get_by_id" else func(model)

    @transaction_decorator
    def create(self, model: type[Base], **kwargs: Any) -> Literal[True]:
        """Creates a new record in the database."""
        try:
            instance = model(**kwargs)
            self._ensure_session().add(instance)
            self._invalidate_cache(model.__name__.lower(), "get_all", "get_by_custom_fields")
            return True
        except exc.SQLAlchemyError as e:
            raise e

    def _get_by_id_cache_invalidation(self, model: str, item_id: str | int) -> None:
        redis_conn = self.redis_db_manager.get_connection()
        redis_conn.delete(f"get_by_id:{model}:item_id:{item_id}")

    @cache
    @transaction_decorator
    def get_by_id(self, model: type[T], item_id: str | int) -> dict[str,Any] | None:
        """Retrieves a record by its primary key (assuming id)."""
        try:
            result = self._ensure_session().get(model, item_id)
            if not result:
                return None
            return result.to_dict()
        except exc.SQLAlchemyError as e:
            raise e

    @cache
    @transaction_decorator
    def get_by_custom_field(self,
                            model: type[T],
                            field_name: str,
                            field_value: Any) -> dict[str, Any] | None:
        """
        Retrieves a record from the database based on a custom field name and value.

        Args:
            model: The name of model to find record in.
            field_name: The name of the field to filter on (as a string).
            field_value: The value to filter the field by.

        Returns:
            The first matching record, or None if no matching record is found.

        Raises:
            ValueError: If the field_name is not a valid attribute of the model.
            TypeError: If model is not a valid SQLAlchemy model.
        """
        if not isinstance(model, type) or not issubclass(model, Base):
            raise TypeError("model must be a SQLAlchemy model class (DeclarativeBase)")

        inspector = sqlalchemy_inspect(model)
        attribute_names = [c.key for c in inspector.columns]

        if field_name not in attribute_names:
            raise ValueError(f"Invalid field_name:{field_name}. Valid fields are:{attribute_names}")

        try:
            result = (self._ensure_session().query(model).
                      where(inspector.columns[field_name] == field_value).
                      first())
            if result and isinstance(result,Base):
                return result.to_dict()
            return None

        except exc.SQLAlchemyError as e:
            raise e

    def _get_by_custom_fields_cache_invalidation(self, model: str) -> None:
        redis_conn = self.redis_db_manager.get_connection()
        keys_to_del_bin = redis_conn.keys(f"get_by_custom_fields:{model}*")
        if len(keys_to_del_bin):
            redis_conn.delete(*keys_to_del_bin)

    @cache
    @transaction_decorator
    def get_by_custom_fields(self, model: type[Base], **kwargs: Any) -> list[dict[str, Any]]:
        """
        Retrieves records from the database based on multiple custom fields
        specified as keyword arguments.

        Args:
            model: The SQLAlchemy model class to query.
            **kwargs: Keyword arguments representing name = value to search for.
                       For example: `username="testuser", email="test@example.com"`

        Returns:
            A list of records that match the specified search criteria.
        """
        try:
            inspector = sqlalchemy_inspect(model)

            query = select(model)
            for field, value in kwargs.items():
                column = getattr(model, field, None)  # Get the column object from the model
                if column is None:
                    raise SQLAlchemyError(f"Model '{model.__name__}' has no attribute '{field}'")
                query = query.where(inspector.columns[field] == value)

            # Execute the query and return the results
            result = self._ensure_session().execute(query).scalars().all()
            return [x.to_dict() for x in result]

        except exc.SQLAlchemyError as e:
            raise e

    @transaction_decorator
    def update(self, model:type[Base], item_id: str | int, **data: Any) -> bool:
        """Updates a record in the database."""
        try:
            instance = self._ensure_session().get(model, item_id)
            if instance:
                for key, value in data.items():
                    if hasattr(instance, key) and key in get_type_hints(model):
                        setattr(instance, key, value)
                self._invalidate_cache(
                    model.__name__.lower(),
                    "get_all", "get_by_custom_fields", "get_by_id",
                    item_id=item_id
                )
                return True
            return False
        except exc.SQLAlchemyError as e:
            raise e

    @transaction_decorator
    def delete(self, model: type[Base], item_id: str | int) -> bool:
        """Deletes a record from the database."""
        try:
            session = self._ensure_session()
            instance = session.get(model, item_id)
            if instance:
                session.delete(instance)
                self._invalidate_cache(
                    model.__name__.lower(),
                    "get_all", "get_by_custom_fields", "get_by_id",
                    item_id=item_id
                )
                return True
            return False
        except exc.SQLAlchemyError as e:
            raise e

    def _get_all_cache_invalidation(self, model: str) -> None:
        redis_conn = self.redis_db_manager.get_connection()
        redis_conn.delete(f"get_all:{model}")

    @cache
    @transaction_decorator
    def get_all(self, model: type[Base]) -> list[dict[str, Any]]:
        """Returns all records of the database table"""
        try:
            result = self._ensure_session().query(model).all()
            return [x.to_dict() for x in result if isinstance(x,Base)]
        except exc.SQLAlchemyError as e:
            raise e
