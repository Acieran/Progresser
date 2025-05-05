from typing import Any, List, Optional, Union

from sqlalchemy import Boolean, Float, ForeignKey, String, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary, optionally excluding relationships."""
        mapper = inspect(self.__class__)
        result = {}

        for column in mapper.columns:
            result[column.name] = getattr(self, column.name)
        return result

class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(1000),nullable=True)
    owner_name: Mapped[str] = mapped_column(ForeignKey("users.username"))
    owner: Mapped["User"] = relationship(back_populates="workspace")
    child_tasks: Mapped[List["Task"]] = relationship("Task", back_populates="workspace", cascade="all, delete-orphan")
    def __repr__(self) -> str:
        return f"Item(Name={self.name!r}, Owner={self.owner_name!r}, Description={self.description!r})"

class User(Base):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(primary_key=True)
    # password: Mapped[str] = mapped_column(String())
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    telegram_username: Mapped[str] = mapped_column(String, nullable=True)
    workspace: Mapped[List["Workspace"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan", lazy="select"
    )
    user_state: Mapped[List["UserState"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    def __repr__(self) -> str:
        return f"Username(id={self.username!r}, Active={self.active!r}, Chat_id={self.telegram_username!r})"

class UserState(Base):
    __tablename__ = "user_state"
    telegram_username: Mapped[str] = mapped_column(ForeignKey("users.telegram_username"), primary_key=True)
    state: Mapped[Optional[str]] = mapped_column(String(50), default=None, nullable=True)
    user: Mapped["User"] = relationship(User, back_populates="user_state")
    def __repr__(self) -> str:
        return f"UserState(id={self.telegram_username!r}, State={self.state!r})"

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)

    workspace_id: Mapped[int] = mapped_column(ForeignKey("workspaces.id"))
    workspace: Mapped["Workspace"] = relationship(back_populates="child_tasks")

    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    parent_task: Mapped[Optional["Task"]] = relationship(
        "Task", back_populates="child_tasks", remote_side=id
    )

    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    weight: Mapped[float] = mapped_column(Float, default=1)
    owner_name: Mapped[str] = mapped_column(ForeignKey("users.username"))

    child_tasks: Mapped[List["Task"]] = relationship(back_populates="parent_task", cascade="all, delete-orphan")

class Summary:
    all_cls = Union[Workspace, UserState, Task, User]