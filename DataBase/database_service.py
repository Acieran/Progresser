from typing import Type, Any, Dict, Optional, get_type_hints

from sqlalchemy import create_engine, exc, inspect
from sqlalchemy.orm import Session, DeclarativeMeta, DeclarativeBase

from .schemas import Base, User, UserState


class DatabaseService:

    def __init__(self):
        self.engine = create_engine("sqlite:///DataBase/progresser.db", echo=True)
        Base.metadata.create_all(self.engine)

    def create(self, model: Type, data: Dict[str, Any]) -> Any:
        """Creates a new record in the database."""
        try:
            with Session(self.engine) as session:
                instance = model(**data)  # Create an instance of the model
                session.add(instance)
                session.commit()
                session.refresh(instance)  # Get the updated object
                return instance
        except exc.SQLAlchemyError as e:
            raise e


    def get_by_id(self, model: Type, item_id: Any, session: Any | None) -> Optional[Any]:
        """Retrieves a record by its primary key (assuming id)."""
        try:
            if session is None:
                with Session(self.engine) as session:
                    return session.get(model, item_id) # Use session.get() for efficiency
            else:
                return session.get(model, item_id)
        except exc.SQLAlchemyError as e:
            raise e

    def get_by_custom_field(self, model: Type[DeclarativeBase], field_name: str, field_value: Any) -> Optional[Any]:
        """
        Retrieves a record from the database based on a custom field name and value.

        Args:
            model: The SQLAlchemy model class (e.g., User, Workspace). Must be a DeclarativeBase.
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
            with Session(self.engine) as session:
                attribute = getattr(model, field_name)
                result = session.query(model).filter(attribute == field_value).first()
                return result

        except exc.SQLAlchemyError as e:
             print(f"Error during query: {e}")
             raise e


    def update(self, model: Type, item_id: Any, data: Dict[str, Any]) -> Optional[Any]:
        """Updates a record in the database."""
        try:
            with Session(self.engine) as session:
                instance = session.get(model, item_id)
                if instance:
                    for key, value in data.items():
                        if hasattr(instance, key) and key in get_type_hints(model):  # Check for valid fields
                            setattr(instance, key, value)
                    session.commit()
                    session.refresh(instance)
                return instance
        except exc.SQLAlchemyError as e:
            raise e


    def delete(self, model: Type, item_id: Any) -> bool:
        """Deletes a record from the database."""
        try:
            with Session(self.engine) as session:
                instance = self.get_by_id(model, item_id)
                if instance:
                    session.delete(instance)
                    session.commit()
                    return True
                return False
        except exc.SQLAlchemyError as e:
            raise e

    def create_user(self, username: str) -> Any:
        """Creates a new record in the database."""
        try:
            self.create(User, {'username': username, 'telegram_username': username})
            self.create(UserState, {'telegram_username': username})
        except exc.SQLAlchemyError as e:
            raise e

    def get_all(self, model:Type) -> Any:
        """Creates a new record in the database."""
        try:
            with Session(self.engine) as session:
                result = session.query(model).all()
                return result
        except exc.SQLAlchemyError as e:
            raise e