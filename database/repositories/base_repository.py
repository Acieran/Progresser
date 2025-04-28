from typing import get_type_hints, TypeVar

from sqlalchemy import exc, inspect, select
from sqlalchemy.orm import Session, DeclarativeBase

from database.database_manager import SQLDatabaseManager

T = TypeVar('T', bound=DeclarativeBase)

class BaseRepository:
    def __init__(self, db_manager: SQLDatabaseManager):
        self.db_manager = db_manager
        self._session: Session | None = None

    def transaction(self):
        """Use this when you need multi-operation transactions"""
        return self._TransactionHelper(self)

    def get_session(self) -> Session:
        return self._session

    @staticmethod
    def transaction_decorator(func):
        def wrapper(self, model, *args, **kwargs):
            if self._session is None:
                with self.transaction():
                    return func(self, model, *args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper

    class _TransactionHelper:
        def __init__(self, repository):
            self.repository = repository

        def __enter__(self):
            # Start a new session if none exists
            if self.repository._session is None:
                self.repository._session = self.repository.db_manager.get_session()
            return self.repository

        def __exit__(self, exc_type, _, __):
            if exc_type is None:
                self.repository._session.commit()
            else:
                self.repository._session.rollback()
            self.repository._session.close()
            self.repository._session = None

    @transaction_decorator
    def create(self, model: type[DeclarativeBase], **kwargs) -> True:
        """Creates a new record in the database."""
        try:
            instance = model(**kwargs)
            self._session.add(instance)
            return True
        except exc.SQLAlchemyError as e:
            raise e

    @transaction_decorator
    def get_by_id(self, model: type[T], item_id: str | int) -> T | None:
        """Retrieves a record by its primary key (assuming id)."""
        try:
            return self._session.get(model, item_id)
        except exc.SQLAlchemyError as e:
            raise e

    @transaction_decorator
    def get_by_custom_field(self, model: type[DeclarativeBase], field_name: str, field_value) -> type[DeclarativeBase]:
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
        if not isinstance(model, type) or not issubclass(model, DeclarativeBase):
            raise TypeError(f"model must be a SQLAlchemy model class (DeclarativeBase)")

        inspector = inspect(model)
        attribute_names = [c.key for c in inspector.mapper.column_attrs]

        if field_name not in attribute_names:
            raise ValueError(f"Invalid field_name: '{field_name}'.  Valid fields are: {attribute_names}")

        try:
            attribute = getattr(model, field_name)
            result = self._session.query(model).filter(attribute == field_value).first()
            return result

        except exc.SQLAlchemyError as e:
             raise e

    @transaction_decorator
    def get_by_custom_fields(self, model: type[DeclarativeBase], **kwargs) -> list[type[DeclarativeBase]]:
        """
        Retrieves records from the database based on multiple custom fields specified as keyword arguments.

        Args:
            model: The SQLAlchemy model class to query.
            session: The SQLAlchemy session object.
            **kwargs: Keyword arguments representing the custom fields and their values to search for.
                       For example: `username="testuser", email="test@example.com"`

        Returns:
            A list of records that match the specified search criteria.
        """
        try:
            query = select(model)
            for field, value in kwargs.items():
                column = getattr(model, field, None)  # Get the column object from the model
                if column is None:
                    raise ValueError(f"Model '{model.__name__}' has no attribute '{field}'")
                query = query.where(column == value)

            # Execute the query and return the results
            result = self._session.execute(query).scalars().all()
            return list(result)

        except exc.SQLAlchemyError as e:
             raise e

    @transaction_decorator
    def update(self, model:type[DeclarativeBase], item_id, data: dict[str, object]) -> True:
        """Updates a record in the database."""
        try:
            instance = self._session.get(model, item_id)
            if instance:
                for key, value in data.items():
                    if hasattr(instance, key) and key in get_type_hints(model):  # Check for valid fields
                        setattr(instance, key, value)
                self._session.commit()
                self._session.refresh(instance)
            return instance
        except exc.SQLAlchemyError as e:
            raise e

    @transaction_decorator
    def delete(self, model: type[DeclarativeBase], item_id) -> True:
        """Deletes a record from the database."""
        try:
            instance = self.get_by_id(model, item_id)
            if instance:
                self._session.delete(instance)
                self._session.commit()
                return True
            return False
        except exc.SQLAlchemyError as e:
            raise e

    @transaction_decorator
    def get_all(self, model: type[DeclarativeBase]) -> list[type[DeclarativeBase]]:
        try:
            result = self._session.query(model).all()
            return result
        except exc.SQLAlchemyError as e:
            raise e