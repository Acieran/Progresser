from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, Boolean, Integer, Float
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class Workspace(Base):
    __tablename__ = "workspaces"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    description: Mapped[Optional[str]] = mapped_column(String(1000),nullable=True)
    owner_name: Mapped[str] = mapped_column(ForeignKey("users.username"))
    owner: Mapped["User"] = relationship(back_populates="workspace")
    progress: Mapped[float] = mapped_column(Float)
    task_lists: Mapped[List["TaskList"]] = relationship("TaskList", back_populates="workspace", cascade="all, delete-orphan")
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

class TaskList(Base):
    __tablename__ = "lists"
    id: Mapped[int] = mapped_column(primary_key=True)
    workspace: Mapped["Workspace"] = relationship(back_populates="task_lists")
    workspace_name: Mapped[str] = mapped_column(ForeignKey("workspaces.name"))
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    progress: Mapped[float] = mapped_column(Float)
    weight: Mapped[float] = mapped_column(Float)
    tasks: Mapped[List["Task"]] = relationship(back_populates="list", cascade="all, delete-orphan")
    user: Mapped["User"] = relationship(User)
    def __repr__(self) -> str:
        return (f"TaskList(id={self.id!r}, Workspace_name={self.workspace_name!r}, Name={self.name!r}, "
                f"Description={self.description!r}, Completed={self.completed!r}, Weight={self.weight!r})")

class Task(Base):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)
    list_id: Mapped[int] = mapped_column(ForeignKey("lists.id"))
    list:Mapped["TaskList"] = relationship(back_populates="tasks")
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    weight: Mapped[float] = mapped_column(Float)
    def __repr__(self) -> str:
        return (f"TaskList(id={self.id!r}, List Id={self.list_id!r}, Name={self.name!r}, "
                f"Description={self.description!r}, Completed={self.completed!r}, Weight={self.weight!r})")