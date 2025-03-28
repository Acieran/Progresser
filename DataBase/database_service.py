from typing import Type, Any, Dict, Optional, get_type_hints, List, Union

from sqlalchemy import create_engine, exc, inspect, select
from sqlalchemy.orm import Session, DeclarativeMeta, DeclarativeBase, sessionmaker

from .schemas import Base, User, UserState, Summary


class DatabaseService:

    def __init__(self):
        self.engine = create_engine("sqlite:///DataBase/progresser.db", echo=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine, expire_on_commit=False)

    def create_session(self):
        return self.SessionLocal()

    def close_session(self, session: Session):
        session.close()

    def create(self, model: Type, data: Dict[str, Any], session: Optional[Session] = None) -> Any:
        """Creates a new record in the database."""
        own_session = False
        try:
            if session is None:
                session = self.SessionLocal()
                own_session = True

            instance = model(**data)  # Create an instance of the model
            session.add(instance)
            session.commit()
            session.refresh(instance)  # Get the updated object
            return instance
        except exc.SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            if own_session:
                session.close()


    def get_by_id(self, model: Type, item_id: Any, session: Session | None = None) -> Optional[Any]:
        """Retrieves a record by its primary key (assuming id)."""
        own_session = False
        try:
            if session is None:
                session = self.SessionLocal()
                own_session = True

            return session.get(model, item_id)
        except exc.SQLAlchemyError as e:
            raise e
        finally:
            if own_session:
                session.close()

    def get_by_custom_field(self, model: Type[DeclarativeBase], field_name: str, field_value: Any, session: Optional[Session] = None) -> Optional[Any]:
        """
        Retrieves a record from the database based on a custom field name and value.

        Args:
            model: The SQLAlchemy model class (e.g., User, Workspace). Must be a DeclarativeBase.
            field_name: The name of the field to filter on (as a string).
            field_value: The value to filter the field by.
            session: The SQLAlchemy session object.

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

        own_session = False
        try:
            if session is None:
                session = self.SessionLocal()
                own_session = True

            attribute = getattr(model, field_name)
            result = session.query(model).filter(attribute == field_value).first()
            return result

        except exc.SQLAlchemyError as e:
             raise e
        finally:
            if own_session:
                session.close()

    def get_by_custom_fields(self, model: Type[Base], *, session: Optional[Session] = None, **kwargs) -> List[Summary.all_cls]:
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
        own_session = False
        try:
            if session is None:
                session = self.SessionLocal()
                own_session = True

            query = select(model)
            for field, value in kwargs.items():
                column = getattr(model, field, None)  # Get the column object from the model
                if column is None:
                    raise ValueError(f"Model '{model.__name__}' has no attribute '{field}'")
                query = query.where(column == value)

            # Execute the query and return the results
            result = session.execute(query).scalars().all()
            return list(result)

        except exc.SQLAlchemyError as e:
             raise e
        finally:
            if own_session:
                session.close()


    def update(self, model: Type, item_id: Any, data: Dict[str, Any], session: Optional[Session] = None) -> Optional[Any]:
        """Updates a record in the database."""
        own_session = False
        try:
            if session is None:
                session = self.SessionLocal()
                own_session = True

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
        finally:
            if own_session:
                session.close()


    def delete(self, model: Type, item_id: Any, session: Optional[Session] = None) -> bool:
        """Deletes a record from the database."""
        own_session = False
        try:
            if session is None:
                session = self.SessionLocal()  # type: ignore
                own_session = True

            instance = self.get_by_id(model, item_id)
            if instance:
                session.delete(instance)
                session.commit()
                return True
            return False
        except exc.SQLAlchemyError as e:
            raise e
        finally:
            if own_session:
                session.close()

    def create_user(self, username: str) -> Any:
        """Creates a new record in the database."""
        try:
            self.create(User, {'username': username, 'telegram_username': username})
            self.create(UserState, {'telegram_username': username})
        except exc.SQLAlchemyError as e:
            raise e

    def get_all(self, model:Type, session: Optional[Session] = None) -> Any:
        own_session = False
        try:
            if session is None:
                session = self.SessionLocal()  # type: ignore
                own_session = True

            result = session.query(model).all()
            return result
        except exc.SQLAlchemyError as e:
            raise e
        finally:
            if own_session:
                session.close()

    def get_user_state(self, telegram_username: str, session: Optional[Session] = None) -> Any:
        own_session = False
        try:
            if session is None:
                session = self.SessionLocal()  # type: ignore
                own_session = True

            if result := self.get_by_id(UserState, telegram_username, session):
                return result.state
            else:
                self.create(UserState, {'telegram_username': telegram_username})
                return None
        except exc.SQLAlchemyError as e:
            raise e
        finally:
            if own_session:
                session.close()